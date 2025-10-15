"""
  Abstract base class for audio generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AudioGenerator(ABC):
    """Abstract interface for audio generation services."""
    
    @abstractmethod
    def generate_audio(self, text: str, output_path: str, 
                      audio_config: Dict[str, Any]) -> bool:
        """
        Generate audio from text.
        
        Args:
            text: Text content to convert to speech
            output_path: Local path to save the audio
            audio_config: Configuration for voice characteristics
            
        Returns:
            True if generation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def enhance_audio(self, input_file: str, output_file: str, 
                     audio_config: Dict[str, Any]) -> None:
        """
        Enhance audio quality based on configuration.
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output enhanced audio file
            audio_config: Configuration for enhancement parameters
        """
        pass
    
    @abstractmethod
    def create_unified_audio(self, audio_segments: List[Dict[str, Any]], 
                           target_duration: float, output_path: str) -> bool:
        """
        Create unified audio track from multiple segments.
        
        Args:
            audio_segments: List of audio segment dictionaries
            target_duration: Target total duration in seconds
            output_path: Path to save the unified audio
            
        Returns:
            True if creation successful, False otherwise
        """
        pass
