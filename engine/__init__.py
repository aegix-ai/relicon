"""
  Relicon - Enterprise AI Video Generation Platform
  
  A modular, provider-agnostic video generation system with enterprise-grade
  architecture and seamless provider switching capabilities.
"""

from .core.orchestrator import VideoOrchestrator
from .core.provider_manager import provider_manager
from .config.settings import settings

__version__ = "0.9.0"
__author__ = "Relicon"

# Main entry points
def create_video(brand_info, output_path):
    """Create a complete video from brand information."""
    orchestrator = VideoOrchestrator()
    return orchestrator.create_complete_video(brand_info, output_path)

def create_video_from_prompt(prompt, output_path, duration=30):
    """Create video from a simple text prompt."""
    orchestrator = VideoOrchestrator()
    return orchestrator.create_video_from_simple_prompt(prompt, output_path, duration)

# Provider management
def switch_providers(video=None, audio=None, text=None):
    """Switch AI service providers at runtime."""
    orchestrator = VideoOrchestrator()
    orchestrator.switch_providers(video, audio, text)

def get_system_status():
    """Get current system status and configuration."""
    orchestrator = VideoOrchestrator()
    return orchestrator.get_system_status()

# Export key classes for advanced usage
__all__ = [
    'VideoOrchestrator',
    'provider_manager', 
    'settings',
    'create_video',
    'create_video_from_prompt',
    'switch_providers',
    'get_system_status'
]
