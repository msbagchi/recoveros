import os


def _normalize_db_url(url: str) -> str:
    # Render provides postgresql:// — psycopg needs postgresql+psycopg://
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "RecoverOS")
        self.app_env = os.getenv("APP_ENV", "development")
        raw_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:SQL123@localhost:5432/recoveros",
        )
        self.database_url = _normalize_db_url(raw_url)


settings = Settings()

DATABASE_URL = settings.database_url