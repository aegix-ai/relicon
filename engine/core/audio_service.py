"""
  High-level audio generation service.
  Orchestrates audio creation using abstracted providers.
"""

import os
import tempfile
from typing import Dict, Any, List
from pathlib import Path
from core.provider_manager import provider_manager
from core.music_service import music_service
from core.logger import audio_logger
from config.settings import settings


class AudioService:
    """High-level audio generation orchestration service."""
    
    def __init__(self):
        self.provider_manager = provider_manager
    
    def generate_audio_from_architecture(self, architecture: Dict[str, Any], output_path: str) -> bool:
        """
        Generate complete audio track from architectural plan.
        
        Args:
            architecture: Video architecture from planning service
            output_path: Path to save final audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract script and audio configuration
            script = architecture.get('unified_script', '')
            audio_config = architecture.get('audio_architecture', {})
            
            if not script:
                audio_logger.error("No script found in architecture", "audio.validation.failed",
                                  **{"audio.missing_field": "unified_script"})
                return False
            
            # Get target duration - ensure it's 18s
            target_duration = architecture.get('scene_architecture', {}).get('total_duration', 18)
            print(f"DEBUG: Audio service target_duration = {target_duration}s")
            
            # Generate audio segments for each scene
            scenes = architecture.get('scene_architecture', {}).get('scenes', [])
            audio_segments = []
            
            if len(scenes) > 1:
                # Split script by scenes
                script_parts = self._split_script_by_scenes(script, scenes)
            else:
                # Single scene
                script_parts = [script]
            
            # Generate audio for each part
            audio_generator = self.provider_manager.get_audio_generator()
            temp_dir = tempfile.mkdtemp()
            
            try:
                for i, (scene, script_part) in enumerate(zip(scenes, script_parts)):
                    if not script_part.strip():
                        continue
                    
                    temp_audio_path = os.path.join(temp_dir, f"segment_{i:02d}.mp3")
                    
                    if audio_generator.generate_audio(script_part, temp_audio_path, audio_config):
                        audio_segments.append({
                            'file': temp_audio_path,
                            'duration': scene.get('duration', 5),
                            'scene_number': i + 1
                        })
                        print(f"Generated audio segment {i + 1}")
                    else:
                        print(f"Failed to generate audio segment {i + 1}")
                
                # Create unified audio track
                if audio_segments:
                    # Generate voice-only audio first
                    temp_voice_path = os.path.join(tempfile.mkdtemp(), "voice_only.mp3")
                    voice_success = audio_generator.create_unified_audio(
                        audio_segments, target_duration, temp_voice_path
                    )
                    
                    if voice_success:
                        print(f"Unified voice audio created: {temp_voice_path}")
                        
                        # Add background music to voice
                        tone = audio_config.get('voice_tone', 'friendly')
                        music_success = music_service.create_audio_with_music(
                            temp_voice_path, target_duration, tone, output_path
                        )
                        
                        if music_success:
                            print(f"Complete audio with background music: {output_path}")
                            return True
                        else:
                            print("CRITICAL: Music mixing failed - this should not happen!")
                            # Force music integration - don't fallback to voice only
                            raise Exception("Background music integration failed - all ads must have music")
                    else:
                        print("Failed to create unified audio")
                        return False
                else:
                    print("No audio segments generated")
                    return False
                    
            finally:
                # Cleanup temporary files
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"Audio generation failed: {e}")
            return False
    
    def _split_script_by_scenes(self, script: str, scenes: List[Dict[str, Any]]) -> List[str]:
        """Split script into parts based on scene count and duration, preventing repetition."""
        if not scenes:
            return [script]
        
        # First check if scenes have individual script_line
        script_parts = []
        for i, scene in enumerate(scenes):
            if 'script_line' in scene and scene['script_line'].strip():
                script_parts.append(scene['script_line'].strip())
            else:
                # Fallback: split unified script evenly
                sentences = script.split('. ')
                sentences_per_scene = max(1, len(sentences) // len(scenes))
                start_idx = i * sentences_per_scene
                end_idx = min((i + 1) * sentences_per_scene, len(sentences))
                if i == len(scenes) - 1:  # Last scene gets remaining sentences
                    end_idx = len(sentences)
                scene_sentences = sentences[start_idx:end_idx]
                script_parts.append('. '.join(scene_sentences))
        
        # Ensure we have parts for all scenes
        while len(script_parts) < len(scenes):
            script_parts.append("Discover the future of innovation.")
        
        # Truncate if we have too many parts
        script_parts = script_parts[:len(scenes)]
        
        return script_parts
    
    def generate_single_audio(self, text: str, output_path: str, audio_config: Dict[str, Any] = None) -> bool:
        """
        Generate a single audio file from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            audio_config: Audio configuration parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if audio_config is None:
                audio_config = {
                    'voice_gender': 'male',
                    'voice_tone': 'energetic',
                    'energy_level': 'high'
                }
            
            audio_generator = self.provider_manager.get_audio_generator()
            return audio_generator.generate_audio(text, output_path, audio_config)
            
        except Exception as e:
            print(f"Single audio generation failed: {e}")
            return False
    
    def switch_provider(self, provider_name: str) -> None:
        """
        Switch audio generation provider at runtime.
        
        Args:
            provider_name: Name of the provider ('elevenlabs', etc.)
        """
        try:
            self.provider_manager.set_audio_provider(provider_name)
            print(f"Switched to {provider_name} audio provider")
        except Exception as e:
            print(f"Failed to switch to {provider_name}: {e}")
            raise
