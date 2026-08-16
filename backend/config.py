import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    APP_NAME: str = "Bông Sao Rental Sniffer"
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))  # Default: Every 60 seconds (1 min)
    MAX_LISTING_AGE_HOURS: int = int(os.getenv("MAX_LISTING_AGE_HOURS", "48"))  # Drop listings older than 48h (2 days)
    DATABASE_PATH: str = "rental_sniffer.db"
    
    # Push Notifications
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID", "")
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL", "")

    # Facebook Scraping Configuration
    FB_COOKIE_C_USER: Optional[str] = os.getenv("FB_COOKIE_C_USER", "")
    FB_COOKIE_XS: Optional[str] = os.getenv("FB_COOKIE_XS", "")

    # Proxy Configuration (Optional)
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL", "")

    # Search Rules & Criteria
    TARGET_LOCATION: str = "Chung cư Bông Sao, Phường 5, Quận 8, TP.HCM"
    REQUIRED_BEDROOMS: int = 2
    REQUIRED_BATHROOMS: int = 2
    BLOCK_ALIASES: List[str] = ["Block B1", "Lô B1", "Lô B", "Block B", "B1"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
