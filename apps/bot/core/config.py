from typing import Union

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    TELEGRAM_BOT_TOKEN: str
    ADMIN_SERVICE_URL: str = "http://localhost:8000"
    ADMIN_API_TOKEN: str = ""
    ADMIN_TOKEN_FILE: str = ""
    ALLOWED_USER_IDS: Union[str, list[int]] = Field(default_factory=list)
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "bot_user"
    POSTGRES_PASSWORD: str = "bot_password"
    POSTGRES_DB: str = "bot_db"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if isinstance(self.ALLOWED_USER_IDS, str):
            self.ALLOWED_USER_IDS = [
                int(uid.strip()) for uid in self.ALLOWED_USER_IDS.split(",") if uid.strip()
            ]
        elif not isinstance(self.ALLOWED_USER_IDS, list):
            self.ALLOWED_USER_IDS = []

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

