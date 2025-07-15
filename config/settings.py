"""
Configuration settings for Relicon AI Video Generation Platform
Centralizes all environment variables and configuration constants
"""
import os
from typing import Optional
from pathlib import Path

class Settings:
    """Application settings and configuration"""
    
    # Application
    APP_NAME = "Relicon AI Video Generation Platform"
    APP_VERSION = "2.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    LUMA_API_KEY = os.getenv("LUMA_API_KEY")
    
    # External APIs
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
    SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")
    
    # Video Generation
    DEFAULT_VIDEO_DURATION = 30
    MAX_VIDEO_DURATION = 60
    VIDEO_QUALITY = "1080p"
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    TEMP_DIR = BASE_DIR / "temp"
    OUTPUT_DIR = BASE_DIR / "outputs"
    
    # Ensure directories exist
    ASSETS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_required_keys(cls) -> bool:
        """Validate that all required API keys are present"""
        required_keys = [
            cls.OPENAI_API_KEY,
            cls.DATABASE_URL
        ]
        return all(key is not None for key in required_keys)
    
    @classmethod
    def get_luma_headers(cls) -> dict:
        """Get headers for Luma AI API"""
        return {
            "Authorization": f"Bearer {cls.LUMA_API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_openai_client_config(cls) -> dict:
        """Get OpenAI client configuration"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "timeout": 60.0
        }

# Global settings instance
settings = Settings()