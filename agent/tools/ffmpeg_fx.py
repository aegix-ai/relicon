"""
FFmpeg Video Assembly Tool
Final video compilation with transitions, effects, and audio mixing
"""
import json
import os
import subprocess
from typing import Dict, Any, List
from pathlib import Path
import tempfile

from config.settings import settings, logger


def run(assembly_data: str) -> str:
    """
    Assemble final video using FFmpeg with comprehensive filter_complex
    
    This is the critical final step that compiles all assets into the finished video.
    Creates a single, optimized FFmpeg command with complex filters for professional output.
    
    Args:
        assembly_data: JSON string containing complete timeline and assets
        
    Returns:
        JSON string with final video information and rendering details
    """
    try:
        # Parse assembly data
        if isinstance(assembly_data, str):
            try:
                assembly_info = json.loads(assembly_data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in assembly data")
                raise ValueError("Assembly data must be valid JSON")
        else:
            assembly_info = assembly_data
            
        logger.info("Starting FFmpeg video assembly")
        
        # Extract components
        timeline = assembly_info.get('timeline', [])
        audio_plan = assembly_info.get('audio_plan', {})
        footage_segments = assembly_info.get('footage_segments', [])
        audio_segments = assembly_info.get('audio_segments', [])
        
        if not timeline:
            raise ValueError("No timeline found for video assembly")
        
        # Create output directory
        output_dir = Path("outputs/final")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique output filename
        import hashlib
        timeline_hash = hashlib.md5(str(timeline).encode()).hexdigest()[:8]
        output_filename = f"reelforge_ad_{timeline_hash}.mp4"
        output_path = output_dir / output_filename
        
        # Build comprehensive FFmpeg command
        ffmpeg_command = _build_ffmpeg_command(
            timeline=timeline,
            audio_plan=audio_plan,
            footage_segments=footage_segments,
            audio_segments=audio_segments,
            output_path=str(output_path)
        )
        
        # Execute FFmpeg rendering
        rendering_result = _execute_ffmpeg_render(ffmpeg_command, str(output_path))
        
        if not rendering_result["success"]:
            raise Exception(f"FFmpeg rendering failed: {rendering_result['error']}")
        
        # Validate output video
        video_info = _validate_output_video(str(output_path))
        
        # Create comprehensive results
        assembly_results = {
            "success": True,
            "output_file": str(output_path),
            "output_filename": output_filename,
            "video_info": video_info,
            "rendering_stats": rendering_result["stats"],
            "ffmpeg_command": ffmpeg_command["description"],  # Don't expose raw command for security
            "processing_summary": {
                "video_segments": len([item for item in timeline if item.get('type') == 'video']),
                "audio_segments": len(audio_segments),
                "transitions": len([item for item in timeline if item.get('type') == 'transition']),
                "total_duration": video_info["duration"],
                "resolution": video_info["resolution"]
            },
            "quality_metrics": _analyze_video_quality(str(output_path)),
            "generated_by": "ReelForge FFmpeg Assembler",
            "version": "1.0"
        }
        
        logger.info("Video assembly completed successfully",
                   output_file=output_filename,
                   duration=video_info["duration"],
                   resolution=video_info["resolution"])
        
        return json.dumps(assembly_results, indent=2)
        
    except Exception as e:
        error_msg = f"Video assembly failed: {str(e)}"
        logger.error("FFmpeg assembly error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "success": False,
            "error": error_msg,
            "output_file": None,
            "generated_by": "ReelForge FFmpeg Assembler (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def _build_ffmpeg_command(timeline: List[Dict[str, Any]], audio_plan: Dict[str, Any], 
                         footage_segments: List[Dict[str, Any]], audio_segments: List[Dict[str, Any]], 
                         output_path: str) -> Dict[str, Any]:
    """Build comprehensive FFmpeg command with complex filters"""
    
    # Collect all input files
    input_files = []
    filter_parts = []
    
    # Video inputs
    video_segments = [item for item in timeline if item.get('type') == 'video']
    for i, segment in enumerate(video_segments):
        # Find corresponding footage file
        footage_file = None
        for footage in footage_segments:
            if footage.get('scene_id') == segment.get('scene_id'):
                footage_file = footage.get('file_path')
                break
        
        if footage_file and os.path.exists(footage_file):
            input_files.append(footage_file)
        else:
            logger.warning(f"Missing footage for scene {segment.get('scene_id')}")
            # Create placeholder
            placeholder_file = _create_placeholder_video(segment.get('duration', 5))
            input_files.append(placeholder_file)
    
    # Audio inputs
    for audio_segment in audio_segments:
        audio_file = audio_segment.get('file_path')
        if audio_file and os.path.exists(audio_file):
            input_files.append(audio_file)
    
    # Background music input
    background_music = audio_plan.get('background_music', {})
    if background_music.get('enabled'):
        music_file = _get_background_music_file(background_music.get('style', 'corporate_upbeat'))
        if music_file:
            input_files.append(music_file)
    
    logger.info(f"Building FFmpeg command with {len(input_files)} input files")
    
    # Build filter_complex
    filter_complex = _build_filter_complex(timeline, audio_plan, len(video_segments), len(audio_segments))
    
    # Construct full FFmpeg command
    cmd_parts = [settings.ffmpeg_binary_path]
    
    # Add input files
    for input_file in input_files:
        cmd_parts.extend(["-i", input_file])
    
    # Add filter_complex
    if filter_complex:
        cmd_parts.extend(["-filter_complex", filter_complex])
    
    # Output settings
    cmd_parts.extend([
        "-map", "[final_video]",  # Map final video output
        "-map", "[final_audio]",  # Map final audio output
        "-c:v", "libx264",  # Video codec
        "-preset", "medium",  # Encoding speed vs quality balance
        "-crf", "23",  # Quality setting (lower = better quality)
        "-c:a", "aac",  # Audio codec
        "-b:a", "128k",  # Audio bitrate
        "-movflags", "+faststart",  # Optimize for streaming
        "-y",  # Overwrite output file
        output_path
    ])
    
    return {
        "command": cmd_parts,
        "input_files": input_files,
        "filter_complex": filter_complex,
        "description": f"FFmpeg assembly with {len(video_segments)} video segments and complex filtering"
    }


def _build_filter_complex(timeline: List[Dict[str, Any]], audio_plan: Dict[str, Any], 
                         video_count: int, audio_count: int) -> str:
    """Build the complex filter string for FFmpeg"""
    
    filter_parts = []
    video_segments = [item for item in timeline if item.get('type') == 'video']
    transitions = [item for item in timeline if item.get('type') == 'transition']
    
    # Process video segments
    current_video_label = None
    for i, segment in enumerate(video_segments):
        duration = segment.get('duration', 5)
        
        # Trim and scale video segment
        input_label = f"{i}:v"
        segment_label = f"v{i}"
        
        filter_parts.append(
            f"[{input_label}]trim=0:{duration},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black[{segment_label}]"
        )
        
        # Apply transitions
        if i > 0 and len(transitions) > i - 1:
            transition = transitions[i - 1]
            transition_type = transition.get('name', 'fade')
            transition_duration = transition.get('duration', 0.5)
            
            # Apply transition between previous and current segment
            prev_label = current_video_label or f"v{i-1}"
            transition_label = f"vt{i}"
            
            if transition_type == 'crossfade':
                filter_parts.append(
                    f"[{prev_label}][{segment_label}]xfade=transition=fade:duration={transition_duration}:offset=0[{transition_label}]"
                )
            elif transition_type == 'wipe':
                filter_parts.append(
                    f"[{prev_label}][{segment_label}]xfade=transition=wipeleft:duration={transition_duration}:offset=0[{transition_label}]"
                )
            elif transition_type == 'dissolve':
                filter_parts.append(
                    f"[{prev_label}][{segment_label}]xfade=transition=dissolve:duration={transition_duration}:offset=0[{transition_label}]"
                )
            else:
                # Default fade transition
                filter_parts.append(
                    f"[{prev_label}][{segment_label}]xfade=transition=fade:duration={transition_duration}:offset=0[{transition_label}]"
                )
            
            current_video_label = transition_label
        else:
            current_video_label = segment_label
    
    # Final video output
    if current_video_label:
        filter_parts.append(f"[{current_video_label}]format=yuv420p[final_video]")
    else:
        # Fallback if no video processing
        filter_parts.append("[0:v]scale=1920:1080[final_video]")
    
    # Process audio
    audio_filter_parts = []
    
    # Collect voiceover audio segments
    voiceover_inputs = []
    for i in range(audio_count):
        voiceover_inputs.append(f"[{video_count + i}:a]")
    
    if voiceover_inputs:
        # Concatenate voiceover segments
        voiceover_concat = f"{''.join(voiceover_inputs)}concat=n={len(voiceover_inputs)}:v=0:a=1[voiceover]"
        audio_filter_parts.append(voiceover_concat)
        
        # Handle background music
        background_music = audio_plan.get('background_music', {})
        if background_music.get('enabled') and video_count + audio_count < len(timeline):
            music_input = f"[{video_count + audio_count}:a]"
            music_volume = background_music.get('volume_level', 0.3)
            
            # Mix voiceover with background music
            audio_filter_parts.append(
                f"[voiceover]{music_input}amix=inputs=2:weights=1 {music_volume}:normalize=0[final_audio]"
            )
        else:
            # Just use voiceover
            audio_filter_parts.append("[voiceover]anull[final_audio]")
    else:
        # No audio, create silent track
        audio_filter_parts.append("anullsrc=channel_layout=stereo:sample_rate=44100[final_audio]")
    
    # Combine video and audio filters
    all_filters = filter_parts + audio_filter_parts
    
    return ';'.join(all_filters)


def _execute_ffmpeg_render(ffmpeg_command: Dict[str, Any], output_path: str) -> Dict[str, Any]:
    """Execute the FFmpeg rendering command"""
    try:
        cmd = ffmpeg_command["command"]
        
        logger.info("Starting FFmpeg rendering", output=output_path)
        
        # Execute with timeout and progress tracking
        start_time = time.time()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=settings.max_job_duration  # Prevent runaway processes
        )
        
        end_time = time.time()
        render_duration = end_time - start_time
        
        if result.returncode != 0:
            logger.error("FFmpeg rendering failed", 
                        return_code=result.returncode,
                        stderr=result.stderr)
            return {
                "success": False,
                "error": f"FFmpeg failed with code {result.returncode}: {result.stderr}",
                "stats": {"render_duration": render_duration}
            }
        
        # Check if output file was created
        if not os.path.exists(output_path):
            return {
                "success": False,
                "error": "Output file was not created",
                "stats": {"render_duration": render_duration}
            }
        
        # Check file size
        file_size = os.path.getsize(output_path)
        if file_size < 10000:  # Less than 10KB
            return {
                "success": False,
                "error": "Output file is too small",
                "stats": {"render_duration": render_duration, "file_size": file_size}
            }
        
        logger.info("FFmpeg rendering completed successfully",
                   render_duration=render_duration,
                   file_size_mb=file_size / (1024 * 1024))
        
        return {
            "success": True,
            "stats": {
                "render_duration": render_duration,
                "file_size": file_size,
                "file_size_mb": file_size / (1024 * 1024)
            }
        }
        
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg rendering timed out")
        return {
            "success": False,
            "error": "Rendering timed out",
            "stats": {"render_duration": settings.max_job_duration}
        }
    except Exception as e:
        logger.error("FFmpeg execution error", error=str(e))
        return {
            "success": False,
            "error": f"Execution error: {str(e)}",
            "stats": {}
        }


