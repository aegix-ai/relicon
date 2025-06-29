"""
Text-to-Speech Tool
Generates high-quality voiceover audio from script text
"""
import json
import os
import hashlib
from typing import Dict, Any, List
from pathlib import Path
import requests
from openai import OpenAI

from config.settings import settings, logger


def run(script_data: str) -> str:
    """
    Generate voiceover audio files from script segments
    
    Args:
        script_data: JSON string containing script segments with voiceover text
        
    Returns:
        JSON string with audio file information and timing data
    """
    try:
        # Parse script data
        if isinstance(script_data, str):
            try:
                script_info = json.loads(script_data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in script data")
                raise ValueError("Script data must be valid JSON")
        else:
            script_info = script_data
            
        script_segments = script_info.get('script_segments', [])
        if not script_segments:
            raise ValueError("No script segments found for TTS generation")
            
        logger.info("Starting TTS generation", segments=len(script_segments))
        
        # Initialize TTS provider
        tts_provider = _get_tts_provider()
        
        # Generate audio for each segment
        audio_results = []
        total_audio_duration = 0
        
        for i, segment in enumerate(script_segments):
            voiceover_text = segment.get('voiceover', '')
            if not voiceover_text:
                logger.warning(f"Empty voiceover text for segment {i+1}")
                continue
                
            # Generate audio file
            audio_result = _generate_audio_segment(
                tts_provider,
                voiceover_text,
                segment_id=i+1,
                tone=segment.get('emotional_tone', 'professional')
            )
            
            if audio_result:
                audio_results.append(audio_result)
                total_audio_duration += audio_result['duration']
                
                # Update original segment with audio information
                segment['audio_file'] = audio_result['file_path']
                segment['audio_duration'] = audio_result['duration']
                segment['audio_checksum'] = audio_result['checksum']
        
        # Create comprehensive TTS results
        tts_results = {
            "audio_segments": audio_results,
            "total_segments": len(audio_results),
            "total_audio_duration": total_audio_duration,
            "tts_provider": settings.tts_provider,
            "generation_settings": {
                "voice_model": _get_voice_settings()["voice"],
                "speed": _get_voice_settings()["speed"],
                "quality": "high"
            },
            "script_segments_updated": script_segments,
            "generated_by": "ReelForge TTS Generator",
            "version": "1.0"
        }
        
        logger.info("TTS generation completed",
                   segments_generated=len(audio_results),
                   total_duration=total_audio_duration)
        
        return json.dumps(tts_results, indent=2)
        
    except Exception as e:
        error_msg = f"TTS generation failed: {str(e)}"
        logger.error("TTS generation error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "error": error_msg,
            "audio_segments": [],
            "total_segments": 0,
            "total_audio_duration": 0,
            "generated_by": "ReelForge TTS Generator (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def _get_tts_provider():
    """Initialize the appropriate TTS provider"""
    if settings.tts_provider == "openai":
        return OpenAI(api_key=settings.openai_api_key)
    elif settings.tts_provider == "elevenlabs":
        if not settings.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not found, falling back to OpenAI")
            return OpenAI(api_key=settings.openai_api_key)
        return "elevenlabs"  # Placeholder for ElevenLabs client
    else:
        logger.warning(f"Unknown TTS provider {settings.tts_provider}, using OpenAI")
        return OpenAI(api_key=settings.openai_api_key)


def _generate_audio_segment(provider, text: str, segment_id: int, tone: str = "professional") -> Dict[str, Any]:
    """Generate audio for a single text segment"""
    try:
        # Create output directory
        output_dir = Path("outputs/audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename based on content
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        audio_filename = f"segment_{segment_id}_{text_hash}.mp3"
        audio_path = output_dir / audio_filename
        
        # Check if audio already exists (cache)
        if audio_path.exists():
            logger.info(f"Using cached audio for segment {segment_id}")
            duration = _get_audio_duration(str(audio_path))
            return {
                "segment_id": segment_id,
                "file_path": str(audio_path),
                "filename": audio_filename,
                "duration": duration,
                "text": text,
                "cached": True,
                "checksum": text_hash
            }
        
        # Generate new audio
        if settings.tts_provider == "openai":
            duration = _generate_openai_audio(provider, text, str(audio_path), tone)
        elif settings.tts_provider == "elevenlabs":
            duration = _generate_elevenlabs_audio(text, str(audio_path), tone)
        else:
            raise ValueError(f"Unsupported TTS provider: {settings.tts_provider}")
        
        logger.info(f"Generated audio for segment {segment_id}", duration=duration)
        
        return {
            "segment_id": segment_id,
            "file_path": str(audio_path),
            "filename": audio_filename,
            "duration": duration,
            "text": text,
            "cached": False,
            "checksum": text_hash,
            "generation_time": "now"  # In production, use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Failed to generate audio for segment {segment_id}", error=str(e))
        return None


def _generate_openai_audio(client, text: str, output_path: str, tone: str) -> float:
    """Generate audio using OpenAI TTS"""
    try:
        # Select voice based on tone
        voice_settings = _get_voice_settings(tone)
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1-hd",  # High quality model
            voice=voice_settings["voice"],
            input=text,
            speed=voice_settings["speed"]
        )
        
        # Save audio file
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        # Calculate duration (approximate based on text length and speed)
        words = len(text.split())
        # Average speaking rate: 2.5 words per second
        duration = words / (2.5 * voice_settings["speed"])
        
        return duration
        
    except Exception as e:
        logger.error("OpenAI TTS generation failed", error=str(e))
        raise


def _generate_elevenlabs_audio(text: str, output_path: str, tone: str) -> float:
    """Generate audio using ElevenLabs TTS (placeholder implementation)"""
    # This is a placeholder implementation
    # In production, implement actual ElevenLabs API integration
    
    logger.warning("ElevenLabs TTS not implemented, creating silent audio")
    
    # Create a short silent audio file as placeholder
    import subprocess
    duration = max(2.0, len(text.split()) / 2.5)
    
    # Generate silent audio with FFmpeg
    cmd = [
        settings.ffmpeg_binary_path,
        "-f", "lavfi",
        "-i", f"anullsrc=duration={duration}:sample_rate=44100:channel_layout=stereo",
        "-y",  # Overwrite output file
        output_path
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return duration


def _get_voice_settings(tone: str = "professional") -> Dict[str, Any]:
    """Get voice settings based on desired tone"""
    voice_mapping = {
        "professional": {"voice": "alloy", "speed": 1.0},
        "casual": {"voice": "nova", "speed": 1.1},
        "energetic": {"voice": "fable", "speed": 1.2},
        "calm": {"voice": "echo", "speed": 0.9},
        "friendly": {"voice": "shimmer", "speed": 1.0},
        "authoritative": {"voice": "onyx", "speed": 0.95}
    }
    
    return voice_mapping.get(tone, voice_mapping["professional"])


def _get_audio_duration(file_path: str) -> float:
    """Get duration of audio file using FFmpeg"""
    try:
        import subprocess
        
        cmd = [
            settings.ffmpeg_binary_path,
            "-i", file_path,
            "-f", "null",
            "-"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.STDOUT)
        
        # Parse duration from FFmpeg output
        for line in result.stderr.split('\n'):
            if 'Duration:' in line:
                duration_str = line.split('Duration:')[1].split(',')[0].strip()
                # Parse HH:MM:SS.ss format
                time_parts = duration_str.split(':')
                if len(time_parts) == 3:
                    hours = float(time_parts[0])
                    minutes = float(time_parts[1])
                    seconds = float(time_parts[2])
                    return hours * 3600 + minutes * 60 + seconds
        
        # Fallback: estimate based on file size (rough approximation)
        file_size = os.path.getsize(file_path)
        # Assume ~128 kbps MP3, rough calculation
        estimated_duration = file_size / (128 * 1024 / 8)  # bytes per second
        return max(1.0, estimated_duration)
        
    except Exception as e:
        logger.error("Failed to get audio duration", file=file_path, error=str(e))
        # Return default duration based on text length
        return 3.0  # Default fallback


def validate_audio_files(audio_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate generated audio files"""
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "total_files": len(audio_results),
        "total_duration": 0
    }
    
    for audio_result in audio_results:
        file_path = audio_result.get('file_path')
        
        # Check file exists
        if not os.path.exists(file_path):
            validation_results["errors"].append(f"Audio file not found: {file_path}")
            validation_results["valid"] = False
            continue
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 1000:  # Less than 1KB
            validation_results["warnings"].append(f"Very small audio file: {file_path}")
        
        # Add to total duration
        validation_results["total_duration"] += audio_result.get('duration', 0)
    
    return validation_results
