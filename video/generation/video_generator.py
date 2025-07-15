"""
Core video generation functionality
Handles video creation, processing, and assembly
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from config.settings import settings

class VideoGenerator:
    """Core video generation functionality"""
    
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR
        self.output_dir = settings.OUTPUT_DIR
        self.assets_dir = settings.ASSETS_DIR
    
    def create_video_from_segments(self, segments: List[Dict[str, Any]], output_file: str, 
                                 progress_callback: Optional[Callable] = None) -> bool:
        """
        Create video from multiple segments with audio and visual components
        
        Args:
            segments: List of segment dictionaries with audio and video info
            output_file: Path to output video file
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback(10, "Starting video assembly...")
            
            # Create temporary directory for this job
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Process each segment
                segment_files = []
                for i, segment in enumerate(segments):
                    if progress_callback:
                        progress = 20 + (i * 50 // len(segments))
                        progress_callback(progress, f"Processing segment {i+1}/{len(segments)}")
                    
                    segment_file = self._create_segment_video(segment, temp_path, i)
                    if segment_file:
                        segment_files.append(segment_file)
                
                if not segment_files:
                    print("No valid segments created")
                    return False
                
                if progress_callback:
                    progress_callback(80, "Combining segments...")
                
                # Combine all segments
                success = self._combine_segments(segment_files, output_file)
                
                if progress_callback:
                    progress_callback(100, "Video generation complete!")
                
                return success
                
        except Exception as e:
            print(f"Error creating video: {e}")
            return False
    
    def _create_segment_video(self, segment: Dict[str, Any], temp_path: Path, index: int) -> Optional[str]:
        """Create a single video segment"""
        try:
            # Extract segment information
            audio_file = segment.get('audio_file')
            duration = segment.get('duration', 5)
            visual_type = segment.get('visual_type', 'color')
            
            if not audio_file or not os.path.exists(audio_file):
                print(f"Audio file not found for segment {index}: {audio_file}")
                return None
            
            # Create video file path
            segment_file = temp_path / f"segment_{index}.mp4"
            
            # Create video based on visual type
            if visual_type == 'luma_video' and segment.get('luma_video_file'):
                # Use Luma-generated video with audio overlay
                success = self._create_luma_segment(
                    segment['luma_video_file'], 
                    audio_file, 
                    str(segment_file), 
                    duration
                )
            else:
                # Create simple colored background video with audio
                success = self._create_simple_segment(
                    audio_file, 
                    str(segment_file), 
                    duration,
                    segment.get('background_color', '#1a1a2e')
                )
            
            return str(segment_file) if success else None
            
        except Exception as e:
            print(f"Error creating segment {index}: {e}")
            return None
    
    def _create_luma_segment(self, video_file: str, audio_file: str, 
                           output_file: str, duration: float) -> bool:
        """Create segment using Luma video with audio overlay"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-t', str(duration),
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating Luma segment: {e}")
            return False
    
    def _create_simple_segment(self, audio_file: str, output_file: str, 
                             duration: float, background_color: str = '#1a1a2e') -> bool:
        """Create simple segment with colored background and audio"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={background_color}:s=1920x1080:d={duration}',
                '-i', audio_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-t', str(duration),
                '-shortest',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating simple segment: {e}")
            return False
    
    def _combine_segments(self, segment_files: List[str], output_file: str) -> bool:
        """Combine multiple video segments into final video"""
        try:
            if len(segment_files) == 1:
                # Single segment, just copy
                shutil.copy2(segment_files[0], output_file)
                return True
            
            # Create file list for ffmpeg
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for segment_file in segment_files:
                    f.write(f"file '{segment_file}'\n")
                file_list = f.name
            
            try:
                # Combine segments
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', file_list,
                    '-c', 'copy',
                    output_file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
            finally:
                os.unlink(file_list)
                
        except Exception as e:
            print(f"Error combining segments: {e}")
            return False
    
    def enhance_audio(self, input_file: str, output_file: str) -> bool:
        """Enhance audio with volume boost and energy processing"""
        try:
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-af', 'volume=10dB,compand=attacks=0.3:decays=0.8:points=-80/-900|-45/-15|-27/-9:gain=5',
                '-c:a', 'libmp3lame', '-b:a', '320k',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Fall back to simple volume boost
                simple_cmd = [
                    'ffmpeg', '-y', '-i', input_file,
                    '-af', 'volume=8dB',
                    output_file
                ]
                result = subprocess.run(simple_cmd, capture_output=True)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error enhancing audio: {e}")
            return False
    
    def validate_video(self, video_file: str) -> bool:
        """Validate that video file is properly created"""
        try:
            if not os.path.exists(video_file):
                return False
            
            # Check if file has content
            if os.path.getsize(video_file) == 0:
                return False
            
            # Use ffprobe to check video properties
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error validating video: {e}")
            return False

# Global video generator instance
video_generator = VideoGenerator()