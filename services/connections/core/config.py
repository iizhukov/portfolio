from shared.env.utils import getenv, getenv_int, validate_required_env_vars, print_env_info


class Settings:
    def __init__(self):
        required_vars = [
            "HOST",
            "PORT",

            "VERSION",
            "API_V1_STR",

            "POSTGRES_SERVER",
            "POSTGRES_PORT",
            "POSTGRES_USER", 
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",

            "MESSAGE_BROKERS",
            "ADMIN_CONNECTIONS_TOPIC",

            "MODULES_SERVICE_URL",
            "GRPC_PORT",
        ]
        
        validate_required_env_vars(required_vars)
        
        self.PROJECT_NAME: str = "Connections Service"
        self.VERSION: str = getenv("VERSION")
        self.API_V1_STR = getenv("API_V1_STR")

        self.POSTGRES_SERVER: str = getenv("POSTGRES_SERVER")
        self.POSTGRES_PORT: str = getenv("POSTGRES_PORT")
        self.POSTGRES_USER: str = getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD")
        self.POSTGRES_DB: str = getenv("POSTGRES_DB")
        self.DATABASE_URL: str = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        self.MESSAGE_BROKERS: str = getenv("MESSAGE_BROKERS")
        self.ADMIN_CONNECTIONS_TOPIC: str = getenv("ADMIN_CONNECTIONS_TOPIC")
        
        self.MODULES_SERVICE_URL: str = getenv("MODULES_SERVICE_URL")
        self.MODULES_HEARTBEAT_INTERVAL: int = getenv_int("MODULES_HEARTBEAT_INTERVAL", 0)
        
        self.GRPC_PORT: int = getenv_int("GRPC_PORT")
        
        self.HOST: str = getenv("HOST")
        self.PORT: int = getenv_int("PORT")
        
        self._print_config_info()
    
    def _print_config_info(self):
        env_vars = {
            "HOST": self.HOST,
            "PORT": str(self.PORT),

            "POSTGRES_SERVER": self.POSTGRES_SERVER,
            "POSTGRES_PORT": self.POSTGRES_PORT,
            "POSTGRES_USER": self.POSTGRES_USER,
            "POSTGRES_PASSWORD": "***" if self.POSTGRES_PASSWORD else None,
            "POSTGRES_DB": self.POSTGRES_DB,

            "MESSAGE_BROKERS": self.MESSAGE_BROKERS,
            "ADMIN_CONNECTIONS_TOPIC": self.ADMIN_CONNECTIONS_TOPIC,

            "MODULES_SERVICE_URL": self.MODULES_SERVICE_URL,
            "MODULES_HEARTBEAT_INTERVAL": str(self.MODULES_HEARTBEAT_INTERVAL),
            "GRPC_PORT": str(self.GRPC_PORT)
        }
        print_env_info(env_vars)


settings = Settings()
