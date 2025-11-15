from typing import Optional
from shared.env import getenv, getenv_int, validate_required_env_vars, print_env_info


class Settings:
    def __init__(self):
        required_vars = [
            "HOST",
            "PORT",

            "VERSION",
            "API_V1_STR",

            "CONNECTIONS_SERVICE_HOST",
            "CONNECTIONS_SERVICE_PORT",

            "PROJECTS_SERVICE_HOST",
            "PROJECTS_SERVICE_PORT",

            "MODULES_SERVICE_HOST",
            "MODULES_SERVICE_PORT",
            "MODULES_HTTP_PORT",

            "ADMIN_SERVICE_HOST",
            "ADMIN_SERVICE_PORT",

            "UPLOAD_SERVICE_HOST",
            "UPLOAD_SERVICE_PORT",

            "REDIS_HOST",
            "REDIS_PORT",
            "REDIS_DB",

            "GRPC_TIMEOUT",
            "GRPC_MAX_RETRIES",

            "CACHE_TTL_DEFAULT",
            "CACHE_TTL_CONNECTIONS",

            "LOG_LEVEL",
            "ADMIN_API_TOKEN",
        ]
        
        validate_required_env_vars(required_vars)
        
        self.PROJECT_NAME: str = "API Gateway"
        self.VERSION: str = getenv("VERSION")
        self.API_V1_STR: str = getenv("API_V1_STR")

        self.CONNECTIONS_SERVICE_HOST: str = getenv("CONNECTIONS_SERVICE_HOST")
        self.CONNECTIONS_SERVICE_PORT: int = getenv_int("CONNECTIONS_SERVICE_PORT")

        self.PROJECTS_SERVICE_HOST: str = getenv("PROJECTS_SERVICE_HOST")
        self.PROJECTS_SERVICE_PORT: int = getenv_int("PROJECTS_SERVICE_PORT")

        self.MODULES_SERVICE_HOST: str = getenv("MODULES_SERVICE_HOST")
        self.MODULES_SERVICE_PORT: int = getenv_int("MODULES_SERVICE_PORT")
        self.MODULES_HTTP_PORT: int = getenv_int("MODULES_HTTP_PORT")

        self.UPLOAD_SERVICE_HOST: str = getenv("UPLOAD_SERVICE_HOST")
        self.UPLOAD_SERVICE_PORT: int = getenv_int("UPLOAD_SERVICE_PORT")

        self.ADMIN_SERVICE_HOST: str = getenv("ADMIN_SERVICE_HOST")
        self.ADMIN_SERVICE_PORT: int = getenv_int("ADMIN_SERVICE_PORT")
        self.ADMIN_HTTP_PORT: int = getenv_int("ADMIN_HTTP_PORT", 8004)
        self.ADMIN_SERVICE_BASE_URL: str = f"http://{self.ADMIN_SERVICE_HOST}:{self.ADMIN_HTTP_PORT}"

        self.GRPC_TIMEOUT: int = getenv_int("GRPC_TIMEOUT")
        self.GRPC_MAX_RETRIES: int = getenv_int("GRPC_MAX_RETRIES")

        self.REDIS_HOST: str = getenv("REDIS_HOST")
        self.REDIS_PORT: int = getenv_int("REDIS_PORT")
        self.REDIS_DB: int = getenv_int("REDIS_DB")
        self.REDIS_PASSWORD: Optional[str] = getenv("REDIS_PASSWORD") if getenv("REDIS_PASSWORD") else ""
        self.REDIS_URL: str = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

        self.CACHE_TTL_DEFAULT: int = getenv_int("CACHE_TTL_DEFAULT")
        self.CACHE_TTL_CONNECTIONS: int = getenv_int("CACHE_TTL_CONNECTIONS")
        self.CACHE_TTL_MODULES: int = getenv_int("CACHE_TTL_MODULES", 600)
        self.CACHE_TTL_ADMIN: int = getenv_int("CACHE_TTL_ADMIN", 60)

        self.HOST: str = getenv("HOST")
        self.PORT: int = getenv_int("PORT")
        
        self.LOG_LEVEL: str = getenv("LOG_LEVEL")
        self.ADMIN_API_TOKEN: str = getenv("ADMIN_API_TOKEN")
        
        self._print_config_info()
    
    def _print_config_info(self):
        env_vars = {
            "HOST": self.HOST,
            "PORT": str(self.PORT),

            "CONNECTIONS_SERVICE_HOST": self.CONNECTIONS_SERVICE_HOST,
            "CONNECTIONS_SERVICE_PORT": str(self.CONNECTIONS_SERVICE_PORT),

            "PROJECTS_SERVICE_HOST": self.PROJECTS_SERVICE_HOST,
            "PROJECTS_SERVICE_PORT": str(self.PROJECTS_SERVICE_PORT),

            "MODULES_SERVICE_HOST": self.MODULES_SERVICE_HOST,
            "MODULES_SERVICE_PORT": str(self.MODULES_SERVICE_PORT),
            "MODULES_HTTP_PORT": str(self.MODULES_HTTP_PORT),

            "UPLOAD_SERVICE_HOST": self.UPLOAD_SERVICE_HOST,
            "UPLOAD_SERVICE_PORT": str(self.UPLOAD_SERVICE_PORT),

            "ADMIN_SERVICE_HOST": self.ADMIN_SERVICE_HOST,
            "ADMIN_SERVICE_PORT": str(self.ADMIN_SERVICE_PORT),
            "ADMIN_HTTP_PORT": str(self.ADMIN_HTTP_PORT),

            "REDIS_HOST": self.REDIS_HOST,
            "REDIS_PORT": str(self.REDIS_PORT),
            "REDIS_DB": str(self.REDIS_DB),
            "REDIS_PASSWORD": "***" if self.REDIS_PASSWORD else None,

            "GRPC_TIMEOUT": str(self.GRPC_TIMEOUT),

            "CACHE_TTL_DEFAULT": str(self.CACHE_TTL_DEFAULT),
            "CACHE_TTL_CONNECTIONS": str(self.CACHE_TTL_CONNECTIONS),

            "LOG_LEVEL": self.LOG_LEVEL,
            "ADMIN_API_TOKEN": self.ADMIN_API_TOKEN,
        }
        print_env_info(env_vars)


settings = Settings()