def _validate_output_video(video_path: str) -> Dict[str, Any]:
    """Validate the output video file"""
    try:
        import subprocess
        
        # Use FFprobe to get detailed video information
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            
            # Extract video and audio stream info
            video_stream = None
            audio_stream = None
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            format_info = info.get('format', {})
            
            return {
                "duration": float(format_info.get('duration', 0)),
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}" if video_stream else "unknown",
                "video_codec": video_stream.get('codec_name', 'unknown') if video_stream else None,
                "audio_codec": audio_stream.get('codec_name', 'unknown') if audio_stream else None,
                "bitrate": int(format_info.get('bit_rate', 0)),
                "file_size": int(format_info.get('size', 0)),
                "has_video": video_stream is not None,
                "has_audio": audio_stream is not None
            }
        else:
            logger.error("FFprobe validation failed", stderr=result.stderr)
            return {
                "duration": 0,
                "resolution": "unknown",
                "error": "Validation failed"
            }
            
    except Exception as e:
        logger.error("Video validation error", error=str(e))
        return {
            "duration": 0,
            "resolution": "unknown",
            "error": str(e)
        }


def _analyze_video_quality(video_path: str) -> Dict[str, Any]:
    """Analyze video quality metrics"""
    try:
        file_size = os.path.getsize(video_path)
        video_info = _validate_output_video(video_path)
        
        duration = video_info.get('duration', 0)
        bitrate = video_info.get('bitrate', 0)
        
        # Calculate quality metrics
        quality_metrics = {
            "file_size_mb": file_size / (1024 * 1024),
            "bitrate_mbps": bitrate / (1024 * 1024) if bitrate > 0 else 0,
            "duration_seconds": duration,
            "quality_score": "unknown"
        }
        
        # Simple quality scoring
        if bitrate > 5000000:  # > 5 Mbps
            quality_metrics["quality_score"] = "high"
        elif bitrate > 2000000:  # > 2 Mbps
            quality_metrics["quality_score"] = "medium"
        else:
            quality_metrics["quality_score"] = "low"
        
        return quality_metrics
        
    except Exception as e:
        logger.error("Quality analysis error", error=str(e))
        return {"error": str(e)}


