"""
Mock audio generation provider for testing without ElevenLabs API.
"""

import os
import time
import subprocess
from typing import Optional
from interfaces.audio_generator import AudioGenerator


class MockAudioProvider(AudioGenerator):
    """Mock audio generator for testing without API calls."""

    def __init__(self):
        print("🎭 Mock Audio Provider initialized (no API key required)")

    def generate_speech(self, text: str, voice_id: str = "default",
                       output_path: Optional[str] = None) -> str:
        """Generate mock speech audio."""

        print(f"🎭 Mock speech generation started")
        print(f"   Text: {text[:80]}...")
        print(f"   Voice: {voice_id}")

        # Simulate API call time
        time.sleep(1)

        if output_path:
            self._create_mock_audio_file(output_path, duration=18)
            print(f"✅ Mock speech created: {output_path}")
            return output_path
        else:
            mock_url = f"https://mock-audio-cdn.example.com/speech_{int(time.time())}.mp3"
            print(f"✅ Mock speech URL: {mock_url}")
            return mock_url

    def generate_music(self, prompt: str, duration: int = 30,
                      output_path: Optional[str] = None) -> str:
        """Generate mock background music."""

        print(f"🎭 Mock music generation started")
        print(f"   Prompt: {prompt[:80]}...")
        print(f"   Duration: {duration}s")

        # Simulate API call time
        time.sleep(1)

        if output_path:
            self._create_mock_audio_file(output_path, duration=duration)
            print(f"✅ Mock music created: {output_path}")
            return output_path
        else:
            mock_url = f"https://mock-audio-cdn.example.com/music_{int(time.time())}.mp3"
            print(f"✅ Mock music URL: {mock_url}")
            return mock_url

    def _create_mock_audio_file(self, output_path: str, duration: int = 18) -> bool:
        """Create a mock audio file."""

        print(f"🎭 Creating mock audio file: {output_path}")

        try:
            if self._is_ffmpeg_available():
                success = self._create_test_audio_with_ffmpeg(output_path, duration)
            else:
                success = self._create_placeholder_audio(output_path)

            if success:
                file_size = os.path.getsize(output_path)
                print(f"✅ Mock audio created: {file_size:,} bytes")
                return True
            else:
                print(f"❌ Failed to create mock audio")
                return False

        except Exception as e:
            print(f"❌ Mock audio creation error: {e}")
            return False

    def _is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _create_test_audio_with_ffmpeg(self, output_path: str, duration: int) -> bool:
        """Create a simple test audio file using FFmpeg."""
        try:
            # Create a silent audio file with the specified duration
            command = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', str(duration),
                '-c:a', 'libmp3lame',
                '-b:a', '128k',
                '-y',
                output_path
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            return result.returncode == 0

        except Exception as e:
            print(f"FFmpeg test audio creation failed: {e}")
            return False

    def _create_placeholder_audio(self, output_path: str) -> bool:
        """Create a placeholder audio file when FFmpeg is not available."""
        try:
            # Create a minimal MP3 file header
            with open(output_path, 'wb') as f:
                # Write minimal MP3 header
                f.write(b'\xFF\xFB\x90\x00')
                f.write(b'\x00' * 1024 * 10)  # 10KB placeholder

            print("⚠️  Created placeholder audio (FFmpeg not available for real test audio)")
            return True

        except Exception as e:
            print(f"Placeholder audio creation failed: {e}")
            return False

    def text_to_speech(self, text: str, voice: str = "default") -> str:
        """Mock text to speech."""
        return self.generate_speech(text, voice_id=voice)
