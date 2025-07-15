#!/usr/bin/env python3
"""
Create and test bulletproof video system
"""

import subprocess
import json
import os

def create_bulletproof_video():
    """Create a video that absolutely works"""
    print("🔧 Creating bulletproof professional video...")
    
    # Ultra-simplified but professional filter that ALWAYS works
    filter_complex = '''
    [0]drawtext=text='Transform Your Business Today':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=800:box=1:boxcolor=0x1A237E@0.8:boxborderw=10[v0a];
    [v0a]drawtext=text='with AI Innovation':fontsize=50:fontcolor=cyan:x=(w-text_w)/2:y=900:box=1:boxcolor=0x1A237E@0.8:boxborderw=8[v0];
    [1]drawtext=text='Increase Productivity 300%':fontsize=58:fontcolor=white:x=(w-text_w)/2:y=800:box=1:boxcolor=0x1B5E20@0.85:boxborderw=10[v1a];
    [v1a]drawtext=text='in Just 30 Days':fontsize=48:fontcolor=green:x=(w-text_w)/2:y=900:box=1:boxcolor=0x1B5E20@0.85:boxborderw=8[v1];
    [2]drawtext=text='Join Success Stories':fontsize=62:fontcolor=white:x=(w-text_w)/2:y=800:box=1:boxcolor=0xAD1457@0.9:boxborderw=12[v2a];
    [v2a]drawtext=text='Start Now!':fontsize=55:fontcolor=orangered:x=(w-text_w)/2:y=900:box=1:boxcolor=0xAD1457@0.9:boxborderw=10[v2];
    [v0][v1]xfade=transition=fade:duration=0.5:offset=3.5[t1];
    [t1][v2]xfade=transition=dissolve:duration=0.5:offset=7[video]
    '''
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=4',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=4', 
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-filter_complex', filter_complex.strip(),
        '-map', '[video]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-t', '11',
        'bulletproof_test.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Bulletproof video created!")
            if os.path.exists('bulletproof_test.mp4'):
                size = os.path.getsize('bulletproof_test.mp4')
                print(f"✅ Output file: {size} bytes")
                return True
            else:
                print("❌ No output file")
                return False
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Relicon Bulletproof Test")
    print("="*40)
    
    if create_bulletproof_video():
        print("✅ SYSTEM IS WORKING - Ready for deployment!")
    else:
        print("❌ CRITICAL FAILURE - Need immediate fix")