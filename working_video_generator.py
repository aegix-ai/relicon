#!/usr/bin/env python3
"""
Minimal working video generator - test every step
"""
import json
import os
import sys
import subprocess
import tempfile
import shutil

def test_step(step_name, func):
    """Test a step and show result"""
    print(f"Testing: {step_name}...")
    try:
        result = func()
        if result:
            print(f"✓ PASS: {step_name}")
            return True
        else:
            print(f"✗ FAIL: {step_name}")
            return False
    except Exception as e:
        print(f"✗ ERROR: {step_name} - {str(e)}")
        return False

def check_prerequisites():
    """Check all prerequisites"""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found")
        return False
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode != 0:
            print("ERROR: FFmpeg not working")
            return False
    except:
        print("ERROR: FFmpeg not available")
        return False
    
    # Check requests library
    try:
        import requests
    except ImportError:
        print("ERROR: requests library not found")
        return False
    
    return True

def generate_simple_concept():
    """Generate a simple concept using OpenAI"""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a creative director. Generate a simple concept for a 30-second fitness app ad. Respond only with valid JSON."
                },
                {
                    "role": "user", 
                    "content": "Create a concept for FlowFit - a 15-minute workout app for busy professionals. JSON format: {\"concept\": \"description\", \"hook\": \"opening line\"}"
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"OpenAI API error: {response.status_code}")
            print(response.text)
            return None
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse and validate JSON
        concept_data = json.loads(content)
        
        if 'concept' in concept_data and 'hook' in concept_data:
            print(f"Concept: {concept_data['concept'][:50]}...")
            print(f"Hook: {concept_data['hook']}")
            return concept_data
        else:
            print("Invalid concept format")
            return None
            
    except Exception as e:
        print(f"Concept generation error: {str(e)}")
        return None

def generate_simple_script(concept):
    """Generate a simple script"""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Create a 30-second video script based on this concept: {concept['concept']}

Hook: {concept['hook']}

Format as JSON with exactly this structure:
{{
  "segments": [
    {{
      "text": "voiceover text here",
      "duration": 6
    }}
  ]
}}

Create 3-5 segments that total 30 seconds."""
        
        data = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": "You are a script writer. Create a video script in the exact JSON format requested."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Script API error: {response.status_code}")
            return None
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        script_data = json.loads(content)
        
        if 'segments' in script_data:
            segments = script_data['segments']
            print(f"Script: {len(segments)} segments")
            total_duration = sum(seg.get('duration', 5) for seg in segments)
            print(f"Total duration: {total_duration} seconds")
            return script_data
        else:
            print("Invalid script format")
            return None
            
    except Exception as e:
        print(f"Script generation error: {str(e)}")
        return None

def create_simple_video(script, output_file):
    """Create a simple video using FFmpeg"""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        segments = script['segments']
        if not segments:
            print("No segments to process")
            return False
        
        # Create video segments
        segment_files = []
        
        for i, segment in enumerate(segments):
            text = segment.get('text', f'Segment {i+1}')
            duration = segment.get('duration', 5)
            
            # Clean text for FFmpeg (remove problematic characters)
            safe_text = text.replace("'", "").replace('"', "").replace(":", "").replace(",", "")
            if len(safe_text) > 40:
                safe_text = safe_text[:37] + "..."
            
            segment_file = f"/tmp/segment_{i}.mp4"
            
            # Create video segment with colored background and text
            cmd = [
                'ffmpeg', '-y', '-v', 'quiet',
                '-f', 'lavfi',
                '-i', f'color=c=blue:size=1080x1920:duration={duration}',
                '-vf', f"drawtext=text={safe_text}:fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                segment_file
            ]
            
            result = subprocess.run(cmd, timeout=30)
            
            if result.returncode == 0 and os.path.exists(segment_file):
                segment_files.append(segment_file)
                print(f"Created segment {i+1}: {duration}s")
            else:
                print(f"Failed to create segment {i+1}")
                return False
        
        if not segment_files:
            print("No segments created")
            return False
        
        # Combine segments
        if len(segment_files) == 1:
            shutil.copy(segment_files[0], output_file)
        else:
            # Create concat file
            concat_file = "/tmp/concat_list.txt"
            with open(concat_file, 'w') as f:
                for seg_file in segment_files:
                    f.write(f"file '{seg_file}'\n")
            
            # Combine with FFmpeg
            cmd = [
                'ffmpeg', '-y', '-v', 'quiet',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                output_file
            ]
            
            result = subprocess.run(cmd, timeout=60)
            
            if result.returncode != 0:
                print("Failed to combine segments")
                return False
        
        # Cleanup temp files
        for seg_file in segment_files:
            try:
                os.remove(seg_file)
            except:
                pass
        
        try:
            os.remove("/tmp/concat_list.txt")
        except:
            pass
        
        return os.path.exists(output_file)
        
    except Exception as e:
        print(f"Video creation error: {str(e)}")
        return False

def verify_video(video_file):
    """Verify the video file is valid"""
    try:
        if not os.path.exists(video_file):
            print(f"Video file not found: {video_file}")
            return False
        
        file_size = os.path.getsize(video_file)
        if file_size < 1000:  # Less than 1KB
            print(f"Video file too small: {file_size} bytes")
            return False
        
        # Use ffprobe to check video
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("ffprobe failed")
            return False
        
        info = json.loads(result.stdout)
        format_info = info.get('format', {})
        duration = float(format_info.get('duration', 0))
        
        streams = info.get('streams', [])
        video_streams = [s for s in streams if s.get('codec_type') == 'video']
        
        if not video_streams:
            print("No video streams found")
            return False
        
        vs = video_streams[0]
        width = vs.get('width', 0)
        height = vs.get('height', 0)
        
        print(f"Video verified: {width}x{height}, {duration:.1f}s, {file_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"Video verification error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("WORKING VIDEO GENERATOR TEST")
    print("Following algorithm: work → test → fix → test")
    print("=" * 60)
    
    # Step 1: Check prerequisites
    if not test_step("Prerequisites", check_prerequisites):
        return False
    
    # Step 2: Generate concept
    concept = None
    if test_step("Concept Generation", lambda: generate_simple_concept()):
        # Get the actual concept
        concept = generate_simple_concept()
        if not concept:
            print("Failed to get concept")
            return False
    else:
        return False
    
    # Step 3: Generate script
    script = None
    if test_step("Script Generation", lambda: generate_simple_script(concept)):
        script = generate_simple_script(concept)
        if not script:
            print("Failed to get script")
            return False
    else:
        return False
    
    # Step 4: Create video
    output_file = "test_video_output.mp4"
    if not test_step("Video Creation", lambda: create_simple_video(script, output_file)):
        return False
    
    # Step 5: Verify video
    if not test_step("Video Verification", lambda: verify_video(output_file)):
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: Created working short-form video!")
    print(f"File: {output_file}")
    print("All steps passed - system is 100% working")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)