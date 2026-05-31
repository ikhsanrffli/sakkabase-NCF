from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DB_HOST:     str = "localhost"
    DB_PORT:     int = 3306
    DB_USER:     str = "root"
    DB_PASSWORD: str = ""
    DB_NAME:     str = "sakkabase_ncf"

    # JWT
    JWT_SECRET:         str = "changethis"
    JWT_ALGORITHM:      str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 jam

    # NCF model
    MODEL_PATH: str = "../models/ncf_config_B.pth"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
