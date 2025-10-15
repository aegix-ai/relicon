"""
  Abstract base class for text generation providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class TextGenerator(ABC):
    """Abstract interface for text generation services."""
    
    @abstractmethod
    def architect_complete_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create complete video architecture from brand information.
        
        Args:
            brand_info: Dictionary containing brand information
            
        Returns:
            Complete video architecture dictionary
        """
        pass
    
    @abstractmethod
    def create_cutting_edge_prompts(self, architecture: Dict[str, Any], 
                                  service_type: str = "luma") -> List[Dict[str, Any]]:
        """
        Generate service-specific prompts for each scene.
        
        Args:
            architecture: Video architecture dictionary
            service_type: Target service type for prompts
            
        Returns:
            List of enhanced scene dictionaries with prompts
        """
        pass
    
    def optimize_scene_prompts(self, scenes: List[Dict[str, Any]], service_type: str = "hailuo") -> List[Dict[str, Any]]:
        """
        Optimize scene prompts for specific video generation services.
        Default implementation - providers can override for service-specific optimization.
        
        Args:
            scenes: List of scene dictionaries
            service_type: Target service for optimization
            
        Returns:
            Optimized scenes with service-specific prompts
        """
        return scenes
