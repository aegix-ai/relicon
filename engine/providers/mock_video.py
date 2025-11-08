"""
Mock video generation provider for testing without Luma/Hailuo API.
"""

import os
import time
import subprocess
from typing import Optional
from interfaces.video_generator import VideoGenerator


class MockVideoProvider(VideoGenerator):
    """Mock video generator for testing without API calls."""

    def __init__(self):
        print("🎭 Mock Video Provider initialized (no API key required)")

    def generate_video(self, prompt: str, aspect_ratio: str = "9:16",
                      image_url: Optional[str] = None, force_unique: bool = False, **kwargs) -> str:
        """Generate mock video without calling real API."""

        print(f"🎭 Mock video generation started")
        print(f"   Prompt: {prompt[:80]}...")
        print(f"   Aspect Ratio: {aspect_ratio}")
        if image_url:
            print(f"   Using keyframe image: {image_url[:50]}...")

        # Simulate API call time (2-5 seconds instead of 2-5 minutes)
        wait_time = 3
        print(f"   Simulating generation... ({wait_time}s)")
        time.sleep(wait_time)

        # Return mock video URL
        mock_url = f"https://mock-video-cdn.example.com/video_{int(time.time())}.mp4"
        print(f"✅ Mock video generated: {mock_url}")

        return mock_url

    def download_video(self, video_url: str, output_path: str, max_retries: int = 3) -> bool:
        """Create mock video file instead of downloading."""

        print(f"🎭 Creating mock video file: {output_path}")

        try:
            # Create a simple test video using FFmpeg (if available)
            # Otherwise create a placeholder file
            if self._is_ffmpeg_available():
                success = self._create_test_video_with_ffmpeg(output_path)
            else:
                success = self._create_placeholder_video(output_path)

            if success:
                file_size = os.path.getsize(output_path)
                print(f"✅ Mock video created: {file_size:,} bytes")
                return True
            else:
                print(f"❌ Failed to create mock video")
                return False

        except Exception as e:
            print(f"❌ Mock video creation error: {e}")
            return False

    def _is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _create_test_video_with_ffmpeg(self, output_path: str) -> bool:
        """Create a simple test video using FFmpeg."""
        try:
            # Create a 6-second video with a color background and text
            # 720x1280 (9:16 aspect ratio), 6 seconds, 30fps
            command = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', 'color=c=blue:s=720x1280:d=6:r=30',
                '-vf', 'drawtext=text=\'MOCK VIDEO\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
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
            print(f"FFmpeg test video creation failed: {e}")
            return False

    def _create_placeholder_video(self, output_path: str) -> bool:
        """Create a placeholder file when FFmpeg is not available."""
        try:
            # Create a minimal MP4 file header (won't be playable but valid for testing)
            with open(output_path, 'wb') as f:
                # Write minimal MP4 header
                f.write(b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41')
                f.write(b'\x00' * 1024 * 100)  # 100KB placeholder

            print("⚠️  Created placeholder video (FFmpeg not available for real test video)")
            return True

        except Exception as e:
            print(f"Placeholder creation failed: {e}")
            return False

    def text_to_video(self, prompt: str, aspect_ratio: str = "9:16") -> str:
        """Mock text to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=None)

    def image_to_video(self, prompt: str, image_url: str, aspect_ratio: str = "9:16") -> str:
        """Mock image to video generation."""
        return self.generate_video(prompt, aspect_ratio, image_url=image_url)
