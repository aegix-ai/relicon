"""
  Abstract base class for video generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class VideoGenerator(ABC):
    """Abstract interface for video generation services."""
    
    @abstractmethod
    def generate_video(self, prompt: str, aspect_ratio: str = "9:16", 
                      image_url: Optional[str] = None, **kwargs) -> str:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description for video content
            aspect_ratio: Video aspect ratio (default: "9:16")
            image_url: Optional first frame image URL
            **kwargs: Provider-specific parameters
            
        Returns:
            Video URL or file path
        """
        pass
    
    @abstractmethod
    def download_video(self, video_url: str, output_path: str, 
                      max_retries: int = 3) -> bool:
        """
        Download video from URL to local file.
        
        Args:
            video_url: URL of the generated video
            output_path: Local path to save the video
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if download successful, False otherwise
        """
        pass
    
    @abstractmethod
    def text_to_video(self, prompt: str, aspect_ratio: str = "9:16") -> str:
        """
        Generate video from text prompt only.
        
        Args:
            prompt: Text description for video content
            aspect_ratio: Video aspect ratio
            
        Returns:
            Video URL or file path
        """
        pass
    
    @abstractmethod
    def image_to_video(self, prompt: str, image_url: str, 
                      aspect_ratio: str = "9:16") -> str:
        """
        Generate video from text prompt and initial image.
        
        Args:
            prompt: Text description for video content
            image_url: URL of the initial image frame
            aspect_ratio: Video aspect ratio
            
        Returns:
            Video URL or file path
        """
        pass
