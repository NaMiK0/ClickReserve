# ClickReserve

Бэкенд системы бронирования мест на мероприятия (концерты, кино, театр и т.п.).
Пользователь регистрируется, просматривает мероприятия и места, бронирует свободное место.
Администратор управляет мероприятиями. Защита от двойного бронирования реализована через
распределённую блокировку в Redis, а просроченные брони автоматически очищаются фоновым воркером.

## Возможности

- **JWT-авторизация**: регистрация, вход, защита эндпоинтов (bcrypt + PyJWT).
- **Ролевой доступ (RBAC)**: создание и удаление мероприятий доступно только админам.
- **Управление мероприятиями и местами**: создание события сразу с сеткой мест `ряды × места`.
- **Бронирование с блокировкой**: атомарный лок места в Redis (`SET NX EX`) на 10 минут — два пользователя не займут одно место.
- **Фоновая очистка**: воркер раз в минуту удаляет просроченные брони в статусе `pending`.
- **Миграции БД**: Alembic (async).

## Технологический стек

| Категория | Технологии |
|-----------|-----------|
| Язык | Python 3.12 |
| Веб-фреймворк | FastAPI |
| ORM / БД | SQLAlchemy 2.0 (async) + PostgreSQL 15 |
| Кэш / блокировки | Redis 7 |
| Миграции | Alembic |
| Валидация | Pydantic v2 / pydantic-settings |
| Авторизация | PyJWT, bcrypt |
| Инфраструктура | Docker, Docker Compose |
| ASGI-сервер | Uvicorn |

## Архитектура

Слоистая структура с разделением ответственности:

```
backend/app/
├── main.py            # точка входа FastAPI, lifespan, подключение роутеров
├── config.py          # настройки из .env (pydantic-settings)
├── database.py        # async-движок и фабрика сессий SQLAlchemy
├── redis_client.py    # клиент Redis
├── models/            # ORM-модели (таблицы): user, event, seat, booking
├── schemas/           # Pydantic-схемы ввода/вывода
├── repositories/      # доступ к данным (запросы к БД)
├── services/          # бизнес-логика (booking, event)
├── routers/           # HTTP-эндпоинты + зависимости (auth, events, booking)
├── core/              # утилиты безопасности (хэш паролей, JWT)
├── tasks/             # фоновый воркер очистки броней
└── alembic/           # миграции БД
```

Поток запроса: `router → service → repository → model`. Роутер не ходит в БД напрямую,
репозиторий ничего не знает про HTTP — это упрощает тестирование и поддержку.

### Модель данных

- **User** — `id, username, email, hashed_password, is_admin`
- **Event** — `id, title, description, date`
- **Seat** — `id, row_number, seat_number, price, id_event` (FK → events, `ON DELETE CASCADE`)
- **Booking** — `id, id_seat, id_user, status, created_at, expires_at`
  - `status`: `pending | confirmed | expired`
  - `expires_at` по умолчанию = `created_at + 10 минут`

Удаление мероприятия каскадно удаляет его места и связанные брони.

## Требования

