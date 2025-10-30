from shared.env.utils import getenv, getenv_bool, getenv_int, validate_required_env_vars, print_env_info


class Settings:
    def __init__(self) -> None:
        required_vars = [
            "HOST",
            "PORT",
            "MINIO_ENDPOINT",
            "MINIO_ACCESS_KEY",
            "MINIO_SECRET_KEY",
            "MINIO_BUCKET",
        ]

        validate_required_env_vars(required_vars)

        self.HOST: str = getenv("HOST")
        self.PORT: int = getenv_int("PORT")

        self.MINIO_ENDPOINT: str = getenv("MINIO_ENDPOINT")
        self.MINIO_ACCESS_KEY: str = getenv("MINIO_ACCESS_KEY")
        self.MINIO_SECRET_KEY: str = getenv("MINIO_SECRET_KEY")
        self.MINIO_BUCKET: str = getenv("MINIO_BUCKET")
        self.MINIO_SECURE: bool = getenv_bool("MINIO_SECURE", False)
        self.MINIO_REGION: str = getenv("MINIO_REGION", "")
        self.MINIO_EXTERNAL_URL: str = getenv("MINIO_EXTERNAL_URL", "")

        self.PROJECT_NAME: str = "Upload Service"

        self._print_config()

    def _print_config(self) -> None:
        info = {
            "HOST": self.HOST,
            "PORT": str(self.PORT),
            "MINIO_ENDPOINT": self.MINIO_ENDPOINT,
            "MINIO_BUCKET": self.MINIO_BUCKET,
            "MINIO_REGION": self.MINIO_REGION,
            "MINIO_SECURE": str(self.MINIO_SECURE),
            "MINIO_EXTERNAL_URL": self.MINIO_EXTERNAL_URL,
        }
        print_env_info(info)


settings = Settings()
