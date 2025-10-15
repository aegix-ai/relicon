"""
  Background music service for enterprise video generation.
  Provides professional background music tracks for commercial ads.
"""

import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Optional


class MusicService:
    """Background music generation and integration service."""
    
    def __init__(self):
        self.music_library = self._get_built_in_music_tracks()
    
    def _get_built_in_music_tracks(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in music tracks using FFmpeg tone generation."""
        return {
            "energetic_commercial": {
                "description": "Upbeat commercial background music",
                "frequency_pattern": [220, 261, 329, 392],  # A3, C4, E4, G4
                "tempo": "fast",
                "volume": 0.4
            },
            "friendly_corporate": {
                "description": "Warm, professional background music",
                "frequency_pattern": [174, 220, 261, 329],  # F3, A3, C4, E4
                "tempo": "medium",
                "volume": 0.35
            },
            "inspiring_upbeat": {
                "description": "Motivational background music",
                "frequency_pattern": [196, 246, 293, 349],  # G3, B3, D4, F4
                "tempo": "fast",
                "volume": 0.45
            },
            "calm_professional": {
                "description": "Subtle, professional background music",
                "frequency_pattern": [164, 196, 246, 293],  # E3, G3, B3, D4
                "tempo": "slow",
                "volume": 0.3
            }
        }
    
    def generate_background_music(self, duration: float, tone: str = "friendly", 
                                output_path: str = None) -> Optional[str]:
        """
        Generate background music track using ElevenLabs.
        
        Args:
            duration: Duration in seconds (typically 18s for our ads)
            tone: Music tone (friendly, energetic, inspiring, calm)
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to generated music file or None if failed
        """
        try:
            if output_path is None:
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, "background_music.mp3")
            
            # Import ElevenLabs provider for music generation
            from providers.elevenlabs import ElevenLabsProvider
            
            try:
                elevenlabs = ElevenLabsProvider()
                success = elevenlabs.generate_background_music(duration, tone, output_path)
                
                if success and os.path.exists(output_path):
                    print(f"ElevenLabs background music generated: {output_path}")
                    return output_path
                else:
                    print(f"ElevenLabs music generation failed")
                    return None
                    
            except Exception as elevenlabs_error:
                print(f"ElevenLabs music generation failed: {elevenlabs_error}")
                return None
                
        except Exception as e:
            print(f"Music generation error: {e}")
            return None
    
    def mix_audio_with_music(self, voice_path: str, music_path: str, 
                           output_path: str, voice_volume: float = 1.0, 
                           music_volume: float = 0.15) -> bool:
        """
        Mix voiceover with background music.
        
        Args:
            voice_path: Path to voiceover audio
            music_path: Path to background music
            output_path: Output path for mixed audio
            voice_volume: Voice volume level (1.0 = normal)
            music_volume: Music volume level (0.15 = subtle background)
            
        Returns:
            True if mixing successful, False otherwise
        """
        try:
            print(f"🎵 Mixing voiceover with background music...")
            
            # Verify input audio levels first using correct FFmpeg syntax
            voice_probe = subprocess.run(['ffmpeg', '-i', voice_path, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
            music_probe = subprocess.run(['ffmpeg', '-i', music_path, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
            print(f"DEBUG Voice levels: {voice_probe.stderr.split('volumedetect')[1] if 'volumedetect' in voice_probe.stderr else 'No volume data'}")
            print(f"DEBUG Music levels: {music_probe.stderr.split('volumedetect')[1] if 'volumedetect' in music_probe.stderr else 'No volume data'}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', voice_path,
                '-i', music_path,
                '-filter_complex', 
                f'[0:a]volume={voice_volume}[voice];[1:a]volume={music_volume * 0.3}[music];[voice][music]amix=inputs=2:duration=shortest:normalize=0[mixed]',
                '-map', '[mixed]',
                '-c:a', 'libmp3lame', '-b:a', '320k',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify final mixed audio levels
                final_probe = subprocess.run(['ffmpeg', '-i', output_path, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
                print(f"DEBUG Final mixed levels: {final_probe.stderr.split('volumedetect')[1] if 'volumedetect' in final_probe.stderr else 'No volume data'}")
                print(f"Audio mixed with background music: {output_path}")
                return True
            else:
                print(f"Audio mixing failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Audio mixing error: {e}")
            return False
    
    def create_audio_with_music(self, voice_audio_path: str, duration: float, 
                              tone: str, output_path: str) -> bool:
        """
        Create complete audio track with voiceover and background music.
        
        Args:
            voice_audio_path: Path to generated voiceover
            duration: Target duration in seconds
            tone: Music tone to match ad mood
            output_path: Final output path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate background music
            temp_dir = tempfile.mkdtemp()
            music_path = os.path.join(temp_dir, "bg_music.mp3")
            
            if not self.generate_background_music(duration, tone, music_path):
                print("CRITICAL: Background music generation failed!")
                raise Exception("Background music generation failed - all ads must have music")
            
            # Mix voice with background music (50% music volume as requested)
            success = self.mix_audio_with_music(
                voice_audio_path, music_path, output_path, 
                voice_volume=1.0, music_volume=0.5
            )
            
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return success
            
        except Exception as e:
            print(f"Complete audio creation failed: {e}")
            # NO FALLBACK - music is mandatory
            raise Exception(f"Audio with music creation failed: {e}")


# Global music service instance
music_service = MusicService()
