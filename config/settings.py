"""
Central configuration management for ReelForge
All settings are loaded from environment variables with sensible defaults
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    openai_temperature: float = 0.7
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_result_backend: str = "redis://localhost:6379/1"
    
    # Storage Configuration
    storage_type: str = "local"  # "local" or "s3"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # TTS Configuration
    tts_provider: str = "openai"  # "openai" or "elevenlabs"
    elevenlabs_api_key: Optional[str] = None
    
    # Stock Footage Configuration
    stock_provider: str = "pexels"
    pexels_api_key: str
    
    # FFmpeg Configuration
    ffmpeg_binary_path: str = "/usr/bin/ffmpeg"
    
    # Logging Configuration
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    
    # Job Configuration
    max_job_duration: int = 300  # seconds
    default_video_duration: int = 30  # seconds
    max_video_duration: int = 60  # seconds
    
    # Development Configuration
    debug: bool = False
    
    # Transition and Effect Presets
    available_transitions: list = [
        "fade", "crossfade", "dissolve", "wipe", "slide", "zoom", "rotate"
    ]
    
    # Brand Safety Rules
    max_scene_count: int = 8
    min_scene_duration: float = 2.0  # seconds
    max_scene_duration: float = 8.0  # seconds
    require_logo_end: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Logging configuration
import structlog
import logging

if settings.sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(dsn=settings.sentry_dsn)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = structlog.get_logger()
