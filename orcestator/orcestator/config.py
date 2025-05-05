"""
Configuration module for Orcestator.
Handles environment variables and settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for Orcestator."""

    HOST: str = os.getenv("OR_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("OR_PORT", "8000"))

    API_KEY: str = os.getenv("OR_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("OR_DEFAULT_MODEL", "openai/gpt-4o")

    LOG_FILE: str = os.getenv("OR_LOG_FILE", "logs/traffic.log")
    DB_PATH: Optional[str] = os.getenv("OR_DB_PATH", None)
    LOG_LEVEL: str = os.getenv("OR_LOG_LEVEL", "info").upper()

    CONTROLLER_HOST: str = "0.0.0.0"
    CONTROLLER_PORT: int = 21001
    WORKER_PORT: int = 8002

    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not cls.API_KEY:
            print("ERROR: OR_API_KEY environment variable is required")
            return False
        
        return True
