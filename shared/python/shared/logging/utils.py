import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        log_level = level or "INFO"
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return logger


def setup_service_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    logger = get_logger(service_name, log_level)
    logger.info(f"{service_name} started with log level: {log_level}")

    return logger