- [Docker](https://www.docker.com/) и Docker Compose

(Локальный Python нужен только при запуске без контейнеров.)

## Запуск

Все команды выполняются из каталога `backend/app` (там лежат `docker-compose.yml` и `.env`).

### 1. Настроить переменные окружения

```bash
cd backend/app
cp .env.example .env
```
Откройте `.env` и подставьте свои значения (особенно `JWT_SECRET_KEY`).
Сгенерировать секрет можно так:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Поднять контейнеры

```bash
docker compose up -d --build
```
Поднимутся три сервиса: `db` (PostgreSQL), `redis`, `web` (приложение на `:8000`).

### 3. Применить миграции (создать таблицы)

```bash
docker compose exec web sh -c "cd backend/app && alembic upgrade head"
```

### 4. Назначить администратора

Зарегистрируйте пользователя через `POST /auth/register` (в Swagger, см. ниже), затем повысьте его:
```bash
docker exec booking_postgres psql -U postgres -d mydb \
  -c "UPDATE users SET is_admin = true WHERE email = 'admin@example.com';"
```

### 5. Открыть API

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Переменные окружения

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `SQL_HOST` | Хост БД (`db` для Docker, `localhost` локально) | `db` |
| `SQL_PORT` | Порт PostgreSQL | `5432` |
| `SQL_USER` | Пользователь БД | `postgres` |
| `SQL_PASSWORD` | Пароль БД | `mysecretpassword` |
| `SQL_DB_NAME` | Имя базы | `mydb` |
| `REDIS_CONNECT` | URL Redis | `redis://redis:6379` |
| `JWT_SECRET_KEY` | Секрет для подписи токенов | `<длинная случайная строка>` |
| `JWT_ALGORITHM` | Алгоритм подписи | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (мин) | `30` |

## API

### Авторизация
| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| POST | `/auth/register` | публичный | Регистрация (возвращает данные без пароля) |
| POST | `/auth/login` | публичный | Вход, возвращает `{access_token, token_type}` |

### Мероприятия
| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| GET | `/events` | публичный | Список мероприятий |
| POST | `/events` | **админ** | Создать мероприятие + сетку мест |
| DELETE | `/events/{event_id}` | **админ** | Удалить мероприятие (каскадно с местами) |

### Бронирование
| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| POST | `/bookings` | авторизованный | Забронировать место (`id_user` берётся из токена) |
| GET | `/bookings` | публичный | Все брони |
| GET | `/bookings/events/{id_event}` | публичный | Брони по мероприятию |
| GET | `/bookings/events/{id_event}/seats` | публичный | Места мероприятия со статусами `free/locked/booked` |
| DELETE | `/bookings/events/{id_event}/seats/{id_seat}` | публичный | Снять бронь и Redis-лок |

## Авторизация в Swagger UI

Используется схема **HTTP Bearer**:

1. `POST /auth/login` → скопируйте `access_token` из ответа.
2. Нажмите **Authorize**  вверху страницы.
3. Вставьте **только токен** (без слова `Bearer`) → **Authorize**.

Защищённые ручки помечены замком; без токена они вернут `401`, без прав админа — `403`.

## Типовой сценарий

1. `POST /auth/register` — создать пользователя.
2. `POST /auth/login` — получить токен, авторизоваться (Authorize).
3. (админ) `POST /events` — создать мероприятие с местами, например:
   ```json
   {"title": "Концерт", "description": "Live", "date": "2026-09-01T19:00:00",
    "rows": 5, "cols": 10, "base_price": 1500}
   ```
4. `GET /bookings/events/{id_event}/seats` — посмотреть места и найти `id` свободного (`status: free`).
5. `POST /bookings` с телом `{"id_seat": <id>}` — забронировать.

## Как работает бронирование

При `POST /bookings` сервис ставит в Redis ключ `lock:seat:{id}` командой `SET NX EX 600`
(атомарно, на 10 минут). Если ключ уже существует — место занято, ответ `409`. Если лок взят —
создаётся запись брони в статусе `pending` с `expires_at = now() + 10 минут`.

Фоновый воркер (`tasks/booking.py`) раз в 60 секунд удаляет просроченные `pending`-брони,
освобождая места.

## Миграции (Alembic)

Команды выполняются внутри контейнера `web` из каталога `backend/app`:

```bash
# создать новую миграцию по изменениям в моделях
docker compose exec web sh -c "cd backend/app && alembic revision --autogenerate -m 'описание'"

# применить миграции
docker compose exec web sh -c "cd backend/app && alembic upgrade head"

# откатить на шаг назад
docker compose exec web sh -c "cd backend/app && alembic downgrade -1"
```

## Структура проекта

```
ClickReserve/
├── backend/
│   └── app/
│       ├── docker-compose.yml   # описание сервисов (db, redis, web)
│       ├── Dockerfile           # образ приложения
│       ├── requirements.txt     # зависимости Python
│       ├── alembic.ini          # конфиг Alembic
│       ├── .env.example         # шаблон переменных окружения
│       └── ...                  # код приложения (см. «Архитектура»)
└── README.md
```
