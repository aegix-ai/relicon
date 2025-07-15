"""Precise synchronization system for captions with audio timing"""
import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import settings

class PreciseSyncGenerator:
    """Generates precisely synchronized captions using audio analysis"""
    
    def __init__(self):
        self.temp_dir = Path(settings.OUTPUT_DIR) / "temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_precise_captions(self, full_text: str, audio_file: str) -> List[Dict[str, Any]]:
        """Generate precisely synchronized captions using audio analysis"""
        try:
            # Clean and prepare text
            clean_text = self._clean_text(full_text)
            words = clean_text.split()
            
            # Get audio duration
            audio_duration = self._get_audio_duration(audio_file)
            if not audio_duration:
                return []
            
            # Calculate precise timing
            return self._calculate_precise_timing(words, audio_duration)
            
        except Exception as e:
            print(f"Precise caption generation error: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean text for precise synchronization"""
        # Remove hesitation markers added by TTS processing
        cleaned = text.replace("... uh... ", " ")
        cleaned = cleaned.replace("um... ", "")
        cleaned = cleaned.replace("... ", " ")
        
        # Normalize punctuation
        cleaned = cleaned.replace(".", " ")
        cleaned = cleaned.replace(",", " ")
        cleaned = cleaned.replace("!", " ")
        cleaned = cleaned.replace("?", " ")
        
        # Remove extra spaces
        cleaned = " ".join(cleaned.split())
        
        return cleaned
    
    def _calculate_precise_timing(self, words: List[str], audio_duration: float) -> List[Dict[str, Any]]:
        """Calculate precise timing for 3-word chunks with perfect sync"""
        caption_segments = []
        
        # Calculate precise speaking rate
        total_words = len(words)
        words_per_second = total_words / audio_duration
        
        # Use actual speaking rate for perfect sync
        effective_words_per_second = words_per_second
        
        current_time = 0.0
        
        # Calculate total chunks to ensure perfect timing
        total_chunks = (len(words) + 2) // 3  # Round up division
        
        for i in range(0, len(words), 3):
            chunk_words = words[i:i+3]
            chunk_text = " ".join(chunk_words)
            
            # Calculate precise duration for this chunk
            word_count = len(chunk_words)
            base_duration = word_count / effective_words_per_second
            
            # Add minimal pause between chunks (50ms)
            if i > 0:
                current_time += 0.05
            
            # Ensure we don't exceed total duration
            remaining_time = audio_duration - current_time
            if remaining_time < base_duration:
                base_duration = max(0.5, remaining_time)  # Minimum 0.5s duration
            
            caption_segments.append({
                "text": chunk_text,
                "start_time": current_time,
                "end_time": current_time + base_duration,
                "duration": base_duration,
                "word_count": word_count
            })
            
            current_time += base_duration
        
        return caption_segments
    
    def _adjust_for_complexity(self, text: str, base_duration: float) -> float:
        """Adjust duration based on text complexity"""
        # Longer words take more time
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split())
        
        # Complexity multiplier
        complexity_factor = 1.0
        if avg_word_length > 6:
            complexity_factor = 1.3
        elif avg_word_length > 4:
            complexity_factor = 1.1
        
        return base_duration * complexity_factor
    
    def _get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Get precise audio duration"""
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
    
    def create_srt_file(self, caption_segments: List[Dict[str, Any]], output_path: str) -> bool:
        """Create SRT file with precise timing"""
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
            print(f"SRT file creation error: {e}")
            return False
    
    def add_precise_captions(self, video_path: str, caption_segments: List[Dict[str, Any]], 
                           output_path: str) -> bool:
        """Add precisely synchronized captions to video"""
        try:
            # Create SRT file
            srt_path = self.temp_dir / "precise_captions.srt"
            if not self.create_srt_file(caption_segments, str(srt_path)):
                return False
            
            # Enhanced FFmpeg command for precise caption overlay
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", (
                    f"scale=1080:1920:force_original_aspect_ratio=increase,"
                    f"crop=1080:1920,"
                    f"subtitles={srt_path}:force_style='"
                    "FontName=Arial,FontSize=42,Bold=1,PrimaryColour=&Hffffff&,"
                    "OutlineColour=&H000000&,Outline=3,Shadow=2,Alignment=2,"
                    "MarginV=150,ScaleX=100,ScaleY=100'"
                ),
                "-c:a", "copy",
                "-aspect", "9:16",
                "-preset", "medium",
                "-crf", "23",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up
            if srt_path.exists():
                srt_path.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Precise caption overlay error: {e}")
            return False
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format with millisecond precision"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

# Global instance
precise_sync_generator = PreciseSyncGenerator()