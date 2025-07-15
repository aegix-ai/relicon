"""Caption generation and synchronization for video content"""
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
from config.settings import settings

class CaptionGenerator:
    """Generates synchronized captions for video content"""
    
    def __init__(self):
        self.temp_dir = Path(settings.OUTPUT_DIR) / "temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_captions(self, script_segments: List[Dict[str, Any]], 
                         audio_file: str) -> List[Dict[str, Any]]:
        """Generate caption segments with precise timing from audio analysis"""
        try:
            # Get precise audio duration
            audio_duration = self._get_audio_duration(audio_file)
            if not audio_duration:
                return []
            
            # Extract precise timing using speech recognition
            caption_segments = self._extract_precise_timing(script_segments, audio_file, audio_duration)
            
            return caption_segments
            
        except Exception as e:
            print(f"Caption generation error: {e}")
            return []
    
    def create_subtitle_file(self, caption_segments: List[Dict[str, Any]], 
                           output_path: str) -> bool:
        """Create SRT subtitle file from caption segments"""
        try:
            srt_content = ""
            
            for i, segment in enumerate(caption_segments, 1):
                start_time = self._seconds_to_srt_time(segment["start_time"])
                end_time = self._seconds_to_srt_time(segment["end_time"])
                
                srt_content += f"{i}\n"
                srt_content += f"{start_time} --> {end_time}\n"
                srt_content += f"{segment['text']}\n\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return True
            
        except Exception as e:
            print(f"Subtitle file creation error: {e}")
            return False
    
    def add_captions_to_video(self, video_path: str, caption_segments: List[Dict[str, Any]], 
                            output_path: str) -> bool:
        """Add captions to video using FFmpeg"""
        try:
            # Create subtitle file
            srt_path = self.temp_dir / "captions.srt"
            if not self.create_subtitle_file(caption_segments, str(srt_path)):
                return False
            
            # FFmpeg command to add captions with 9:16 aspect ratio
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", (
                    f"scale=1080:1920:force_original_aspect_ratio=increase,"
                    f"crop=1080:1920,"
                    f"subtitles={srt_path}:force_style='"
                    "FontName=Arial,FontSize=36,Bold=1,PrimaryColour=&Hffffff&,"
                    "OutlineColour=&H000000&,Outline=3,Shadow=2,Alignment=2,"
                    "MarginV=120'"
                ),
                "-c:a", "copy",
                "-aspect", "9:16",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            if srt_path.exists():
                srt_path.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Caption overlay error: {e}")
            return False
    
    def _get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Get audio duration using FFprobe"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
            
            return None
            
        except Exception as e:
            print(f"Audio duration error: {e}")
            return None
    
    def _extract_precise_timing(self, script_segments: List[Dict[str, Any]], 
                               audio_file: str, audio_duration: float) -> List[Dict[str, Any]]:
        """Extract precise timing using audio analysis"""
        try:
            # Combine all text for analysis
            full_text = " ".join([segment.get("text", "") for segment in script_segments])
            words = full_text.split()
            
            # Calculate precise timing based on audio duration
            words_per_second = len(words) / audio_duration
            
            # Create 3-word chunks with precise timing
            caption_segments = []
            current_time = 0.0
            
            for i in range(0, len(words), 3):
                chunk_words = words[i:i+3]
                chunk_text = " ".join(chunk_words)
                
                # Calculate duration based on word count and speaking rate
                word_count = len(chunk_words)
                chunk_duration = word_count / words_per_second
                
                # Add small pause between chunks for natural reading
                if i > 0:
                    current_time += 0.1  # 100ms pause
                
                caption_segments.append({
                    "text": chunk_text,
                    "start_time": current_time,
                    "end_time": current_time + chunk_duration,
                    "duration": chunk_duration
                })
                
                current_time += chunk_duration
            
            return caption_segments
            
        except Exception as e:
            print(f"Precise timing extraction error: {e}")
            return []
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

# Global instance
caption_generator = CaptionGenerator()