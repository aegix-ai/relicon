#!/usr/bin/env python3
"""
Simple direct video creation test
"""
import subprocess
import os

def create_test_video():
    """Create a simple test video directly"""
    print("Creating simple test video...")
    
    output_file = "simple_test.mp4"
    
    # Create a simple 10-second video with text
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'color=c=blue:size=1080x1920:duration=10',
        '-vf', "drawtext=text='FlowFit Test Video':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-r', '30',
        output_file
    ]
    
    print("Running FFmpeg command...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"SUCCESS: Video created - {output_file} ({size:,} bytes)")
            
            # Verify with ffprobe
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', output_file]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode == 0:
                import json
                info = json.loads(probe_result.stdout)
                duration = float(info['format']['duration'])
                print(f"Duration: {duration:.1f} seconds")
                return True
            else:
                print("Video created but probe failed")
                return True
        else:
            print("FFmpeg succeeded but no file created")
            return False
    else:
        print(f"FFmpeg failed: {result.stderr}")
        return False

if __name__ == "__main__":
    success = create_test_video()
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")