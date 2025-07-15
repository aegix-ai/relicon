#!/usr/bin/env python3
"""
Debug FFmpeg video generation issues
"""

import subprocess
import json
import os

def test_simple_video():
    """Test basic video creation"""
    print("🔧 Testing basic video creation...")
    
    # Create simple test video
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=5',
        '-vf', 'drawtext=text="TEST":fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        'test_simple.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Basic video creation works")
            if os.path.exists('test_simple.mp4'):
                size = os.path.getsize('test_simple.mp4')
                print(f"✅ Output file created: {size} bytes")
                return True
            else:
                print("❌ No output file created")
                return False
        else:
            print(f"❌ Basic video failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_complex_filter():
    """Test the complex filter we're using"""
    print("\n🔧 Testing complex filter...")
    
    # Simulate the actual filter we're generating
    filter_complex = '''
    [0]drawtext=text='Transform Your Business Today':fontsize=55:fontcolor=#FFFFFF:x=(w-text_w)/2:y=900:box=1:boxcolor=0x1A237E@0.8:boxborderw=8[v0a];
    [v0a]drawtext=text='with AI Innovation':fontsize=47:fontcolor=#00E5FF:x=(w-text_w)/2:y=965:box=1:boxcolor=0x1A237E@0.8:boxborderw=6[v0]
    '''
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-filter_complex', filter_complex.strip(),
        '-map', '[v0]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        'test_complex.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Complex filter works")
            return True
        else:
            print(f"❌ Complex filter failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_transitions():
    """Test transition system"""
    print("\n🔧 Testing transitions...")
    
    # Create two simple videos and test xfade
    filter_complex = '''
    [0]drawtext=text='Scene 1':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2[v0];
    [1]drawtext=text='Scene 2':fontsize=60:fontcolor=red:x=(w-text_w)/2:y=(h-text_h)/2[v1];
    [v0][v1]xfade=transition=fade:duration=0.5:offset=2[video]
    '''
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=blue:s=1080x1920:d=3',
        '-f', 'lavfi', '-i', 'color=c=green:s=1080x1920:d=3',
        '-filter_complex', filter_complex.strip(),
        '-map', '[video]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        'test_transition.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Transitions work")
            return True
        else:
            print(f"❌ Transitions failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Relicon FFmpeg Debug Suite")
    print("="*50)
    
    success_count = 0
    
    if test_simple_video():
        success_count += 1
    
    if test_complex_filter():
        success_count += 1
        
    if test_transitions():
        success_count += 1
    
    print(f"\n📊 Summary: {success_count}/3 tests passed")
    
    if success_count == 3:
        print("✅ All FFmpeg components working!")
    else:
        print("❌ Some components failing - need fixes")