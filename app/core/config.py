from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "YouTube Insights API"
    API_DESCRIPTION: str = "API for extracting insights from YouTube videos"
    API_VERSION: str = "0.1.0"
    PORT: int
    DEBUG: bool = False

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_SITE_URL: Optional[str] = None
    OPENROUTER_SITE_NAME: Optional[str] = "YouTube Insights"

    # Upstash Redis Configuration
    UPSTASH_REDIS_URL: str
    UPSTASH_REDIS_TOKEN: str

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10  # Requests per hour per IP

    # Request Timeout (seconds)
    REQUEST_TIMEOUT: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
