"""
Audio processing functionality for video generation
Handles TTS, audio enhancement, and audio manipulation
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import settings

class AudioProcessor:
    """Handles audio processing for video generation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.temp_dir = settings.TEMP_DIR
    
    def generate_voiceover(self, text: str, voice: str = "alloy", 
                          output_file: Optional[str] = None) -> Optional[str]:
        """
        Generate voiceover from text using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            output_file: Optional output file path
            
        Returns:
            str: Path to generated audio file, or None if failed
        """
        try:
            if not output_file:
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    output_file = f.name
            
            # Generate speech
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Write to file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            return output_file
            
        except Exception as e:
            print(f"Error generating voiceover: {e}")
            return None
    
    def enhance_audio_energy(self, input_file: str, output_file: str) -> bool:
        """
        Enhance audio with volume boost and energy processing
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Advanced audio enhancement
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-af', 'volume=10dB,compand=attacks=0.3:decays=0.8:points=-80/-900|-45/-15|-27/-9:gain=5',
                '-c:a', 'libmp3lame', '-b:a', '320k',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Advanced enhancement failed: {result.stderr}")
                # Fall back to simple volume boost
                return self._simple_volume_boost(input_file, output_file)
            
            return True
            
        except Exception as e:
            print(f"Error enhancing audio: {e}")
            return False
    
    def _simple_volume_boost(self, input_file: str, output_file: str) -> bool:
        """Simple volume boost fallback"""
        try:
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-af', 'volume=8dB',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error with simple volume boost: {e}")
            return False
    
    def create_advertisement_voiceover(self, text: str, voice: str = "alloy") -> Optional[str]:
        """
        Create energetic advertisement-style voiceover
        
        Args:
            text: Text to convert to speech
            voice: Voice to use
            
        Returns:
            str: Path to generated audio file, or None if failed
        """
        try:
            # Make text more energetic
            energetic_text = self._make_advertisement_energetic(text)
            
            # Generate voiceover
            temp_file = self.generate_voiceover(energetic_text, voice)
            if not temp_file:
                return None
            
            # Enhance audio energy
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                enhanced_file = f.name
            
            if self.enhance_audio_energy(temp_file, enhanced_file):
                os.unlink(temp_file)
                return enhanced_file
            else:
                return temp_file
                
        except Exception as e:
            print(f"Error creating advertisement voiceover: {e}")
            return None
    
    def _make_advertisement_energetic(self, text: str) -> str:
        """Transform text to be more energetic and advertisement-style"""
        energetic_patterns = [
            ("Are you", "Have you ever wondered if you're"),
            ("Do you", "Have you ever thought about whether you"),
            ("This is", "This is exactly what you've been looking for!"),
            ("We offer", "Get ready to experience"),
            ("Our product", "Discover the revolutionary"),
            ("You can", "You're about to"),
            ("It helps", "Watch how it transforms"),
            ("Benefits include", "Get ready for incredible benefits like"),
            ("Join", "Don't miss out - join"),
            ("Try", "Ready to try"),
            (".", "!"),  # Make statements more exciting
        ]
        
        energetic_text = text
        for old, new in energetic_patterns:
            energetic_text = energetic_text.replace(old, new)
        
        # Add hook questions at the start if not present
        if not any(starter in energetic_text.lower() for starter in ["have you", "are you", "do you", "ready to", "discover"]):
            if "tired" in energetic_text.lower() or "problem" in energetic_text.lower():
                energetic_text = "Have you ever faced this problem? " + energetic_text
            elif "solution" in energetic_text.lower() or "help" in energetic_text.lower():
                energetic_text = "Ready for the solution you've been waiting for? " + energetic_text
            else:
                energetic_text = "Have you ever wondered about this? " + energetic_text
        
        return energetic_text
    
    def get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Get duration of audio file in seconds"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
            
            import json
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
            
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return None
    
    def trim_audio(self, input_file: str, output_file: str, 
                  start_time: float = 0, duration: Optional[float] = None) -> bool:
        """Trim audio file to specified duration"""
        try:
            cmd = ['ffmpeg', '-y', '-i', input_file]
            
            if start_time > 0:
                cmd.extend(['-ss', str(start_time)])
            
            if duration:
                cmd.extend(['-t', str(duration)])
            
            cmd.append(output_file)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error trimming audio: {e}")
            return False

# Global audio processor instance
audio_processor = AudioProcessor()