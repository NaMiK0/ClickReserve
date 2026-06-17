FROM python:3.12-slim
WORKDIR /project/backend/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/project
WORKDIR /project

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]