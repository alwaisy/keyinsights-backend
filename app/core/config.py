from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "YouTube Insights API"
    API_DESCRIPTION: str = "API for extracting insights from YouTube videos"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_SITE_URL: Optional[str] = None
    OPENROUTER_SITE_NAME: Optional[str] = "YouTube Insights"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()