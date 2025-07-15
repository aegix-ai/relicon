"""OpenAI client module"""
import os
from typing import Dict, Any, Optional
from config.settings import settings

class OpenAIClient:
    """OpenAI client for text and speech generation"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI library not installed")
    
    def generate_text(self, prompt: str, max_tokens: int = 100) -> Optional[str]:
        """Generate text with OpenAI"""
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI text generation error: {e}")
            return None
    
    def generate_speech(self, text: str, voice: str = "alloy") -> Optional[bytes]:
        """Generate speech with OpenAI TTS"""
        if not self.client:
            return None
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            print(f"OpenAI TTS error: {e}")
            return None

# Global instance
openai_client = OpenAIClient()