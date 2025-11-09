# type: ignore

"""
Relicon - AI Video Generation Engine

Simple pipeline: Brand Info → Planning → Video Generation → Audio → Assembly → Final Video
"""

from .core.pipeline import VideoGenerationPipeline, pipeline
from .core.provider_manager import provider_manager
from .config.settings import settings

__version__ = "1.0.0"
__author__ = "Relicon"

# Main entry point
def generate_video_ad(brand_info: dict) -> str:
    """
    Generate a complete video ad from brand information.

    Args:
        brand_info: Dict with brand_name, brand_description, product_name, etc.

    Returns:
        Path to generated video file
    """
    return pipeline.generate(brand_info)

# Export for advanced usage
__all__ = [
    'VideoGenerationPipeline',
    'pipeline',
    'generate_video_ad',
    'provider_manager',
    'settings',
]