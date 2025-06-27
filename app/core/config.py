import logging
import sys
from pathlib import Path
from pydantic import BaseSettings, Field
from typing import Optional, Dict, Any

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
            "level": "DEBUG"
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True
        },
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO"
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

def setup_logging():
    """Configure logging for the application."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging is configured")
    return logger

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Document Analyzer"
    API_V1_STR: str = "/api/v1"
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL: str = "deepseek/deepseek-r1-0528-qwen3-8b:free"
    
    # API Configuration
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            # Configure logging as early as possible
            import logging.config
            logging.config.dictConfig(LOGGING_CONFIG)
            logger = logging.getLogger(__name__)
            logger.debug("Configuring settings...")
            
            return env_settings, init_settings, file_secret_settings

settings = Settings()
