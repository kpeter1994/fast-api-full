from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL : str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    DOMAIN : str

    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_FROM_NAME: str
    MAIL_PORT : int
    MAIL_SERVER : str
    USE_CREDENTIALS : bool = True
    VALIDATE_CERTS : bool = True
    MAIL_SSL_TLS : bool = False
    MAIL_STARTTLS : bool = True
    TEMPLATE_FOLDER : str = "templates"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config =  Settings()