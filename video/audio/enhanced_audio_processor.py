"""Enhanced audio processing with ElevenLabs integration and human-like speech"""
import os
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import time
from config.settings import settings

class EnhancedAudioProcessor:
    """Enhanced audio processor with ElevenLabs and human-like speech"""
    
    def __init__(self):
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
        self.output_dir = Path(settings.OUTPUT_DIR) / "audio"
        self.output_dir.mkdir(exist_ok=True)
        
        # Human-like voice settings for ElevenLabs
        self.voice_settings = {
            "stability": 0.5,       # More variation for natural speech
            "similarity_boost": 0.8,  # High similarity to original voice
            "style": 0.4,           # Moderate style exaggeration
            "use_speaker_boost": True
        }
        
        # Best ElevenLabs voices for human-like speech
        self.voices = {
            "professional": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Professional female
            "conversational": "29vD33N1CtxCmqQRPOHJ",  # Drew - Conversational male
            "warm": "EXAVITQu4vr4xnSDxMaL",           # Bella - Warm female
            "casual": "VR6AewLTigWG4xSOukaG",         # Arnold - Casual male
            "natural": "pNInz6obpgDQGcFmaJgB",        # Adam - Natural male
        }
    
    def create_human_voiceover(self, text: str, voice_style: str = "natural") -> Optional[str]:
        """Create human-like voiceover with ElevenLabs"""
        try:
            # First try ElevenLabs for highest quality
            if self.elevenlabs_api_key:
                audio_file = self._generate_elevenlabs_audio(text, voice_style)
                if audio_file:
                    print(f"Generated ElevenLabs audio: {audio_file}")
                    # Enhance audio to make it more human-like
                    enhanced_file = self._enhance_human_qualities(audio_file)
                    return enhanced_file or audio_file
            
            # Fallback to OpenAI with human-like settings
            print("Falling back to OpenAI TTS...")
            return self._generate_openai_human_audio(text)
            
        except Exception as e:
            print(f"Human voiceover generation error: {e}")
            return None
    
    def _generate_elevenlabs_audio(self, text: str, voice_style: str) -> Optional[str]:
        """Generate audio using ElevenLabs API with human-like settings"""
        try:
            voice_id = self.voices.get(voice_style, self.voices["natural"])
            
            # Make text sound more human and less robotic
            humanized_text = self._humanize_text(text)
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": humanized_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": self.voice_settings
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                output_file = self.output_dir / f"elevenlabs_{int(time.time())}.mp3"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return str(output_file)
            
            return None
            
        except Exception as e:
            print(f"ElevenLabs generation error: {e}")
            return None
    
    def _generate_openai_human_audio(self, text: str) -> Optional[str]:
        """Generate human-like audio using OpenAI TTS"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Humanize text for more natural speech
            humanized_text = self._humanize_text(text)
            
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="alloy",  # Most natural voice
                input=humanized_text,
                speed=0.9  # Slightly slower for more natural delivery
            )
            
            output_file = self.output_dir / f"openai_human_{int(time.time())}.mp3"
            response.stream_to_file(output_file)
            
            # Enhance for human qualities
            enhanced_file = self._enhance_human_qualities(str(output_file))
            return enhanced_file or str(output_file)
            
        except Exception as e:
            print(f"OpenAI human audio generation error: {e}")
            return None
    
    def _humanize_text(self, text: str) -> str:
        """Make text more natural and human-like"""
        # Add natural pauses and emphasis
        humanized = text
        
        # Add slight pauses after commas
        humanized = humanized.replace(',', '... ')
        
        # Add emphasis to key words
        humanized = humanized.replace('!', '. ')
        
        # Make sentences flow more naturally
        humanized = humanized.replace('. ', '... ')
        
        # Add natural speech patterns
        if not humanized.endswith('.'):
            humanized += '.'
        
        return humanized
    
    def _enhance_human_qualities(self, audio_file: str) -> Optional[str]:
        """Enhance audio to sound more human and less robotic"""
        try:
            output_file = self.output_dir / f"enhanced_{int(time.time())}.mp3"
            
            # FFmpeg command to enhance human qualities
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_file,
                # Add subtle reverb for natural room sound
                "-af", (
                    "aresample=44100,"
                    "volume=0.9,"
                    "highpass=f=80,"  # Remove low-frequency noise
                    "lowpass=f=8000,"  # Remove high-frequency harshness
                    "compand=0.02,0.20:-60/-60|-30/-15|-20/-10|-5/-5|0/-3:0.02:0.0:-3,"  # Natural compression
                    "reverb=0.5:0.5:0.1:0.1:0.1:0.1"  # Subtle reverb
                ),
                "-ar", "44100",
                "-b:a", "192k",
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return str(output_file)
            
            return None
            
        except Exception as e:
            print(f"Audio enhancement error: {e}")
            return None

# Global instance
enhanced_audio_processor = EnhancedAudioProcessor()