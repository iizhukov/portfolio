from shared.env.utils import (
    getenv,
    getenv_int,
    validate_required_env_vars,
    print_env_info,
)


class Settings:
    def __init__(self) -> None:
        required_vars = [
            "HOST",
            "PORT",
            "REDPANDA_BROKERS",
            "UPLOAD_SERVICE_URL",
            "MODULES_GRPC_HOST",
            "MODULES_GRPC_PORT",
            "MONGODB_URI",
            "MONGODB_DATABASE",
            "ADMIN_RESPONSE_TOPIC",
            "GRPC_PORT",
        ]

        validate_required_env_vars(required_vars)

        self.HOST: str = getenv("HOST")
        self.PORT: int = getenv_int("PORT")
        self.GRPC_PORT: int = getenv_int("GRPC_PORT")

        self.REDPANDA_BROKERS: str = getenv("REDPANDA_BROKERS")
        self.UPLOAD_SERVICE_URL: str = getenv("UPLOAD_SERVICE_URL")

        self.MODULES_GRPC_HOST: str = getenv("MODULES_GRPC_HOST")
        self.MODULES_GRPC_PORT: int = getenv_int("MODULES_GRPC_PORT")

        self.MONGODB_URI: str = getenv("MONGODB_URI")
        self.MONGODB_DATABASE: str = getenv("MONGODB_DATABASE")

        self.ADMIN_RESPONSE_TOPIC: str = getenv("ADMIN_RESPONSE_TOPIC")

        self.REQUEST_TIMEOUT: int = getenv_int("REQUEST_TIMEOUT", 30)

        self.PROJECT_NAME: str = "Admin Service"
        self.LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")

        self._print_config()

    def _print_config(self) -> None:
        info = {
            "HOST": self.HOST,
            "PORT": str(self.PORT),
            "REDPANDA_BROKERS": self.REDPANDA_BROKERS,
            "UPLOAD_SERVICE_URL": self.UPLOAD_SERVICE_URL,
            "MODULES_GRPC_HOST": self.MODULES_GRPC_HOST,
            "MODULES_GRPC_PORT": str(self.MODULES_GRPC_PORT),
            "GRPC_PORT": str(self.GRPC_PORT),
            "MONGODB_DATABASE": self.MONGODB_DATABASE,
            "ADMIN_RESPONSE_TOPIC": self.ADMIN_RESPONSE_TOPIC,
            "REQUEST_TIMEOUT": str(self.REQUEST_TIMEOUT),
        }
        print_env_info(info)


settings = Settings()

