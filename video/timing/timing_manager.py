"""Timing manager for perfect video, audio, and caption synchronization"""
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from config.settings import settings

class TimingManager:
    """Manages perfect timing alignment for all video components"""
    
    def __init__(self):
        self.temp_dir = Path(settings.OUTPUT_DIR) / "temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def calculate_perfect_timing(self, target_duration: float, script_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate perfect timing for all components"""
        try:
            # Ensure script segments fit exactly within target duration
            adjusted_segments = self._adjust_script_timing(script_segments, target_duration)
            
            # Calculate precise caption timing
            caption_timing = self._calculate_caption_timing(adjusted_segments)
            
            # Calculate scene timing
            scene_timing = self._calculate_scene_timing(adjusted_segments)
            
            return {
                "success": True,
                "target_duration": target_duration,
                "adjusted_segments": adjusted_segments,
                "caption_timing": caption_timing,
                "scene_timing": scene_timing,
                "total_duration": sum(seg["duration"] for seg in adjusted_segments)
            }
            
        except Exception as e:
            print(f"Timing calculation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _adjust_script_timing(self, script_segments: List[Dict[str, Any]], target_duration: float) -> List[Dict[str, Any]]:
        """Adjust script segments to fit exactly within target duration"""
        if not script_segments:
            return []
        
        # Calculate current total duration
        current_duration = sum(seg.get("duration", 10) for seg in script_segments)
        
        # Calculate adjustment ratio
        adjustment_ratio = target_duration / current_duration
        
        adjusted_segments = []
        for segment in script_segments:
            original_duration = segment.get("duration", 10)
            adjusted_duration = original_duration * adjustment_ratio
            
            adjusted_segments.append({
                "text": segment.get("text", ""),
                "duration": adjusted_duration,
                "original_duration": original_duration,
                "adjustment_ratio": adjustment_ratio
            })
        
        return adjusted_segments
    
    def _calculate_caption_timing(self, script_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate precise caption timing with 3-word chunks"""
        caption_segments = []
        current_time = 0.0
        
        for segment in script_segments:
            text = segment.get("text", "")
            segment_duration = segment.get("duration", 5)
            
            # Split into 3-word chunks
            words = text.split()
            chunks = []
            
            for i in range(0, len(words), 3):
                chunk_words = words[i:i+3]
                chunks.append(" ".join(chunk_words))
            
            if chunks:
                # Distribute time evenly across chunks
                chunk_duration = segment_duration / len(chunks)
                
                for chunk in chunks:
                    if chunk.strip():
                        caption_segments.append({
                            "text": chunk.strip(),
                            "start_time": current_time,
                            "end_time": current_time + chunk_duration,
                            "duration": chunk_duration
                        })
                        current_time += chunk_duration
            else:
                current_time += segment_duration
        
        return caption_segments
    
    def _calculate_scene_timing(self, script_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate scene timing to match script segments"""
        scene_segments = []
        current_time = 0.0
        
        for i, segment in enumerate(script_segments):
            duration = segment.get("duration", 5)
            
            scene_segments.append({
                "scene_index": i,
                "start_time": current_time,
                "end_time": current_time + duration,
                "duration": duration,
                "text": segment.get("text", "")
            })
            
            current_time += duration
        
        return scene_segments
    
    def create_synchronized_audio(self, text: str, target_duration: float, audio_processor) -> Optional[str]:
        """Create audio that fits exactly within target duration"""
        try:
            # Generate audio with timing constraints
            audio_file = audio_processor.create_human_voiceover(text, "premium")
            
            if audio_file:
                # Verify and adjust audio duration
                actual_duration = self._get_audio_duration(audio_file)
                
                if actual_duration and abs(actual_duration - target_duration) > 0.5:
                    # Adjust audio speed to match target duration
                    adjusted_audio = self._adjust_audio_speed(audio_file, actual_duration, target_duration)
                    return adjusted_audio or audio_file
                
                return audio_file
            
            return None
            
        except Exception as e:
            print(f"Synchronized audio creation error: {e}")
            return None
    
    def _adjust_audio_speed(self, audio_file: str, current_duration: float, target_duration: float) -> Optional[str]:
        """Adjust audio speed to match target duration"""
        try:
            speed_factor = current_duration / target_duration
            
            # Limit speed adjustment to reasonable range
            if speed_factor < 0.7 or speed_factor > 1.3:
                print(f"Speed adjustment too extreme: {speed_factor}")
                return None
            
            output_file = self.temp_dir / f"adjusted_audio_{int(time.time())}.mp3"
            
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_file,
                "-af", f"atempo={speed_factor}",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return str(output_file)
            
            return None
            
        except Exception as e:
            print(f"Audio speed adjustment error: {e}")
            return None
    
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
            print(f"Audio duration check error: {e}")
            return None
    
    def verify_timing_alignment(self, video_file: str, audio_file: str, caption_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that all components are perfectly aligned"""
        try:
            video_duration = self._get_video_duration(video_file)
            audio_duration = self._get_audio_duration(audio_file)
            
            caption_end_time = max(seg["end_time"] for seg in caption_segments) if caption_segments else 0
            
            timing_info = {
                "video_duration": video_duration,
                "audio_duration": audio_duration,
                "caption_end_time": caption_end_time,
                "alignment_status": "perfect" if self._is_perfectly_aligned(video_duration, audio_duration, caption_end_time) else "misaligned"
            }
            
            return timing_info
            
        except Exception as e:
            print(f"Timing verification error: {e}")
            return {"alignment_status": "error", "error": str(e)}
    
    def _get_video_duration(self, video_file: str) -> Optional[float]:
        """Get video duration"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
            
            return None
            
        except Exception as e:
            print(f"Video duration check error: {e}")
            return None
    
    def _is_perfectly_aligned(self, video_duration: Optional[float], audio_duration: Optional[float], caption_end_time: float) -> bool:
        """Check if all components are perfectly aligned"""
        if not video_duration or not audio_duration:
            return False
        
        # Allow 0.1 second tolerance
        tolerance = 0.1
        
        return (
            abs(video_duration - audio_duration) <= tolerance and
            abs(audio_duration - caption_end_time) <= tolerance
        )

# Global instance
timing_manager = TimingManager()