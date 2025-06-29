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
    
    # Create video segments with captions
    for i, (segment, audio_file) in enumerate(zip(script_segments, audio_files)):
        duration = segment.get("duration", 3.0)
        text = segment["voiceover"]
        colors = scene_colors[i % len(scene_colors)].split(",")
        
        # Create gradient background
        gradient_filter = f"color=c={colors[0]}:size=1080x1920:duration={duration}[bg{i}];"
        gradient_filter += f"color=c={colors[1]}:size=1080x1920:duration={duration}[fg{i}];"
        gradient_filter += f"[fg{i}]fade=t=in:st=0:d=0.5:alpha=1[fade{i}];"
        gradient_filter += f"[bg{i}][fade{i}]overlay[grad{i}];"
        
        # Add caption with professional styling (escape text properly)
        safe_text = text.replace("'", "\\'").replace(":", "\\:").replace("%", "\\%")[:100]  # Limit length
        caption_filter = f"[grad{i}]drawtext=text='{safe_text}'"
        caption_filter += ":fontsize=36:fontcolor=white:box=1:boxcolor=black@0.8"
        caption_filter += ":boxborderw=8:x=(w-text_w)/2:y=h-150"
        caption_filter += f":enable='between(t,0,{duration})'[v{i}];"
        
        filter_complex.append(gradient_filter + caption_filter)
        audio_inputs.append(f"-i {audio_file}")
    
    # Concatenate video segments with smooth transitions
    concat_video = f"[{''.join([f'v{i}' for i in range(len(script_segments))])}]concat=n={len(script_segments)}:v=1:a=0[video];"
    filter_complex.append(concat_video)
    
    # Concatenate audio segments
    concat_audio = f"[{''.join([f'{i}:a' for i in range(len(audio_files))])}]concat=n={len(audio_files)}:v=0:a=1[audio];"
    filter_complex.append(concat_audio)
    
    progress_update(85, "Assembling final video with synchronized captions")
    
    # Build complete FFmpeg command
    cmd = ["ffmpeg", "-y"]
    
    # Add audio inputs
    for audio_file in audio_files:
        cmd.extend(["-i", audio_file])
    
    # Add filter complex
    cmd.extend(["-filter_complex", "".join(filter_complex)])
    
    # Output mapping and encoding
    cmd.extend([
        "-map", "[video]",
        "-map", "[audio]", 
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-r", "30",
        "-aspect", "9:16",
        "-s", "1080x1920",
        output_file
    ])
    
    print(f"Running FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"FFmpeg stderr: {result.stderr}")
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        progress_update(95, "Finalizing video output")
        
        # Verify output file
        if not os.path.exists(output_file):
            raise Exception("Output video file was not created")
        
        # Check file size
        file_size = os.path.getsize(output_file)
        if file_size < 1000:  # Less than 1KB
            raise Exception("Output video file is too small")
            
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