#!/usr/bin/env python3
"""
Debug the actual scenario that's failing
"""

import subprocess
import json
import os

def create_mock_script():
    """Create mock script data that mimics real generation"""
    return {
        "segments": [
            {
                "text": "Transform Your Business Today with Revolutionary AI Technology",
                "energy": "exciting",
                "visual_style": "zoom_burst",
                "duration": 4.2
            },
            {
                "text": "Increase Productivity by 300% in Just 30 Days",
                "energy": "confident", 
                "visual_style": "slide_dynamic",
                "duration": 3.8
            },
            {
                "text": "Join Thousands of Success Stories - Start Now!",
                "energy": "urgent",
                "visual_style": "pulse_scale", 
                "duration": 2.5
            }
        ]
    }

def generate_realistic_filter(script_data):
    """Generate the exact filter we're creating in the real system"""
    
    # This replicates the exact logic from server/routes.ts
    video_filters = []
    for i, segment in enumerate(script_data["segments"]):
        raw_text = segment["text"].replace("'", "").replace('"', '').replace('\\', '').replace(':', ' ')
        words = raw_text.split(' ')
        
        # Intelligent text wrapping - max 32 chars per line, 2 lines max
        max_chars_per_line = 32
        lines = []
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += (' ' if current_line else '') + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
                if len(lines) >= 2:
                    break
                    
        if current_line and len(lines) < 2:
            lines.append(current_line)
            
        if len(lines) == 0:
            lines = [raw_text[:max_chars_per_line]]
        
        # Professional color schemes
        color_schemes = {
            'explosive': {'primary': '#FFFFFF', 'secondary': '#FFD700', 'accent': '#FF4444', 'bg': '0xFF1744@0.85'},
            'tension': {'primary': '#F5F5F5', 'secondary': '#FFAB00', 'accent': '#424242', 'bg': '0x37474F@0.9'},
            'exciting': {'primary': '#FFFFFF', 'secondary': '#00E5FF', 'accent': '#3F51B5', 'bg': '0x1A237E@0.8'},
            'confident': {'primary': '#FFFFFF', 'secondary': '#4CAF50', 'accent': '#2E7D32', 'bg': '0x1B5E20@0.85'},
            'urgent': {'primary': '#FFFFFF', 'secondary': '#FF5722', 'accent': '#E91E63', 'bg': '0xAD1457@0.9'}
        }
        
        scheme = color_schemes.get(segment['energy'], color_schemes['exciting'])
        font_size = max(45, min(75, int(1200 / max(len(lines[0]) if lines else 1, 1))))
        
        line_height = font_size + 15
        start_y = 960 if len(lines) == 1 else 900
        
        # Generate text effect based on visual style
        if segment['visual_style'] == 'zoom_burst':
            if len(lines) == 1:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize={int(font_size*0.6)}:fontcolor={scheme['primary']}:x=(w-text_w)/2:y={start_y}:alpha='t/{segment['duration']/3}':box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}a];[v{i}a]drawtext=text='{lines[0]}':fontsize={font_size}:fontcolor={scheme['secondary']}:x=(w-text_w)/2:y={start_y-50}:enable='gte(t,{segment['duration']/3})':box=1:boxcolor={scheme['bg']}:boxborderw=12:shadowcolor={scheme['accent']}:shadowx=4:shadowy=4[v{i}]"
            else:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize={font_size}:fontcolor={scheme['primary']}:x=(w-text_w)/2:y={start_y}:alpha='t/{segment['duration']/3}':box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}a];[v{i}a]drawtext=text='{lines[1]}':fontsize={font_size-8}:fontcolor={scheme['secondary']}:x=(w-text_w)/2:y={start_y+line_height}:enable='gte(t,{segment['duration']/4})':box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}]"
        elif segment['visual_style'] == 'slide_dynamic':
            if len(lines) == 1:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize={font_size}:fontcolor={scheme['primary']}:x='(w-text_w)/2+(w-text_w)*max(0,1-4*t/{segment['duration']})':y={start_y}:box=1:boxcolor={scheme['bg']}:boxborderw=10:shadowcolor={scheme['accent']}:shadowx=2:shadowy=2[v{i}]"
            else:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize={font_size}:fontcolor={scheme['primary']}:x='(w-text_w)/2+(w-text_w)*max(0,1-6*t/{segment['duration']})':y={start_y}:box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}a];[v{i}a]drawtext=text='{lines[1]}':fontsize={font_size-8}:fontcolor={scheme['secondary']}:x='(w-text_w)/2-(w-text_w)*max(0,1-6*(t-{segment['duration']/5})/{segment['duration']})':y={start_y+line_height}:enable='gte(t,{segment['duration']/5})':box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}]"
        else:  # pulse_scale
            pulse_scale = f"{font_size}+{int(font_size*0.15)}*sin(t*6)"
            if len(lines) == 1:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize='{pulse_scale}':fontcolor='if(lt(mod(t,0.8),0.4),{scheme['primary']},{scheme['secondary']})':x=(w-text_w)/2:y={start_y}:box=1:boxcolor={scheme['bg']}:boxborderw=10:shadowcolor={scheme['accent']}:shadowx=2:shadowy=2[v{i}]"
            else:
                text_effect = f"[{i}]drawtext=text='{lines[0]}':fontsize='{pulse_scale}':fontcolor='if(lt(mod(t,0.8),0.4),{scheme['primary']},{scheme['secondary']})':x=(w-text_w)/2:y={start_y}:box=1:boxcolor={scheme['bg']}:boxborderw=8[v{i}a];[v{i}a]drawtext=text='{lines[1]}':fontsize={font_size-8}:fontcolor={scheme['secondary']}:x=(w-text_w)/2:y={start_y+line_height}:enable='gte(t,{segment['duration']/4})':box=1:boxcolor={scheme['bg']}:boxborderw=6[v{i}]"
        
        video_filters.append(text_effect)
    
    # Generate transitions
    if len(script_data["segments"]) == 1:
        transition_chain = "[v0]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[video]"
    else:
        transitions = {
            'explosive_to_tension': 'fadeblack',
            'exciting_to_confident': 'fade',
            'confident_to_urgent': 'wipeleft',
            'any_to_any': 'crossfade'
        }
        
        current_input = "[v0]"
        transition_parts = []
        
        for i in range(1, len(script_data["segments"])):
            prev_energy = script_data["segments"][i-1]['energy']
            current_energy = script_data["segments"][i]['energy']
            transition_key = f"{prev_energy}_to_{current_energy}"
            transition = transitions.get(transition_key, transitions['any_to_any'])
            
            prev_duration = sum(seg['duration'] for seg in script_data["segments"][:i])
            transition_duration = 0.3
            offset = max(0, prev_duration - transition_duration)
            
            if i == len(script_data["segments"]) - 1:
                transition_parts.append(f"{current_input}[v{i}]xfade=transition={transition}:duration={transition_duration}:offset={offset}[video]")
            else:
                transition_parts.append(f"{current_input}[v{i}]xfade=transition={transition}:duration={transition_duration}:offset={offset}[t{i}]")
                current_input = f"[t{i}]"
        
        transition_chain = ';'.join(transition_parts)
    
    # Combine filters
    video_filter_str = ';'.join(video_filters)
    full_filter = f"{video_filter_str};{transition_chain}"
    
    return full_filter

