import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.RESET)
        emoji = self.EMOJIS.get(levelname, '📝')
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        message = record.getMessage()
        
        logger_name = record.name
        if '.' in logger_name:
            logger_name = logger_name.split('.')[-1]
        
        formatted = (
            f"{self.DIM}{timestamp}{self.RESET} "
            f"{emoji} "
            f"{color}{self.BOLD}{levelname:8}{self.RESET} "
            f"{self.DIM}[{logger_name}]{self.RESET} "
            f"{message}"
        )
        
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
        
        return formatted


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        formatter = ColoredFormatter()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        log_level = level or "INFO"
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return logger


def setup_service_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    logger = get_logger(service_name, log_level)
    logger.info(f"🚀 {service_name} started with log level: {log_level}")
    
    return logger


def disable_library_loggers():
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("confluent_kafka").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
