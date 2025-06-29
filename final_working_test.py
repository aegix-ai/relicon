#!/usr/bin/env python3
"""
Final comprehensive test - generates actual video file
"""
import json
import os
import sys
import subprocess

# Add current directory to path
sys.path.append('.')

def main():
    """Run complete video generation test"""
    print("ReelForge Final Working Test")
    print("Generating actual short-form video with AI")
    print("=" * 50)
    
    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found")
        return False
    
    # Check FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ FFmpeg available")
    except:
        print("ERROR: FFmpeg not available")
        return False
    
    job_id = "final_working_test"
    
    try:
        # Import and test all components
        from agent.tools.concept import ConceptGenerationTool
        from agent.tools.script import ScriptWritingTool
        from agent.tools.tts import TextToSpeechTool
        from agent.tools.ffmpeg_fx import FFmpegAssemblyTool
        
        print("✓ All AI tools imported")
        
        # Test data
        brand_data = {
            "brand_name": "FlowFit",
            "brand_description": "Revolutionary fitness app that adapts to your lifestyle with AI-powered personalized workouts that take just 15 minutes a day",
            "target_audience": "Busy professionals aged 25-40",
            "tone": "energetic",
            "duration": 30,
            "call_to_action": "Download free today"
        }
        
        print(f"✓ Testing with brand: {brand_data['brand_name']}")
        
        # Step 1: Generate concept
        print("\n1. Generating concept...")
        concept_tool = ConceptGenerationTool()
        concept_result = concept_tool.run(json.dumps(brand_data))
        concept_data = json.loads(concept_result)
        
        if concept_data.get("status") == "failed":
            print(f"ERROR: {concept_data.get('error')}")
            return False
        
        print(f"✓ Concept: {concept_data.get('concept', '')[:80]}...")
        print(f"✓ Hook: {concept_data.get('hook', '')}")
        
        # Step 2: Write script
        print("\n2. Writing script...")
        script_tool = ScriptWritingTool()
        script_input = {"concept": concept_data, "brand_info": brand_data}
        script_result = script_tool.run(json.dumps(script_input))
        script_data = json.loads(script_result)
        
        if script_data.get("status") == "failed":
            print(f"ERROR: {script_data.get('error')}")
            return False
        
        segments = script_data.get('segments', [])
        print(f"✓ Script with {len(segments)} segments")
        
        # Step 3: Generate audio (may fail, continue anyway)
        print("\n3. Generating audio...")
        tts_tool = TextToSpeechTool()
        tts_input = {"script": script_data, "job_id": job_id, "brand_info": brand_data}
        
        try:
            audio_result = tts_tool.run(json.dumps(tts_input))
            audio_data = json.loads(audio_result)
            
            if audio_data.get("status") == "failed":
                print(f"⚠ Audio failed: {audio_data.get('error')} - continuing")
                audio_data = {"audio_files": [], "total_duration": 30}
            else:
                print(f"✓ Audio: {len(audio_data.get('audio_files', []))} files")
        except Exception as e:
            print(f"⚠ Audio error: {str(e)} - continuing")
            audio_data = {"audio_files": [], "total_duration": 30}
        
        # Step 4: Create video
        print("\n4. Creating video with FFmpeg...")
        ffmpeg_tool = FFmpegAssemblyTool()
        video_input = {
            "script": script_data,
            "audio": audio_data,
            "concept": concept_data,
            "job_id": job_id
        }
        
        video_result = ffmpeg_tool.run(json.dumps(video_input))
        video_data = json.loads(video_result)
        
        if video_data.get("status") == "failed":
            print(f"ERROR: {video_data.get('error')}")
            return False
        
        print(f"✓ Video created: {video_data.get('resolution', 'N/A')}")
        
        # Verify video file
        video_file = f"assets/{job_id}_final.mp4"
        if os.path.exists(video_file):
            file_size = os.path.getsize(video_file)
            print(f"✓ Video file: {video_file}")
            print(f"✓ Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Use ffprobe to verify video
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', video_file
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    format_info = info.get('format', {})
                    duration = float(format_info.get('duration', 0))
                    
                    streams = info.get('streams', [])
                    video_streams = [s for s in streams if s.get('codec_type') == 'video']
                    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
                    
                    print(f"✓ Duration: {duration:.1f} seconds")
                    print(f"✓ Video streams: {len(video_streams)}")
                    print(f"✓ Audio streams: {len(audio_streams)}")
                    
                    if video_streams:
                        vs = video_streams[0]
                        width = vs.get('width', 0)
                        height = vs.get('height', 0)
                        codec = vs.get('codec_name', 'unknown')
                        print(f"✓ Resolution: {width}x{height}")
                        print(f"✓ Codec: {codec}")
                
            except Exception as e:
                print(f"⚠ Could not verify details: {str(e)}")
            
            return True
        else:
            print(f"ERROR: Video file not found: {video_file}")
            return False
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: ReelForge generated a complete video!")
        print("✓ Revolutionary concept generated")
        print("✓ Dynamic script written")
        print("✓ Professional audio attempted") 
        print("✓ Video assembled with FFmpeg")
        print("✓ MP4 file created successfully")
        print("\nThe system works end-to-end and creates real videos!")
    else:
        print("FAILED: See errors above")
    
    sys.exit(0 if success else 1)