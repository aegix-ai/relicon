"""
  Configuration Settings
  Centralized configuration management
"""

import os
from typing import Optional


class Settings:
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    LUMA_API_KEY: str = os.environ.get("LUMA_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.environ.get("ELEVENLABS_API_KEY", "")
    HAILUO_API_KEY: str = os.environ.get("HAILUO_API_KEY", "")
    
    # Provider Configuration
    VIDEO_PROVIDER: str = os.environ.get("VIDEO_PROVIDER", "luma")  # luma (Ray 3 primary), hailuo (fallback)
    AUDIO_PROVIDER: str = os.environ.get("AUDIO_PROVIDER", "elevenlabs")  # elevenlabs
    TEXT_PROVIDER: str = os.environ.get("TEXT_PROVIDER", "openai")  # openai
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///relicon.db")
    
    # Redis
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))
    
    # Storage
    OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "outputs")
    TEMP_DIR: str = os.environ.get("TEMP_DIR", "/tmp/relicon")
    
    # API Settings
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.environ.get("API_PORT", "8000"))
    
    # Video Generation
    DEFAULT_ASPECT_RATIO: str = "9:16"  # TikTok/Instagram format
    DEFAULT_VIDEO_DURATION: int = 18  # seconds - optimized for short-form content
    MAX_VIDEO_DURATION: int = 20  # seconds - maximum duration for enterprise ads
    DEFAULT_VIDEO_RESOLUTION: str = "720p"  # Cost-optimized: 720p = $0.4/5s vs 1080p = $0.9/5s
    DEFAULT_VIDEO_QUALITY: str = "high"
    
    # Cost Limits - Updated for 720p optimization
    ESTIMATED_COST_PER_VIDEO: float = 1.5  # dollars - 3 scenes × $0.4 + audio + OpenAI
    MAX_COST_PER_VIDEO: float = 3.0  # dollars - reduced from 10.0 due to 720p optimization
    COST_WARNING_THRESHOLD: float = 2.0  # dollars - reduced threshold
    
    # Performance
    MAX_CONCURRENT_JOBS: int = int(os.environ.get("MAX_CONCURRENT_JOBS", "3"))
    JOB_TIMEOUT: int = int(os.environ.get("JOB_TIMEOUT", "1800"))  # 30 minutes
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Text provider validation
        if self.TEXT_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required for OpenAI text provider")
        
        # Video provider validation
        if self.VIDEO_PROVIDER == "luma" and not self.LUMA_API_KEY:
            errors.append("LUMA_API_KEY is required for Luma video provider")
        elif self.VIDEO_PROVIDER == "hailuo" and not self.HAILUO_API_KEY:
            errors.append("HAILUO_API_KEY is required for Hailuo video provider")
        
        # Audio provider validation
        if self.AUDIO_PROVIDER == "elevenlabs" and not self.ELEVENLABS_API_KEY:
            errors.append("ELEVENLABS_API_KEY is required for ElevenLabs audio provider")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        
        return errors
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            "output_dir": self.OUTPUT_DIR,
            "temp_dir": self.TEMP_DIR,
            "api_host": self.API_HOST,
            "api_port": self.API_PORT,
            "default_aspect_ratio": self.DEFAULT_ASPECT_RATIO,
            "max_video_duration": self.MAX_VIDEO_DURATION,
            "max_concurrent_jobs": self.MAX_CONCURRENT_JOBS,
            "job_timeout": self.JOB_TIMEOUT,
        }


# Global settings instance
settings = Settings()
