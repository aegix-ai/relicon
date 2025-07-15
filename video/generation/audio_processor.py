"""Audio processing module"""
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
from config.settings import settings

class AudioProcessor:
    """Audio processing service"""
    
    def create_advertisement_voiceover(self, text: str, voice: str = "alloy") -> Optional[str]:
        """Create voiceover using OpenAI TTS"""
        try:
            from external.apis.openai_client import openai_client
            
            # Generate TTS
            audio_data = openai_client.generate_speech(text, voice)
            
            if audio_data:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_file.write(audio_data)
                temp_file.close()
                
                return temp_file.name
            
            return None
            
        except Exception as e:
            print(f"TTS generation error: {e}")
            return None
    
    def enhance_audio_energy(self, input_file: str, output_file: str) -> bool:
        """Enhance audio with energy processing"""
        try:
            if not os.path.exists(input_file):
                return False
            
            # Use FFmpeg to enhance audio
            cmd = [
                "ffmpeg", "-y",
                "-i", input_file,
                "-af", "volume=1.5,highpass=f=200,lowpass=f=3000",
                "-c:a", "mp3",
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Audio enhancement error: {e}")
            return False

# Global instance
audio_processor = AudioProcessor()