def test_realistic_scenario():
    """Test with realistic scenario"""
    print("🔧 Testing realistic video generation scenario...")
    
    script_data = create_mock_script()
    filter_complex = generate_realistic_filter(script_data)
    
    print(f"Generated filter length: {len(filter_complex)} characters")
    print("Filter preview:")
    print(filter_complex[:200] + "..." if len(filter_complex) > 200 else filter_complex)
    
    # Create inputs (one black screen per segment)
    cmd = ['ffmpeg', '-y']
    for i, segment in enumerate(script_data["segments"]):
        cmd.extend(['-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:d={segment["duration"]}'])
    
    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[video]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-t', str(sum(seg['duration'] for seg in script_data["segments"])),
        'test_realistic.mp4'
    ])
    
    print(f"FFmpeg command length: {len(' '.join(cmd))} characters")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Realistic scenario works!")
            if os.path.exists('test_realistic.mp4'):
                size = os.path.getsize('test_realistic.mp4')
                print(f"✅ Output file created: {size} bytes")
                return True
            else:
                print("❌ No output file created")
                return False
        else:
            print(f"❌ Realistic scenario failed:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Relicon Realistic Scenario Debug")
    print("="*50)
    
    if test_realistic_scenario():
        print("✅ Realistic scenario working - issue must be elsewhere")
    else:
        print("❌ Found the problem - fixing needed")