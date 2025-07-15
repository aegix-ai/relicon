"""Script generation module"""
from typing import Dict, Any, List
from config.settings import settings

class ScriptGenerator:
    """Script generation service"""
    
    def generate_energetic_segments(self, brand_info: Dict[str, Any], num_segments: int = 3) -> List[Dict[str, Any]]:
        """Generate energetic script segments"""
        segments = []
        brand_name = brand_info.get("brand_name", "our brand")
        brand_description = brand_info.get("brand_description", "amazing product")
        
        # Generate different types of segments
        segment_types = [
            f"Discover {brand_name} - {brand_description}!",
            f"Experience the power of {brand_name}. Revolutionary results await!",
            f"Join thousands who chose {brand_name}. Transform your life today!"
        ]
        
        duration_per_segment = brand_info.get("duration", 30) // num_segments
        
        for i in range(num_segments):
            segments.append({
                "text": segment_types[i % len(segment_types)],
                "duration": duration_per_segment,
                "energy_level": "high",
                "tone": "enthusiastic"
            })
        
        return segments
    
    def enhance_script_energy(self, script_text: str) -> str:
        """Enhance script with more energy"""
        return f"{script_text} Amazing results guaranteed!"

# Global instance
script_generator = ScriptGenerator()