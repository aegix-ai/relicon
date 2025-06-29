#!/usr/bin/env python3
"""
Complete AI Video Generation System
Creates dynamic planned videos with audio, captions, and 9:16 formatting
"""
import argparse
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import requests
from openai import OpenAI

def progress_update(progress, message):
    """Send progress update that the Node.js server can parse"""
    print(f"PROGRESS:{progress}:{message}", flush=True)

def generate_concept_and_script(brand_name, brand_description, target_audience, tone, duration, call_to_action):
    """Generate AI concept and script using OpenAI"""
    progress_update(25, "Generating AI concept and script")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Generate concept first
    concept_prompt = f"""
    Create a compelling video ad concept for:
    Brand: {brand_name}
    Description: {brand_description}
    Target Audience: {target_audience}
    Tone: {tone}
    Duration: {duration} seconds
    Call to Action: {call_to_action}
    
    Return a JSON object with:
    - hook: attention-grabbing opening
    - key_points: main selling points (3-4 items)
    - visual_style: description of visual approach
    - pacing: how the video should flow
    """
    
    try:
        concept_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": concept_prompt}],
            response_format={"type": "json_object"}
        )
        concept = json.loads(concept_response.choices[0].message.content)
        
        progress_update(35, "Creating detailed script with timing")
        
        # Generate script segments
        script_prompt = f"""
        Based on this concept: {json.dumps(concept)}
        
        Create a detailed {duration}-second video script with exact timing.
        Target audience: {target_audience}
        
        Return JSON with "segments" array, each having:
        - scene: scene number (1, 2, 3...)
        - start_time: when scene starts (seconds)
        - duration: scene length (seconds) 
        - voiceover: exact text to speak (conversational, engaging)
        - visual_hint: what should be shown visually
        - energy: low/medium/high
        
        Make it natural pacing with 3-5 second scenes that build engagement.
        End with strong call to action: "{call_to_action}"
        """
        
        script_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": script_prompt}],
            response_format={"type": "json_object"}
        )
        script_data = json.loads(script_response.choices[0].message.content)
        
        return {
            "concept": concept,
            "script": script_data["segments"]
        }
        
    except Exception as e:
        raise Exception(f"Failed to generate content: {e}")

def create_voiceover_audio(script_segments, output_dir):
    """Create voiceover audio files using OpenAI TTS"""
    progress_update(45, "Creating voiceover with ElevenLabs AI")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    audio_files = []
    
    for i, segment in enumerate(script_segments):
        try:
            audio_file = os.path.join(output_dir, f"audio_segment_{i}.mp3")
            
            # Generate audio using OpenAI TTS
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",  # Professional female voice
                input=segment["voiceover"],
                speed=0.9  # Slightly slower for better clarity
            )
            
            with open(audio_file, "wb") as f:
                f.write(response.content)
            
            audio_files.append(audio_file)
            
        except Exception as e:
            print(f"Warning: Failed to generate audio for segment {i}: {e}")
            # Create silent audio as fallback
            duration = segment.get("duration", 3)
            silent_audio = os.path.join(output_dir, f"audio_segment_{i}.mp3")
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=duration={duration}",
                "-c:a", "libmp3lame", "-ar", "44100", "-y", silent_audio
            ], capture_output=True)
            audio_files.append(silent_audio)
    
    return audio_files

