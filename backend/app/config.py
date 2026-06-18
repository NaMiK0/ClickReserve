from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    sql_host: str
    sql_port: int
    sql_user: str
    sql_password: str
    sql_db_name: str
    redis_connect: str

    jwt_secret_key: str = "change-me-in-production-please-use-a-long-random-value"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        database_url_str = f"postgresql+asyncpg://{self.sql_user}:{self.sql_password}@{self.sql_host}:{self.sql_port}/{self.sql_db_name}"
        return database_url_str


settings = Settings()