def _create_placeholder_video(duration: float) -> str:
    """Create a placeholder video for missing footage"""
    try:
        temp_dir = Path("outputs/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        placeholder_path = temp_dir / f"placeholder_{int(duration)}.mp4"
        
        # Create simple colored video
        cmd = [
            settings.ffmpeg_binary_path,
            "-f", "lavfi",
            "-i", f"color=color=0x444444:size=1920x1080:duration={duration}",
            "-vf", "drawtext=text='Placeholder':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-t", str(duration),
            "-y",
            str(placeholder_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            return str(placeholder_path)
        else:
            logger.error("Failed to create placeholder video")
            return None
            
    except Exception as e:
        logger.error("Placeholder creation error", error=str(e))
        return None


def _get_background_music_file(style: str) -> str:
    """Get background music file for the specified style"""
    # Check for bundled music files
    music_dir = Path("assets/music")
    
    style_mapping = {
        "corporate_upbeat": "corporate_upbeat.mp3",
        "energetic": "energetic.mp3",
        "calm": "calm.mp3",
        "modern": "modern.mp3"
    }
    
    music_filename = style_mapping.get(style, "corporate_upbeat.mp3")
    music_path = music_dir / music_filename
    
    if music_path.exists():
        return str(music_path)
    
    # Create silent background track as fallback
    temp_dir = Path("outputs/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    silent_music_path = temp_dir / "silent_music.mp3"
    
    try:
        cmd = [
            settings.ffmpeg_binary_path,
            "-f", "lavfi",
            "-i", "anullsrc=duration=60:sample_rate=44100:channel_layout=stereo",
            "-y",
            str(silent_music_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            return str(silent_music_path)
    except Exception as e:
        logger.error("Failed to create silent music", error=str(e))
    
    return None


import time  # Add this import at the top
