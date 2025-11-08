"""
  Video assembly service for combining video and audio components.
"""

import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
from core.logger import assembly_logger


class AssemblyService:
    """Service for assembling final video from components."""
    
    def __init__(self):
        pass
    
    def assemble_final_video(self, video_files: List[str], audio_file: str,
                           output_path: str, target_duration: float = 15.0) -> bool:
        """
        Assemble final video from video scenes and audio track.
        
        Args:
            video_files: List of video file paths in order
            audio_file: Path to audio track file
            output_path: Path to save final assembled video
            target_duration: Target duration in seconds
            
        Returns:
            True if assembly successful, False otherwise
        """
        assembly_logger.assembly_timing_debug(
            job_id="current", 
            target_duration_s=target_duration, 
            actual_duration_s=0.0, 
            adjustment_applied=False
        )
        try:
            if not video_files:
                print("No video files provided for assembly")
                return False
            
            if not os.path.exists(audio_file):
                print(f"Audio file not found: {audio_file}")
                return False
            
            # Validate video files exist
            valid_videos = []
            for video_file in video_files:
                if os.path.exists(video_file):
                    valid_videos.append(video_file)
                else:
                    print(f"Warning: Video file not found: {video_file}")
            
            if not valid_videos:
                print("No valid video files found")
                return False
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Step 1: Concatenate video files
                if len(valid_videos) > 1:
                    concat_video_path = os.path.join(temp_dir, "concatenated_video.mp4")
                    if not self._concatenate_videos(valid_videos, concat_video_path):
                        return False
                else:
                    concat_video_path = valid_videos[0]
                
                # Step 2: Adjust video duration to match target
                duration_adjusted_path = os.path.join(temp_dir, "duration_adjusted.mp4")
                if not self._adjust_video_duration(concat_video_path, duration_adjusted_path, target_duration):
                    return False
                
                # Step 3: Combine with audio
                if not self._combine_video_audio(duration_adjusted_path, audio_file, output_path, target_duration):
                    return False
                
                print(f"Final video assembled: {output_path}")
                return True
                
        except Exception as e:
            print(f"Video assembly failed: {e}")
            return False
    
    def _concatenate_videos(self, video_files: List[str], output_path: str) -> bool:
        """Concatenate multiple video files into one."""
        try:
            # Create filter complex for concatenation with scaling
            filter_parts = []
            input_files = []
            
            for i, video_file in enumerate(video_files):
                input_files.extend(['-i', video_file])
                # Scale all videos to cost-optimized 720p format
                filter_parts.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1[v{i}]")
            
            # Concatenate all scaled videos
            video_inputs = ''.join([f"[v{i}]" for i in range(len(video_files))])
            concat_filter = f"{video_inputs}concat=n={len(video_files)}:v=1:a=0[outv]"
            
            # Combine filters
            full_filter = ';'.join(filter_parts) + ';' + concat_filter
            
            cmd = [
                'ffmpeg', '-y'
            ] + input_files + [
                '-filter_complex', full_filter,
                '-map', '[outv]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Videos concatenated successfully")
                return True
            else:
                print(f"Video concatenation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Video concatenation error: {e}")
            return False
    
    def _adjust_video_duration(self, input_path: str, output_path: str, target_duration: float) -> bool:
        """Adjust video duration to exact target length."""
        try:
            # Get current video duration
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', input_path
            ]
            
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode != 0:
                print(f"Failed to probe video duration")
                return False
            
            import json
            probe_data = json.loads(probe_result.stdout)
            current_duration = float(probe_data['format']['duration'])
            
            print(f"Current duration: {current_duration:.2f}s, Target: {target_duration:.2f}s")
            
            # Calculate speed adjustment
            if abs(current_duration - target_duration) < 0.1:
                # Duration is close enough, just copy
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            
            speed_factor = current_duration / target_duration
            
            # Apply speed adjustment
            cmd = [
                'ffmpeg', '-y', '-i', input_path,
                '-filter:v', f'setpts={speed_factor}*PTS',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-t', str(target_duration),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Video duration adjusted to {target_duration}s")
                return True
            else:
                print(f"Duration adjustment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Duration adjustment error: {e}")
            return False
    
    def _combine_video_audio(self, video_path: str, audio_path: str, output_path: str, duration: float) -> bool:
        """Combine video and audio into final output."""
        try:
            # First, let's verify the audio file has proper volume
            probe_cmd = ['ffmpeg', '-i', audio_path, '-af', 'volumedetect', '-f', 'null', '-']
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            volume_info = probe_result.stderr.split('volumedetect')[1] if 'volumedetect' in probe_result.stderr else 'No volume data'
            print(f"🔍 DEBUG: Pre-assembly audio levels: {volume_info}")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '320k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(duration),
                '-shortest',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Video and audio combined successfully")
                return True
            else:
                print(f"Video-audio combination failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Video-audio combination error: {e}")
            return False
    
    def validate_video_output(self, video_path: str, expected_duration: float = 15.0) -> Dict[str, Any]:
        """
        Validate the final video output.
        
        Args:
            video_path: Path to video file to validate
            expected_duration: Expected duration in seconds
            
        Returns:
            Dictionary with validation results
        """
        try:
            if not os.path.exists(video_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            # Get video info
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {'valid': False, 'error': 'Failed to probe video'}
            
            import json
            data = json.loads(result.stdout)
            
            # Extract video info
            format_info = data.get('format', {})
            streams = data.get('streams', [])
            
            video_streams = [s for s in streams if s.get('codec_type') == 'video']
            audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
            
            duration = float(format_info.get('duration', 0))
            file_size = int(format_info.get('size', 0))
            
            # Validation results
            validation = {
                'valid': True,
                'duration': duration,
                'expected_duration': expected_duration,
                'duration_diff': abs(duration - expected_duration),
                'file_size': file_size,
                'has_video': len(video_streams) > 0,
                'has_audio': len(audio_streams) > 0,
                'video_codec': video_streams[0].get('codec_name') if video_streams else None,
                'audio_codec': audio_streams[0].get('codec_name') if audio_streams else None,
                'resolution': None,
                'aspect_ratio': None
            }
            
            # Get resolution info
            if video_streams:
                width = video_streams[0].get('width')
                height = video_streams[0].get('height')
                if width and height:
                    validation['resolution'] = f"{width}x{height}"
                    validation['aspect_ratio'] = f"{width}:{height}"
            
            # Check critical validations
            issues = []
            if not validation['has_video']:
                issues.append('No video stream found')
            if not validation['has_audio']:
                issues.append('No audio stream found')
            if validation['duration_diff'] > 1.0:
                issues.append(f'Duration off by {validation["duration_diff"]:.1f}s')
            if file_size < 1000000:  # Less than 1MB
                issues.append('File size suspiciously small')
            
            if issues:
                validation['valid'] = False
                validation['issues'] = issues
            
            return validation
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
