from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from os import path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", strict=False)
    # アプリ基本情報
    APP_NAME: str
    APP_DEBUG: bool

    # ログ設定情報
    LOG_LEVEL: str
    LOG_RETENTION: str
    LOG_PATH: str = path.dirname(path.dirname((path.abspath(__file__)))) + "/logs/fastapi-{time:YYYY-MM-DD}.log"

    # データベース情報
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # JWT設定情報
    JWT_VERIFY_EMAIL_TOKEN_EXP: int
    JWT_ACCESS_TOKEN_EXP: int
    JWT_SECRETS_KEY: str
    JWT_ALGORITHM: str

    # AWS
    AWS_MAIL_SENDER: str
    C_ARCHIVE_UPLOADED_FILES_BUCKET_NAME: str
    P_UPLOADED_FILES_BUCKET_NAME: str

    # フロントエンド情報
    FRONTEND_BASE_URL: str


settings = Settings()