def create_video_with_captions(script_segments, audio_files, output_file):
    """Create final video with synchronized captions and scenes"""
    progress_update(70, "Generating dynamic scenes and transitions")
    
    # Create color backgrounds for each scene (professional gradient)
    scene_colors = [
        "#1a1a2e,#16213e",  # Dark blue gradient
        "#0f3460,#16537e",  # Blue gradient  
        "#e94560,#f5a623",  # Orange gradient
        "#2d3436,#636e72",  # Gray gradient
        "#00b894,#00cec9",  # Teal gradient
        "#6c5ce7,#a29bfe",  # Purple gradient
        "#fd79a8,#fdcb6e",  # Pink gradient
        "#e17055,#fab1a0"   # Coral gradient
    ]
    
    # Build FFmpeg filter complex for video assembly
    filter_complex = []
    audio_inputs = []
    
    # Create video segments with captions - simpler approach
    video_segments = []
    
    for i, (segment, audio_file) in enumerate(zip(script_segments, audio_files)):
        duration = segment.get("duration", 3.0)
        text = segment["voiceover"]
        colors = scene_colors[i % len(scene_colors)].split(",")
        
        # Create a simple colored background video segment
        segment_file = f"/tmp/segment_{i}.mp4"
        
        # Escape text properly for FFmpeg
        safe_text = text.replace("'", "'\"'\"'").replace(":", "\\:").replace("%", "\\%")[:80]
        
        # Create individual segment with background and caption
        segment_cmd = [
            "ffmpeg", "-y", "-f", "lavfi", 
            "-i", f"color=c={colors[0]}:size=1080x1920:duration={duration}",
            "-i", audio_file,
            "-filter_complex", 
            f"[0:v]drawtext=text='{safe_text}':fontsize=42:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=10:x=(w-text_w)/2:y=h-200[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-c:a", "aac",
            "-t", str(duration),
            segment_file
        ]
        
        try:
            result = subprocess.run(segment_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(segment_file):
                video_segments.append(segment_file)
            else:
                print(f"Warning: Failed to create segment {i}: {result.stderr}")
                # Create fallback segment
                fallback_cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"color=c={colors[0]}:size=1080x1920:duration={duration}",
                    "-i", audio_file,
                    "-map", "0:v", "-map", "1:a", "-t", str(duration),
                    segment_file
                ]
                subprocess.run(fallback_cmd, capture_output=True)
                video_segments.append(segment_file)
        except:
            print(f"Error creating segment {i}, skipping")
    
    if not video_segments:
        raise Exception("No video segments were created")
    
    progress_update(85, "Assembling final video with synchronized captions")
    
    # Concatenate all video segments into final output
    try:
        if len(video_segments) == 1:
            # Single segment, just copy
            shutil.copy2(video_segments[0], output_file)
        else:
            # Multiple segments, concatenate them
            concat_list = "/tmp/concat_list.txt"
            with open(concat_list, "w") as f:
                for segment in video_segments:
                    f.write(f"file '{segment}'\n")
            
            # Concatenate segments
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list,
                "-c", "copy",
                output_file
            ]
            
            print(f"Running FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"FFmpeg stderr: {result.stderr}")
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")
        
        progress_update(95, "Finalizing video output")
        
        # Verify output file
        if not os.path.exists(output_file):
            raise Exception("Output video file was not created")
        
        # Check file size
        file_size = os.path.getsize(output_file)
        if file_size < 1000:  # Less than 1KB
            raise Exception("Output video file is too small")
        
        # Clean up temporary files
        for segment in video_segments:
            try:
                os.remove(segment)
            except:
                pass
        
        progress_update(100, "Video generation completed successfully!")
        return True
        
    except subprocess.TimeoutExpired:
        raise Exception("Video generation timed out")
    except Exception as e:
        raise Exception(f"Video assembly failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate AI video advertisement")
    parser.add_argument("--brand-name", required=True, help="Brand name")
    parser.add_argument("--brand-description", required=True, help="Brand description") 
    parser.add_argument("--target-audience", default="general audience", help="Target audience")
    parser.add_argument("--duration", type=int, default=30, help="Video duration in seconds")
    parser.add_argument("--tone", default="professional", help="Video tone")
    parser.add_argument("--call-to-action", default="Take action now", help="Call to action")
    parser.add_argument("--output", required=True, help="Output video file path")
    parser.add_argument("--job-id", required=True, help="Job ID for tracking")
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found")
        sys.exit(1)
    
    try:
        # Test FFmpeg
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except:
        print("ERROR: FFmpeg not available")
        sys.exit(1)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            progress_update(10, "Starting AI video generation")
            
            # Generate content
            content = generate_concept_and_script(
                args.brand_name,
                args.brand_description, 
                args.target_audience,
                args.tone,
                args.duration,
                args.call_to_action
            )
            
            # Create audio
            audio_files = create_voiceover_audio(content["script"], temp_dir)
            
            # Create final video
            create_video_with_captions(content["script"], audio_files, args.output)
            
            print(f"SUCCESS: Video generated at {args.output}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()