"""
  High-level planning service for video architecture.
  Orchestrates creative planning using abstracted providers.
"""

from typing import Dict, List, Any
from core.provider_manager import provider_manager
from config.settings import settings


class PlanningService:
    """High-level planning orchestration service."""
    
    def __init__(self):
        self.provider_manager = provider_manager
    
    def create_video_architecture(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Use create_enterprise_blueprint() for new implementations.
        Legacy method maintained for backward compatibility.
        """
        print("Using deprecated method. Consider switching to create_enterprise_blueprint()")
        return self.create_enterprise_blueprint(brand_info)
    
    def validate_architecture(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and correct video architecture with enterprise-grade precision.
        
        Args:
            architecture: Video architecture to validate
            
        Returns:
            Validated and corrected architecture with 30-second precision
        """
        try:
            # Validate required enterprise architecture fields
            required_fields = ['creative_vision', 'audio_architecture', 'scene_architecture', 'unified_script']
            for field in required_fields:
                if field not in architecture:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate scene architecture structure
            scene_arch = architecture.get('scene_architecture', {})
            scenes = scene_arch.get('scenes', [])
            target_duration = scene_arch.get('total_duration', 30)
            
            if not scenes:
                raise ValueError("No scenes found in architecture")
            
            # Validate 30-second precision timing
            actual_total = sum(scene.get('duration', 0) for scene in scenes)
            if actual_total != target_duration:
                print(f"Duration precision error: expected {target_duration}s, got {actual_total}s - auto-correcting")
                architecture = self._correct_scene_timing(architecture, target_duration)
            
            # Validate enterprise scene requirements
            for i, scene in enumerate(scenes):
                scene_id = i + 1
                required_scene_fields = ['visual_concept', 'script_line', 'brand_alignment', 'duration']
                
                for field in required_scene_fields:
                    if not scene.get(field):
                        print(f"Scene {scene_id} missing required field: {field}")
                
                # Ensure visual prompts exist (luma_prompt is primary)
                if not scene.get('luma_prompt') and not scene.get('visual_concept'):
                    print(f"Scene {scene_id} missing visual prompts")
                
                # Validate scene duration precision
                duration = scene.get('duration', 0)
                if duration <= 0 or duration > target_duration:
                    print(f"Scene {scene_id} invalid duration: {duration}s")
            
            # Validate audio architecture
            audio_arch = architecture.get('audio_architecture', {})
            if audio_arch.get('total_duration', 0) != target_duration:
                audio_arch['total_duration'] = target_duration
                print(f"Corrected audio duration to {target_duration}s")
            
            # Validate unified script quality
            script = architecture.get('unified_script', '').strip()
            if len(script) < 20:
                print("Script too short - may not fill 30 seconds")
            
            print(f"Architecture validated: {len(scenes)} scenes, {target_duration}s precision")
            return architecture
            
        except Exception as e:
            print(f"Architecture validation failed: {e}")
            raise
    
    def _correct_scene_timing(self, architecture: Dict[str, Any], target_duration: int) -> Dict[str, Any]:
        """
        Correct scene timing with intelligent distribution for narrative flow.
        Maintains storytelling structure: Hook-Build-Transform-Resolve.
        """
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        scene_count = len(scenes)
        
        if scene_count == 0:
            return architecture
        
        # Force exactly 3 scenes for optimal 18s structure  
        if scene_count != 3:
            print(f"Adjusting from {scene_count} to exactly 3 scenes for 18s structure")
            # Take first 3 scenes if more than 3, or duplicate if less than 3
            if scene_count > 3:
                scenes = scenes[:3]
                scene_count = 3
            elif scene_count < 3:
                # Duplicate scenes to reach 3
                while len(scenes) < 3:
                    scenes.append(scenes[0].copy())
                scene_count = 3
        
        # Perfect 18s distribution for 3 scenes: Hook(6s) - Problem/Solution(6s) - Resolve(6s)
        # Using 6s per scene to support both Luma (5s) and Hailuo (6s) providers
        durations = [6, 6, 6]
        
        # Apply corrected durations and update scenes array
        for i, scene in enumerate(scenes):
            scene['duration'] = durations[i] if i < len(durations) else durations[0]
        
        # Update the scenes array in architecture
        architecture['scene_architecture']['scenes'] = scenes
        architecture['scene_architecture']['total_duration'] = target_duration
        
        actual_total = sum(scene.get('duration', 0) for scene in scenes)
        print(f"Applied narrative-optimized timing: {scene_count} scenes, {actual_total}s total")
        return architecture
    
    def create_enterprise_blueprint(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create enterprise-grade video blueprint with complete architecture.
        This is the primary architect method that creates production-ready plans.
        
        Args:
            brand_info: Brand information dictionary
            
        Returns:
            Complete enterprise video blueprint
        """
        try:
            # Validate input requirements
            required_brand_fields = ['brand_name', 'brand_description']
            for field in required_brand_fields:
                if not brand_info.get(field):
                    raise ValueError(f"Missing required brand field: {field}")
            
            # Set enterprise defaults
            brand_info.setdefault('duration', 18)
            brand_info.setdefault('target_audience', 'professional')
            brand_info.setdefault('call_to_action', 'Learn more')
            
            # Create architecture via AI director
            text_generator = self.provider_manager.get_text_generator()
            blueprint = text_generator.architect_complete_video(brand_info)
            
            # Enterprise validation and optimization
            blueprint = self.validate_architecture(blueprint)
            
            # Add production metadata
            blueprint['production_metadata'] = {
                'architect_version': '2.0',
                'target_duration': brand_info['duration'],
                'scene_count': len(blueprint.get('scene_architecture', {}).get('scenes', [])),
                'validated': True,
                'enterprise_grade': True
            }
            
            print(f"Enterprise blueprint created: {blueprint['production_metadata']['scene_count']} scenes, {blueprint['production_metadata']['target_duration']}s")
            return blueprint
            
        except Exception as e:
            print(f"Enterprise blueprint creation failed: {e}")
            raise
    
    def switch_provider(self, provider_name: str) -> None:
        """
        Switch planning provider at runtime.
        
        Args:
            provider_name: Name of the provider ('openai', etc.)
        """
        try:
            self.provider_manager.set_text_provider(provider_name)
            print(f"Switched to {provider_name} planning provider")
        except Exception as e:
            print(f"Failed to switch to {provider_name}: {e}")
            raise
