from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://proedge:proedge@localhost:5432/proedge"
    demo_mode: bool = True
    cookie_secure: bool = False
    session_hours: int = 24
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    mail_from: str = "noreply@proedge.local"
    web_origin: str = "http://localhost:3000"
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
