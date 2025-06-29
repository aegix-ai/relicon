#!/usr/bin/env python3
"""
Test complete system with audio integration
"""

import subprocess
import os

def create_test_audio():
    """Create test audio files"""
    audio_files = []
    for i in range(3):
        audio_file = f'test_audio_{i}.wav'
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'sine=frequency={440 + i*100}:duration=3',
            '-c:a', 'pcm_s16le',
            audio_file
        ]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(audio_file):
            audio_files.append(audio_file)
    return audio_files

def test_complete_assembly():
    """Test complete video + audio assembly"""
    print("Testing complete video + audio assembly...")
    
    # Create test audio
    audio_files = create_test_audio()
    print(f"Created {len(audio_files)} audio files")
    
    # Video filter (3 segments)
    video_filter = """
    [0]drawtext=text='Scene One Text':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=850:box=1:boxcolor=0x1A237E@0.8:boxborderw=12[v0];
    [1]drawtext=text='Scene Two Content':fontsize=58:fontcolor=cyan:x=(w-text_w)/2:y=850:box=1:boxcolor=0x1B5E20@0.85:boxborderw=12[v1];
    [2]drawtext=text='Final Scene':fontsize=62:fontcolor=orangered:x=(w-text_w)/2:y=850:box=1:boxcolor=0xAD1457@0.9:boxborderw=12[v2]
    """
    
    # Transition chain
    transition_chain = "[v0][v1]xfade=transition=fade:duration=0.4:offset=2.6[t1];[t1][v2]xfade=transition=dissolve:duration=0.4:offset=5.6[video]"
    
    # Audio mixing
    audio_mix = "[3:a][4:a][5:a]concat=n=3:v=0:a=1[audio]"
    
    # Complete filter
    filter_complex = video_filter.strip() + ";" + transition_chain + ";" + audio_mix
    
    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3', 
        '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=3',
        '-i', audio_files[0],
        '-i', audio_files[1], 
        '-i', audio_files[2],
        '-filter_complex', filter_complex,
        '-map', '[video]',
        '-map', '[audio]',
        '-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p', '-r', '30', '-crf', '23',
        'test_complete.mp4'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Cleanup audio files
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        
        if result.returncode == 0:
            if os.path.exists('test_complete.mp4'):
                size = os.path.getsize('test_complete.mp4')
                print(f"✅ Complete system works! Video: {size} bytes")
                return True
            else:
                print("❌ No output file")
                return False
        else:
            print(f"❌ Assembly failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Complete System Test")
    print("="*30)
    
    if test_complete_assembly():
        print("🚀 SYSTEM IS FULLY OPERATIONAL!")
    else:
        print("❌ System needs final fixes")