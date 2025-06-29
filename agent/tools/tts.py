"""
Text-to-Speech Tool
Generates high-quality voiceover audio from script segments using ElevenLabs
"""
import json
import os
import requests
import time
from typing import List, Dict, Any

class TextToSpeechTool:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # ElevenLabs voice IDs for different tones
        self.voice_mapping = {
            "professional": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Professional female
            "energetic": "EXAVITQu4vr4xnSDxMaL",    # Sarah - Energetic female  
            "casual": "VR6AewLTigWG4xSOukaG",       # Arnold - Casual male
            "friendly": "pNInz6obpgDQGcFmaJgB",     # Adam - Friendly male
            "authoritative": "Yko7PKHZNXotIFUBG7I9"  # Antoni - Authoritative male
        }
    
    def run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            script = data.get('script', {})
            job_id = data.get('job_id', 'unknown')
            brand_info = data.get('brand_info', {})
            
            # Extract script segments
            segments = script.get('segments', [])
            if not segments and 'voiceover_text' in script:
                # Handle single text block
                segments = [{"voiceover": script['voiceover_text']}]
            
            # Determine voice based on brand tone
            tone = brand_info.get('tone', 'professional')
            voice_id = self.voice_mapping.get(tone, self.voice_mapping['professional'])
            
            audio_files = []
            total_duration = 0
            
            # Generate audio for each segment
            for i, segment in enumerate(segments):
                voiceover_text = segment.get('voiceover', '').strip()
                if not voiceover_text:
                    continue
                
                audio_file = f"assets/{job_id}_segment_{i}.mp3"
                
                # Generate audio using ElevenLabs
                if self.elevenlabs_api_key:
                    success, duration = self._generate_elevenlabs_audio(
                        voiceover_text, 
                        audio_file, 
                        voice_id
                    )
                    if success:
                        audio_files.append(audio_file)
                        total_duration += duration
                    else:
                        # Fallback to OpenAI TTS
                        success, duration = self._generate_openai_audio(
                            voiceover_text, 
                            audio_file
                        )
                        if success:
                            audio_files.append(audio_file)
                            total_duration += duration
                else:
                    # Use OpenAI TTS as fallback
                    success, duration = self._generate_openai_audio(
                        voiceover_text, 
                        audio_file
                    )
                    if success:
                        audio_files.append(audio_file)
                        total_duration += duration
            
            return json.dumps({
                "audio_files": audio_files,
                "total_duration": total_duration,
                "voice_id": voice_id,
                "tone": tone,
                "segments_generated": len(audio_files),
                "status": "success"
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"TTS generation failed: {str(e)}",
                "status": "failed"
            })
    
    def _generate_elevenlabs_audio(self, text: str, output_file: str, voice_id: str) -> tuple[bool, float]:
        """Generate audio using ElevenLabs API"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Ensure assets directory exists
                os.makedirs("assets", exist_ok=True)
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                # Estimate duration (rough calculation: ~150 words per minute)
                word_count = len(text.split())
                estimated_duration = (word_count / 150) * 60
                
                return True, estimated_duration
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False, 0
                
        except Exception as e:
            print(f"ElevenLabs generation error: {str(e)}")
            return False, 0
    
    def _generate_openai_audio(self, text: str, output_file: str) -> tuple[bool, float]:
        """Generate audio using OpenAI TTS as fallback"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # Professional voice
                input=text
            )
            
            # Ensure assets directory exists
            os.makedirs("assets", exist_ok=True)
            
            response.stream_to_file(output_file)
            
            # Estimate duration
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60
            
            return True, estimated_duration
            
        except Exception as e:
            print(f"OpenAI TTS generation error: {str(e)}")
            return False, 0