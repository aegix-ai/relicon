"""
FFmpeg Video Assembly Tool
Final video compilation with transitions, effects, and audio mixing
"""
import json
import os
import subprocess
import tempfile
from typing import List, Dict, Any

class FFmpegAssemblyTool:
    def __init__(self):
        self.ensure_ffmpeg()
    
    def ensure_ffmpeg(self):
        """Ensure FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: FFmpeg not found. Installing...")
            try:
                subprocess.run(['apt', 'update'], capture_output=True)
                subprocess.run(['apt', 'install', '-y', 'ffmpeg'], capture_output=True)
            except:
                print("Could not install FFmpeg automatically")
    
    def run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            timeline = data.get('timeline', {})
            audio = data.get('audio', {})
            footage = data.get('footage', {})
            script = data.get('script', {})
            concept = data.get('concept', {})
            job_id = data.get('job_id', 'unknown')
            
            # Ensure assets directory exists
            os.makedirs("assets", exist_ok=True)
            
            output_file = f"assets/{job_id}_final.mp4"
            
            # Extract key information
            segments = script.get('segments', [])
            duration = script.get('total_duration', 30)
            audio_files = audio.get('audio_files', [])
            
            # Create actual video
            success = self._create_video_with_content(
                segments=segments,
                audio_files=audio_files,
                output_file=output_file,
                job_id=job_id,
                duration=duration,
                concept=concept
            )
            
            if success:
                return json.dumps({
                    "video_url": f"/assets/{job_id}_final.mp4",
                    "output_file": output_file,
                    "duration": duration,
                    "resolution": "1080x1920",  # Vertical for mobile
                    "format": "mp4",
                    "audio_included": len(audio_files) > 0,
                    "segments": len(segments),
                    "status": "success"
                })
            else:
                return json.dumps({
                    "error": "Video assembly failed",
                    "status": "failed"
                })
            
        except Exception as e:
            return json.dumps({
                "error": f"FFmpeg assembly failed: {str(e)}",
                "status": "failed"
            })
    
    def _create_video_with_content(self, segments: List[Dict], audio_files: List[str], 
                                 output_file: str, job_id: str, duration: int, concept: Dict) -> bool:
        """Create actual video content using FFmpeg"""
        try:
            # Create text-based video segments first
            video_parts = []
            
            for i, segment in enumerate(segments):
                segment_file = f"assets/{job_id}_segment_{i}.mp4"
                
                # Create visual segment
                if self._create_text_video_segment(
                    text=segment.get('voiceover', ''),
                    visual_hint=segment.get('visual_hint', ''),
                    duration=segment.get('duration', 5),
                    output_file=segment_file,
                    energy=segment.get('energy_level', 'medium'),
                    segment_num=i
                ):
                    video_parts.append(segment_file)
            
            if not video_parts:
                print("No video segments created")
                return False
            
            # Combine video segments
            if not self._combine_video_segments(video_parts, f"assets/{job_id}_video.mp4"):
                return False
            
            # Add audio if available
            if audio_files and os.path.exists(audio_files[0]):
                return self._add_audio_to_video(
                    video_file=f"assets/{job_id}_video.mp4",
                    audio_files=audio_files,
                    output_file=output_file
                )
            else:
                # Just copy the video file as final output
                try:
                    subprocess.run([
                        'cp', f"assets/{job_id}_video.mp4", output_file
                    ], check=True, capture_output=True)
                    return True
                except:
                    return False
                    
        except Exception as e:
            print(f"Video creation error: {str(e)}")
            return False
    
    def _create_text_video_segment(self, text: str, visual_hint: str, duration: float, 
                                 output_file: str, energy: str, segment_num: int) -> bool:
        """Create a video segment with text overlay and background"""
        try:
            # Choose background color based on energy level
            bg_colors = {
                'high': '#FF6B6B',    # Energetic red
                'medium': '#4ECDC4',  # Professional teal  
                'low': '#45B7D1'      # Calm blue
            }
            bg_color = bg_colors.get(energy, '#4ECDC4')
            
            # Prepare text for video (limit length)
            display_text = text[:80] + "..." if len(text) > 80 else text
            safe_text = display_text.replace("'", "\\'").replace('"', '\\"')
            
            # Create video with FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color={bg_color}:size=1080x1920:duration={duration}',
                '-vf', f"drawtext=text='{safe_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=10",
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Segment creation error: {str(e)}")
            return False
    
    def _combine_video_segments(self, video_parts: List[str], output_file: str) -> bool:
        """Combine multiple video segments with transitions"""
        try:
            if len(video_parts) == 1:
                # Single segment, just copy
                subprocess.run(['cp', video_parts[0], output_file], check=True)
                return True
            
            # Create concat file for FFmpeg
            concat_file = f"assets/concat_{os.getpid()}.txt"
            with open(concat_file, 'w') as f:
                for part in video_parts:
                    if os.path.exists(part):
                        f.write(f"file '{os.path.abspath(part)}'\n")
            
            # Combine with FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            # Cleanup
            try:
                os.remove(concat_file)
            except:
                pass
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"Combine error: {str(e)}")
            return False
    
    def _add_audio_to_video(self, video_file: str, audio_files: List[str], output_file: str) -> bool:
        """Add audio track to video"""
        try:
            # Use first available audio file
            audio_file = None
            for af in audio_files:
                if os.path.exists(af):
                    audio_file = af
                    break
            
            if not audio_file:
                print("No valid audio file found")
                subprocess.run(['cp', video_file, output_file], check=True)
                return True
            
            # Combine video and audio
            cmd = [
                'ffmpeg', '-y',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Audio mixing error: {str(e)}")
            return False