"""
OpenAI API client for AI functionality
Handles all interactions with OpenAI services (GPT, TTS, etc.)
"""
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config.settings import settings

class OpenAIClient:
    """Client for OpenAI API services"""
    
    def __init__(self):
        self.client = OpenAI(**settings.get_openai_client_config())
        self.default_model = "gpt-4o"
        self.tts_model = "tts-1"
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None,
                     model: Optional[str] = None, max_tokens: int = 1000,
                     temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using GPT
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use (defaults to gpt-4o)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            str: Generated text, or None if failed
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating text: {e}")
            return None
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                     model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate JSON response using GPT
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use
            
        Returns:
            dict: Parsed JSON response, or None if failed
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error generating JSON: {e}")
            return None
    
    def generate_speech(self, text: str, voice: str = "alloy",
                       output_file: Optional[str] = None) -> Optional[str]:
        """
        Generate speech from text using TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            output_file: Optional output file path
            
        Returns:
            str: Path to audio file, or None if failed
        """
        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return output_file
            else:
                # Return raw content for temporary use
                return response.content
                
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
            
        Returns:
            str: Transcribed text, or None if failed
        """
        try:
            with open(audio_file, 'rb') as f:
                kwargs = {"model": "whisper-1", "file": f}
                if language:
                    kwargs["language"] = language
                
                response = self.client.audio.transcriptions.create(**kwargs)
                return response.text
                
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Sentiment analysis result with rating and confidence
        """
        try:
            system_prompt = """
            You are a sentiment analysis expert. Analyze the sentiment of the text 
            and provide a rating from 1 to 5 stars and a confidence score between 0 and 1.
            Respond with JSON in this format:
            {"rating": number, "confidence": number, "sentiment": "positive|negative|neutral"}
            """
            
            result = self.generate_json(text, system_prompt)
            if result:
                # Ensure values are within valid ranges
                result["rating"] = max(1, min(5, round(result.get("rating", 3))))
                result["confidence"] = max(0, min(1, result.get("confidence", 0.5)))
                return result
            
            return None
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return None
    
    def generate_image_description(self, prompt: str) -> Optional[str]:
        """
        Generate detailed image description for DALL-E or other image generation
        
        Args:
            prompt: Basic prompt for image
            
        Returns:
            str: Detailed image description, or None if failed
        """
        try:
            system_prompt = """
            You are an expert at creating detailed image descriptions for AI image generation.
            Create a detailed, specific description that would produce high-quality results.
            Include style, lighting, composition, and other artistic elements.
            """
            
            enhanced_prompt = f"Create a detailed image description for: {prompt}"
            return self.generate_text(enhanced_prompt, system_prompt)
            
        except Exception as e:
            print(f"Error generating image description: {e}")
            return None
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text (approximate)
        
        Args:
            text: Text to count tokens for
            model: Model to use for counting (affects tokenization)
            
        Returns:
            int: Approximate token count
        """
        try:
            # Simple approximation: ~4 characters per token
            return len(text) // 4
        except:
            return 0

# Global OpenAI client instance
openai_client = OpenAIClient()