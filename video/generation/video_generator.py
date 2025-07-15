"""Video generation module"""
import os
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import settings

class VideoGenerator:
    """Video generation service"""
    
    def validate_video(self, video_path: str) -> bool:
        """Validate video file"""
        if not os.path.exists(video_path):
            return False
        
        # Check file size
        if os.path.getsize(video_path) < 1024:  # Less than 1KB
            return False
        
        return True
    
    def create_video_from_segments(self, segments: List[Dict[str, Any]], output_path: str) -> bool:
        """Create video from segments"""
        try:
            if not segments:
                return False
            
            # Use first segment's audio file for simple video
            audio_file = segments[0].get("audio_file")
            if not audio_file or not os.path.exists(audio_file):
                return False
            
            duration = segments[0].get("duration", 30)
            
            # Create video with FFmpeg
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c=black:s=1920x1080:d={duration}",
                "-i", audio_file,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Video generation error: {e}")
            return False
    
    def create_simple_video(self, brand_info: Dict[str, Any], audio_files: List[str]) -> Optional[str]:
        """Create simple video with audio"""
        try:
            output_path = Path(settings.OUTPUT_DIR) / f"simple_{brand_info.get('brand_name', 'brand')}.mp4"
            
            # Create a simple black video with audio
            if audio_files and os.path.exists(audio_files[0]):
                # Get audio duration
                duration = brand_info.get("duration", 30)
                
                # Create video with FFmpeg
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c=black:s=1920x1080:d={duration}",
                    "-i", audio_files[0],
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-shortest",
                    str(output_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return str(output_path)
            
            return None
            
        except Exception as e:
            print(f"Video generation error: {e}")
            return None

# Global instance
video_generator = VideoGenerator()