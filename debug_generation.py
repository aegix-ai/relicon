#!/usr/bin/env python3
"""
Debug script to test video generation pipeline
"""
import os
import json
import subprocess
from openai import OpenAI

def test_full_pipeline():
    """Test the complete video generation pipeline"""
    
    print("=== Testing Relicon Video Generation Pipeline ===")
    
    # Test 1: OpenAI Connection
    print("\n1. Testing OpenAI connection...")
    try:
        openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        print("✓ OpenAI client initialized")
        
        # Test concept generation
        prompt = """Create a viral short-form video concept for FlowFit App: A fitness app with 15-minute workouts

Generate a JSON response with:
1. A hook (opening line to grab attention)
2. 3 script segments, each 8-10 seconds long

Format:
{
  "hook": "compelling opening line",
  "segments": [
    {"text": "voiceover text", "duration": 8},
    {"text": "voiceover text", "duration": 9},
    {"text": "voiceover text", "duration": 10}
  ]
}

Make it engaging and thumb-stopping for social media."""

        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        script_data = json.loads(response.choices[0].message.content)
        print(f"✓ OpenAI generated script: {script_data}")
        
    except Exception as e:
        print(f"✗ OpenAI error: {e}")
        return False
    
    # Test 2: FFmpeg Video Generation
    print("\n2. Testing FFmpeg video generation...")
    try:
        job_id = "debug_test"
        output_file = f"static/video_{job_id}.mp4"
        segments = script_data['segments']
        colors = ['0x4A90E2', '0x7B68EE', '0xFF6B6B']
        
        # Build FFmpeg command - simplified version
        inputs = []
        filter_parts = []
        
        for i, segment in enumerate(segments):
            duration = min(segment.get('duration', 8), 10)  # Cap duration
            text = segment.get('text', f'Segment {i+1}')
            
            # Clean text for FFmpeg
            safe_text = text.replace("'", "").replace('"', "").replace(":", "").replace(",", "")
            safe_text = safe_text.replace("(", "").replace(")", "").replace("!", "")
            if len(safe_text) > 40:
                safe_text = safe_text[:37] + "..."
            
            color = colors[i % len(colors)]
            
            # Add input
            inputs.extend(['-f', 'lavfi', '-i', f'color=c={color}:size=1080x1920:duration={duration}'])
            
            # Add text overlay
            y_pos = 960 if i % 2 == 0 else 800
            filter_parts.append(f'[{i}]drawtext=text={safe_text}:fontsize=48:fontcolor=white:x=(w-text_w)/2:y={y_pos}[v{i}]')
        
        # Concatenate all segments
        concat_inputs = ''.join(f'[v{i}]' for i in range(len(segments)))
        filter_parts.append(f'{concat_inputs}concat=n={len(segments)}:v=1:a=0[out]')
        
        # Complete FFmpeg command
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', ';'.join(filter_parts),
            '-map', '[out]',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_file
        ]
        
        print(f"FFmpeg command: {' '.join(cmd[:10])}...")
        
        # Execute FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✓ Video created successfully: {output_file} ({size} bytes)")
            return True
        else:
            print(f"✗ FFmpeg failed:")
            print(f"Return code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"✗ FFmpeg error: {e}")
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    print(f"\n=== Pipeline {'SUCCESS' if success else 'FAILED'} ===")