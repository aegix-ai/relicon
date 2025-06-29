#!/usr/bin/env python3
"""
Test the exact assembly that's failing
"""

import subprocess
import os

def test_single_video_assembly():
    """Test single video case that might be failing"""
    print("Testing single video assembly...")
    
    filter_complex = "[0]drawtext=text='Test Video':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=850:box=1:boxcolor=0x1A237E@0.8:boxborderw=12[v0];[v0]copy[video]"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=5',
        '-filter_complex', filter_complex,
        '-map', '[video]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        'test_single.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Single video assembly works")
            return True
        else:
            print(f"❌ Single video failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_multi_video_assembly():
    """Test multi-video case"""
    print("Testing multi-video assembly...")
    
    filter_complex = """
    [0]drawtext=text='Scene One':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=850:box=1:boxcolor=0x1A237E@0.8:boxborderw=12[v0];
    [1]drawtext=text='Scene Two':fontsize=60:fontcolor=cyan:x=(w-text_w)/2:y=850:box=1:boxcolor=0x1B5E20@0.85:boxborderw=12[v1];
    [v0][v1]xfade=transition=fade:duration=0.5:offset=2.5[video]
    """
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-filter_complex', filter_complex.strip(),
        '-map', '[video]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        'test_multi.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Multi-video assembly works")
            return True
        else:
            print(f"❌ Multi-video failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Assembly Fix Test")
    print("="*30)
    
    success = 0
    if test_single_video_assembly():
        success += 1
    if test_multi_video_assembly():
        success += 1
        
    if success == 2:
        print("✅ Assembly system fixed!")
    else:
        print("❌ Still has issues")