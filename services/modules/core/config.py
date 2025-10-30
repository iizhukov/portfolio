from shared.env.utils import getenv, getenv_int, validate_required_env_vars, print_env_info


class Settings:
    def __init__(self) -> None:
        required_vars = [
            "HOST",
            "GRPC_PORT",

            "POSTGRES_SERVER",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
        ]

        validate_required_env_vars(required_vars)

        self.HOST: str = getenv("HOST")
        self.GRPC_PORT: int = getenv_int("GRPC_PORT")

        self.POSTGRES_SERVER: str = getenv("POSTGRES_SERVER")
        self.POSTGRES_PORT: str = getenv("POSTGRES_PORT")
        self.POSTGRES_USER: str = getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD")
        self.POSTGRES_DB: str = getenv("POSTGRES_DB")

        self.DATABASE_URL: str = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

        self.DEFAULT_TTL_SECONDS: int = getenv_int("MODULES_DEFAULT_TTL", 30)

        self.PROJECT_NAME: str = "Modules Service"

        self._print_debug_info()

    def _print_debug_info(self) -> None:
        env_snapshot = {
            "HOST": self.HOST,
            "GRPC_PORT": str(self.GRPC_PORT),
            "POSTGRES_SERVER": self.POSTGRES_SERVER,
            "POSTGRES_PORT": self.POSTGRES_PORT,
            "POSTGRES_DB": self.POSTGRES_DB,
            "MODULES_DEFAULT_TTL": str(self.DEFAULT_TTL_SECONDS),
        }
        print_env_info(env_snapshot)


settings = Settings()

