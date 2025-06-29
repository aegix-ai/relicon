#!/usr/bin/env python3
"""
Complete end-to-end test of ReelForge video generation
"""
import json
import os
import sys
import time

# Add current directory to path
sys.path.append('.')

def test_complete_video_generation():
    """Test the complete pipeline from concept to video file"""
    print("🎬 Testing Complete Video Generation Pipeline")
    print("=" * 60)
    
    # Test brand data
    brand_data = {
        "brand_name": "FlowFit",
        "brand_description": "Revolutionary fitness app that adapts to your lifestyle with AI-powered personalized workouts that take just 15 minutes a day",
        "target_audience": "Busy professionals aged 25-40",
        "tone": "energetic",
        "duration": 30,
        "call_to_action": "Download free today"
    }
    
    job_id = "test_complete_pipeline"
    
    try:
        # Stage 1: Generate concept
        print("Stage 1: Generating revolutionary concept...")
        from agent.tools.concept import ConceptGenerationTool
        
        concept_tool = ConceptGenerationTool()
        concept_result = concept_tool.run(json.dumps(brand_data))
        concept_data = json.loads(concept_result)
        
        if concept_data.get("status") == "failed":
            print(f"❌ Concept generation failed: {concept_data.get('error')}")
            return False
        
        print(f"✅ Concept: {concept_data.get('concept', '')[:100]}...")
        print(f"🎣 Hook: {concept_data.get('hook', '')}")
        
        # Stage 2: Write script
        print("\nStage 2: Writing dynamic script...")
        from agent.tools.script import ScriptWritingTool
        
        script_tool = ScriptWritingTool()
        script_input = {
            "concept": concept_data,
            "brand_info": brand_data
        }
        script_result = script_tool.run(json.dumps(script_input))
        script_data = json.loads(script_result)
        
        if script_data.get("status") == "failed":
            print(f"❌ Script writing failed: {script_data.get('error')}")
            return False
        
        segments = script_data.get('segments', [])
        print(f"✅ Script with {len(segments)} segments generated")
        
        # Show segment preview
        if segments:
            print(f"   Segment 1: \"{segments[0].get('voiceover', '')[:60]}...\"")
        
        # Stage 3: Generate audio (optional - may fail due to API limits)
        print("\nStage 3: Generating voiceover audio...")
        from agent.tools.tts import TextToSpeechTool
        
        tts_tool = TextToSpeechTool()
        tts_input = {
            "script": script_data,
            "job_id": job_id,
            "brand_info": brand_data
        }
        
        try:
            audio_result = tts_tool.run(json.dumps(tts_input))
            audio_data = json.loads(audio_result)
            
            if audio_data.get("status") == "failed":
                print(f"⚠️ TTS failed: {audio_data.get('error')} - Continuing without audio")
                audio_data = {"audio_files": [], "total_duration": 30}
            else:
                print(f"✅ Audio generated: {len(audio_data.get('audio_files', []))} files")
        except Exception as e:
            print(f"⚠️ TTS error: {str(e)} - Continuing without audio")
            audio_data = {"audio_files": [], "total_duration": 30}
        
        # Stage 4: Create video with FFmpeg
        print("\nStage 4: Creating video with FFmpeg...")
        from agent.tools.ffmpeg_fx import FFmpegAssemblyTool
        
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
            print(f"❌ Video generation failed: {video_data.get('error')}")
            return False
        
        print(f"✅ Video created successfully!")
        
        # Verify video file exists
        video_file = f"assets/{job_id}_final.mp4"
        if os.path.exists(video_file):
            file_size = os.path.getsize(video_file)
            print(f"📁 Video file: {video_file}")
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"🎥 Resolution: {video_data.get('resolution', 'N/A')}")
            print(f"⏱️ Duration: {video_data.get('duration', 'N/A')} seconds")
            print(f"🎵 Audio included: {video_data.get('audio_included', False)}")
            
            # Additional verification
            try:
                import subprocess
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', '-show_streams', video_file
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    format_info = info.get('format', {})
                    print(f"📈 Actual duration: {float(format_info.get('duration', 0)):.2f}s")
                    
                    streams = info.get('streams', [])
                    video_streams = [s for s in streams if s.get('codec_type') == 'video']
                    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
                    
                    print(f"🎬 Video streams: {len(video_streams)}")
                    print(f"🎵 Audio streams: {len(audio_streams)}")
                    
                    if video_streams:
                        vs = video_streams[0]
                        print(f"📺 Video codec: {vs.get('codec_name', 'unknown')}")
                        print(f"📐 Resolution: {vs.get('width', 0)}x{vs.get('height', 0)}")
                    
            except Exception as e:
                print(f"⚠️ Could not verify video details: {str(e)}")
            
            return True
        else:
            print(f"❌ Video file not found: {video_file}")
            return False
        
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete test"""
    print("🧪 ReelForge Complete Pipeline Test")
    print("Testing full video generation from brand input to MP4 file")
    print()
    
    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return False
    
    # Check FFmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg available")
    except:
        print("❌ FFmpeg not available")
        return False
    
    print("✅ Prerequisites check passed")
    print()
    
    # Run the test
    success = test_complete_video_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE SUCCESS!")
        print("ReelForge successfully generated a full short-form video!")
        print("✅ Concept generation")
        print("✅ Script writing")
        print("✅ Audio generation (when possible)")
        print("✅ Video assembly with FFmpeg")
        print("✅ MP4 file creation")
        print()
        print("🎬 The system is working end-to-end!")
    else:
        print("❌ Test failed - see errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)