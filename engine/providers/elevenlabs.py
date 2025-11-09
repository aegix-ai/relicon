# type: ignore# type: ignore# type: ignore



"""

ElevenLabs audio generation provider - thin API wrapper.

Audio processing logic is handled by audio_orchestrator.py""""""

"""

    ElevenLabs audio generation provider - thin API wrapper.    ElevenLabs audio generation provider implementation.

import os

import requests    Audio processing logic is handled by audio_orchestrator.py"""

from typing import Dict, Any, Optional

"""



class ElevenLabsProvider:import os

    """ElevenLabs API provider - thin wrapper for API calls only."""

import osimport requests

    def __init__(self):

        """Initialize ElevenLabs with API key from environment."""import requestsimport subprocess

        self.api_key = os.environ.get("ELEVENLABS_API_KEY")

        if not self.api_key:from typing import Dict, Any, Optionalimport shutil

            raise ValueError("ELEVENLABS_API_KEY environment variable not set")

from pathlib import Path

        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"

        self.headers = {from typing import Dict, Any, List

            "Accept": "audio/mpeg",

            "Content-Type": "application/json",class ElevenLabsProvider:

            "xi-api-key": self.api_key

        }    """ElevenLabs API provider - thin wrapper for API calls only."""



    def generate_audio(self,class ElevenLabsProvider:

                      text: str,

                      output_path: str,    def __init__(self):    """ElevenLabs text-to-speech service implementation."""

                      voice_config: Optional[Dict[str, Any]] = None) -> bool:

        """        """Initialize ElevenLabs with API key from environment."""

        Generate audio from text using ElevenLabs API.

                self.api_key = os.environ.get("ELEVENLABS_API_KEY")    def __init__(self):

        Args:

            text: The text to convert to speech        if not self.api_key:        self.api_key = os.environ.get("ELEVENLABS_API_KEY")

            output_path: Where to save the audio file

            voice_config: Optional voice configuration (gender, tone)            raise ValueError("ELEVENLABS_API_KEY environment variable not set")        if not self.api_key:

            

        Returns:            raise ValueError("ELEVENLABS_API_KEY environment variable is required")

            True if successful, False otherwise

        """        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"

        try:

            voice_gender = voice_config.get('gender', 'neutral') if voice_config else 'neutral'        self.headers = {        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"

            voice_tone = voice_config.get('tone', 'energetic') if voice_config else 'energetic'

            "Accept": "audio/mpeg",        self.headers = {

            # ElevenLabs premium voice selection

            elevenlabs_voices = {            "Content-Type": "application/json",            "Accept": "audio/mpeg",

                ('male', 'energetic'): 'pNInz6obpgDQGcFmaJgB',      # Adam

                ('male', 'calm'): 'VR6AewLTigWG4xSOukaG',           # Arnold            "xi-api-key": self.api_key            "Content-Type": "application/json",

                ('male', 'authoritative'): 'ErXwobaYiN019PkySvjV',    # Antoni

                ('female', 'energetic'): 'EXAVITQu4vr4xnSDxMaL',     # Bella        }            "xi-api-key": self.api_key

                ('female', 'friendly'): 'MF3mGyEYCl7XYWbV9V6O',      # Elli

                ('female', 'professional'): 'ThT5KcBeYPX3keUQqHPh',  # Dorothy        }

                ('neutral', 'energetic'): 'EXAVITQu4vr4xnSDxMaL'     # Default to Bella

            }    def generate_audio(self,



            voice_id = elevenlabs_voices.get((voice_gender, voice_tone), 'EXAVITQu4vr4xnSDxMaL')                      text: str,    def generate_audio(self,



            data = {                      output_path: str,                       text: str,

                "text": text,

                "model_id": "eleven_multilingual_v2",                      voice_config: Optional[Dict[str, Any]] = None) -> bool:                       output_path: str,

                "voice_settings": {

                    "stability": 0.75,        """                       audio_config: Dict[str, Any]) -> bool:

                    "similarity_boost": 0.85,

                    "style": 0.8,        Generate audio from text using ElevenLabs API.        """Generate audio from text using ElevenLabs."""

                    "use_speaker_boost": True

                }                try:

            }

        Args:            voice_gender = audio_config.get('voice_gender', 'male')

            response = requests.post(

                f"{self.base_url}/{voice_id}",            text: The text to convert to speech            voice_tone = audio_config.get('voice_tone', 'energetic')

                json=data,

                headers=self.headers,            output_path: Where to save the audio file

                timeout=30

            )            voice_config: Optional voice configuration (gender, tone)            # Make text more energetic if needed



            if response.status_code == 200:                        if audio_config.get('energy_level') == 'high':

                with open(output_path, 'wb') as f:

                    f.write(response.content)        Returns:                energetic_text = self._make_text_energetic(text)

                print(f"ElevenLabs audio generated: {output_path}")

                return True            True if successful, False otherwise            else:

            else:

                print(f"ElevenLabs API error: {response.status_code} - {response.text}")        """                energetic_text = text

                return False

        try:

        except Exception as e:

            print(f"ElevenLabs generation failed: {e}")            voice_gender = voice_config.get('gender', 'neutral') if voice_config else 'neutral'            print(f"Generating ElevenLabs voice ({voice_gender}, {voice_tone})")

            return False

            voice_tone = voice_config.get('tone', 'energetic') if voice_config else 'energetic'            return self._generate_elevenlabs_audio(energetic_text, output_path, voice_gender, voice_tone)

    def generate_background_music(self,

                                  tone: str,

                                  duration: float,

                                  output_path: str) -> bool:            # ElevenLabs premium voice selection        except Exception as e:

        """

        Generate background music using ElevenLabs Music API.            elevenlabs_voices = {            print(f"TTS generation failed: {e}")

        

        Args:                ('male', 'energetic'): 'pNInz6obpgDQGcFmaJgB',      # Adam            return False

            tone: Music tone (energetic, calm, professional, inspiring, dramatic)

            duration: Duration in seconds (max 22s per ElevenLabs)                ('male', 'calm'): 'VR6AewLTigWG4xSOukaG',           # Arnold

            output_path: Where to save the music file

                            ('male', 'authoritative'): 'ErXwobaYiN019PkySvjV',    # Antoni    def _make_text_energetic(self,

        Returns:

            True if successful, False otherwise                ('female', 'energetic'): 'EXAVITQu4vr4xnSDxMaL',     # Bella                             text: str) -> str:

        """

        try:                ('female', 'friendly'): 'MF3mGyEYCl7XYWbV9V6O',      # Elli        """Transform text to be more energetic and advertisement-style."""

            # Tone-based music prompts

            music_prompts = {                ('female', 'professional'): 'ThT5KcBeYPX3keUQqHPh',  # Dorothy        energetic_patterns = [

                'energetic': "upbeat electronic background music with driving rhythm",

                'calm': "peaceful ambient background music with soft melody",                ('neutral', 'energetic'): 'EXAVITQu4vr4xnSDxMaL'     # Default to Bella            ("Are you", "Have you ever wondered if you're"),

                'professional': "corporate background music with confident tone",

                'inspiring': "uplifting cinematic background music",            }            ("Do you", "Have you ever thought about whether you"),

                'dramatic': "intense dramatic background music with build-up"

            }            ("This is", "This is exactly what you've been looking for!"),



            prompt = music_prompts.get(tone, music_prompts['energetic'])            voice_id = elevenlabs_voices.get((voice_gender, voice_tone), 'EXAVITQu4vr4xnSDxMaL')            ("We offer", "Get ready to experience"),

            print(f"Generating ElevenLabs background music: {tone} tone for {duration}s")

            ("Our product", "Discover the revolutionary"),

            # ElevenLabs Music Generation API

            music_url = "https://api.elevenlabs.io/v1/sound-generation"            data = {            ("You can", "You're about to"),

            music_headers = {

                "Accept": "audio/mpeg",                "text": text,            ("It helps", "Watch how it transforms"),

                "Content-Type": "application/json",

                "xi-api-key": self.api_key                "model_id": "eleven_multilingual_v2",            ("Benefits include", "Get ready for incredible benefits like"),

            }

                "voice_settings": {            ("Join", "Don't miss out - join"),

            music_data = {

                "text": prompt,                    "stability": 0.75,            ("Try", "Ready to try"),

                "duration_seconds": min(duration, 22),  # ElevenLabs max duration

                "prompt_influence": 0.3                    "similarity_boost": 0.85,            (".", "!"),

            }

                    "style": 0.8,        ]

            print(f"Calling ElevenLabs Music API with prompt: {prompt}")

            response = requests.post(                    "use_speaker_boost": True

                music_url,

                json=music_data,                }        energetic_text = text

                headers=music_headers,

                timeout=60            }        for old, new in energetic_patterns:

            )

            energetic_text = energetic_text.replace(old, new)

            if response.status_code == 200:

                with open(output_path, 'wb') as f:            response = requests.post(

                    f.write(response.content)

                print(f"ElevenLabs background music generated: {output_path}")                f"{self.base_url}/{voice_id}",        # Add hook questions at the start if not present

                return True

            else:                json=data,        if not any(starter in energetic_text.lower() for starter in ["have you", "are you", "do you", "ready to", "discover"]):

                print(f"ElevenLabs Music API error: {response.status_code} - {response.text}")

                return False                headers=self.headers,            if "tired" in energetic_text.lower() or "problem" in energetic_text.lower():



        except Exception as e:                timeout=30                energetic_text = "Have you ever faced this problem? " + energetic_text

            print(f"ElevenLabs music generation failed: {e}")

            return False            )            elif "solution" in energetic_text.lower() or "help" in energetic_text.lower():


                energetic_text = "Ready for the solution you've been waiting for? " + energetic_text

            if response.status_code == 200:            else:

                with open(output_path, 'wb') as f:                energetic_text = "Have you ever wondered about this? " + energetic_text

                    f.write(response.content)

                print(f"ElevenLabs audio generated: {output_path}")        return energetic_text

                return True

            else:    def generate_background_music(self,

                print(f"ElevenLabs API error: {response.status_code} - {response.text}")                                  duration: float,

                return False                                  tone: str,

                                  output_path: str) -> bool:

        except Exception as e:        """Generate background music using ElevenLabs music generation."""

            print(f"ElevenLabs generation failed: {e}")        try:

            return False            # ElevenLabs music generation prompts based on tone

            music_prompts = {

    def generate_background_music(self,                "friendly": "Warm, uplifting corporate background music with soft piano and gentle strings, professional and welcoming tone",

                                  tone: str,                "energetic": "High-energy upbeat commercial music with driving beats and bright melodies, motivating and exciting",

                                  duration: float,                "inspiring": "Inspiring motivational background music with soaring melodies and uplifting harmonies, empowering and positive",

                                  output_path: str) -> bool:                "calm": "Calm professional background music with soft ambient tones and subtle harmonies, peaceful and focused",

        """                "professional": "Sophisticated corporate background music with elegant piano and refined orchestration, trustworthy and polished"

        Generate background music using ElevenLabs Music API.            }

        

        Args:            prompt = music_prompts.get(tone, music_prompts["friendly"])

            tone: Music tone (energetic, calm, professional, inspiring, dramatic)            print(f"Generating ElevenLabs background music: {tone} tone for {duration}s")

            duration: Duration in seconds (max 22s per ElevenLabs)

            output_path: Where to save the music file            # ElevenLabs Music Generation API

                        music_url = "https://api.elevenlabs.io/v1/sound-generation"

        Returns:            music_headers = {

            True if successful, False otherwise                "Accept": "audio/mpeg",

        """                "Content-Type": "application/json",

        try:                "xi-api-key": self.api_key

            # Tone-based music prompts            }

            music_prompts = {

                'energetic': "upbeat electronic background music with driving rhythm",            music_data = {

                'calm': "peaceful ambient background music with soft melody",                "text": prompt,

                'professional': "corporate background music with confident tone",                "duration_seconds": min(duration, 22),  # ElevenLabs max duration

                'inspiring': "uplifting cinematic background music",                "prompt_influence": 0.3

                'dramatic': "intense dramatic background music with build-up"            }

            }

            print(f"Calling ElevenLabs Music API with prompt: {prompt}")

            prompt = music_prompts.get(tone, music_prompts['energetic'])            response = requests.post(

            print(f"Generating ElevenLabs background music: {tone} tone for {duration}s")                music_url,

                json=music_data,

            # ElevenLabs Music Generation API                headers=music_headers,

            music_url = "https://api.elevenlabs.io/v1/sound-generation"                timeout=60

            music_headers = {            )

                "Accept": "audio/mpeg",

                "Content-Type": "application/json",            if response.status_code == 200:

                "xi-api-key": self.api_key                with open(output_path, 'wb') as f:

            }                    f.write(response.content)

                print(f"ElevenLabs background music generated: {output_path}")

            music_data = {                return True

                "text": prompt,            else:

                "duration_seconds": min(duration, 22),  # ElevenLabs max duration                print(f"ElevenLabs Music API error: {response.status_code} - {response.text}")

                "prompt_influence": 0.3                return False

            }

        except Exception as e:

            print(f"Calling ElevenLabs Music API with prompt: {prompt}")            print(f"ElevenLabs music generation failed: {e}")

            response = requests.post(            return False

                music_url,

                json=music_data,    def _generate_elevenlabs_audio(self,

                headers=music_headers,                                   text: str,

                timeout=60                                   output_path: str,

            )                                   voice_gender: str,

                                   voice_tone: str) -> bool:

            if response.status_code == 200:        """Generate audio using ElevenLabs API."""

                with open(output_path, 'wb') as f:        try:

                    f.write(response.content)            # ElevenLabs premium voice selection

                print(f"ElevenLabs background music generated: {output_path}")            elevenlabs_voices = {

                return True                ('male', 'energetic'): 'pNInz6obpgDQGcFmaJgB',      # Adam

            else:                ('male', 'calm'): 'VR6AewLTigWG4xSOukaG',           # Arnold

                print(f"ElevenLabs Music API error: {response.status_code} - {response.text}")                ('male', 'authoritative'): 'ErXwobaYiN019PkySvjV',    # Antoni

                return False                ('female', 'energetic'): 'EXAVITQu4vr4xnSDxMaL',     # Bella

                ('female', 'friendly'): 'MF3mGyEYCl7XYWbV9V6O',      # Elli

        except Exception as e:                ('female', 'professional'): 'ThT5KcBeYPX3keUQqHPh',  # Dorothy

            print(f"ElevenLabs music generation failed: {e}")                ('neutral', 'energetic'): 'EXAVITQu4vr4xnSDxMaL'     # Default to Bella

            return False            }


            voice_id = elevenlabs_voices.get((voice_gender, voice_tone), 'EXAVITQu4vr4xnSDxMaL')

            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.85,
                    "style": 0.8,
                    "use_speaker_boost": True
                }
            }

            response = requests.post(
                f"{self.base_url}/{voice_id}",
                json=data,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"ElevenLabs audio generated: {output_path}")
                return True
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"ElevenLabs generation failed: {e}")
            return False

    def enhance_audio(self,
                      input_file: str,
                      output_file: str,
                      audio_config: Dict[str, Any]) -> None:
        """Enhance audio based on AI architectural decisions."""
        try:
            energy_level = audio_config.get('energy_level', 'medium')

            if energy_level == 'high':
                volume_boost = '12dB'
                compand_settings = 'attacks=0.2:decays=0.6:points=-80/-900|-45/-12|-27/-6:gain=6'
            elif energy_level == 'medium':
                volume_boost = '8dB'
                compand_settings = 'attacks=0.3:decays=0.8:points=-80/-900|-45/-15|-27/-9:gain=5'
            else:
                volume_boost = '4dB'
                compand_settings = 'attacks=0.5:decays=1.0:points=-80/-900|-45/-18|-27/-12:gain=3'

            print(f"Enhancing audio with {energy_level} energy profile...")

            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-af', f'volume={volume_boost},compand={compand_settings}',
                '-c:a', 'libmp3lame', '-b:a', '320k',
                output_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Audio enhancement failed: {result.stderr}")
                shutil.copy2(input_file, output_file)
            else:
                print(f"Audio enhanced: {output_file}")

        except Exception as e:
            print(f"Warning: Audio enhancement failed: {e}")
            shutil.copy2(input_file, output_file)

    def create_unified_audio(self,
                             audio_segments: List[Dict[str, Any]],
                             target_duration: float,
                             output_path: str) -> bool:
        """Create unified audio track with precise timing."""
        try:
            if not audio_segments:
                print("No audio segments provided")
                return False

            total_duration = sum(seg.get('duration', 0) for seg in audio_segments)

            if total_duration == 0:
                print("Total audio duration is 0")
                return False

            # Create filter complex for concatenation and timing
            filter_parts = []
            input_files = []

            for i, segment in enumerate(audio_segments):
                input_files.extend(['-i', segment['file']])
                filter_parts.append(f"[{i}:a]")

            # Concatenate all segments
            concat_filter = f"{''.join(filter_parts)}concat=n={len(audio_segments)}:v=0:a=1[concatenated]"

            # Adjust speed to fit target duration
            speed_factor = total_duration / target_duration
            speed_filter = f"[concatenated]atempo={speed_factor:.3f}[adjusted]"

            # Add fade out at the end
            fade_filter = f"[adjusted]afade=out:st={target_duration-1:.1f}:d=1[final]"

            # Combine all filters
            full_filter = f"{concat_filter};{speed_filter};{fade_filter}"

            cmd = [
                'ffmpeg', '-y'
            ] + input_files + [
                '-filter_complex', full_filter,
                '-map', '[final]',
                '-c:a', 'libmp3lame', '-b:a', '320k',
                '-t', str(target_duration),
                output_path
            ]

            print(f"Creating unified {target_duration}s audio from {len(audio_segments)} segments...")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Unified audio created: {output_path}")
                return True
            else:
                print(f"Audio unification failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"Audio unification error: {e}")
            return False
