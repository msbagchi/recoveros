import os


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "RecoverOS")
        self.app_env = os.getenv("APP_ENV", "development")
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:SQL123@localhost:5432/recoveros",
        )


settings = Settings()

DATABASE_URL = settings.database_url