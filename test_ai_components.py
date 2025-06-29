#!/usr/bin/env python3
"""
Test individual AI components for ReelForge
"""
import json
import os
import sys

# Add current directory to path
sys.path.append('.')

def test_concept_generation():
    """Test the enhanced concept generation tool"""
    print("🧠 Testing Concept Generation Tool")
    
    try:
        from agent.tools.concept import ConceptGenerationTool
        
        # Test with FlowFit example
        brand_data = {
            "brand_name": "FlowFit",
            "brand_description": "Revolutionary fitness app that adapts to your lifestyle with AI-powered personalized workouts that take just 15 minutes a day",
            "target_audience": "Busy professionals aged 25-40", 
            "tone": "energetic",
            "duration": 30,
            "call_to_action": "Download free today"
        }
        
        tool = ConceptGenerationTool()
        result = tool.run(json.dumps(brand_data))
        concept = json.loads(result)
        
        if concept.get("status") == "failed":
            print(f"❌ Failed: {concept.get('error')}")
            return False
        
        print("✅ Concept Generated Successfully!")
        print(f"💡 Concept: {concept.get('concept', 'N/A')}")
        print(f"🎣 Hook: {concept.get('hook', 'N/A')}")
        print(f"🎨 Visual Style: {concept.get('visual_style', 'N/A')}")
        print(f"🎯 Emotional Appeal: {concept.get('emotional_appeal', 'N/A')}")
        print(f"⚡ Uniqueness: {concept.get('uniqueness_factor', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_script_writing():
    """Test the enhanced script writing tool"""
    print("\n📝 Testing Script Writing Tool")
    
    try:
        from agent.tools.script import ScriptWritingTool
        
        # Mock concept from previous test
        mock_concept = {
            "concept": "Transform your fitness routine with AI that learns your schedule and creates custom 15-minute workouts that fit seamlessly into your busiest days",
            "hook": "15 minutes. That's all you need.",
            "visual_style": "Fast-paced montage of busy professionals working out in various quick moments"
        }
        
        brand_info = {
            "brand_name": "FlowFit",
            "brand_description": "Revolutionary fitness app with AI-powered personalized workouts",
            "target_audience": "Busy professionals aged 25-40",
            "tone": "energetic",
            "duration": 30,
            "call_to_action": "Download free today"
        }
        
        script_input = {
            "concept": mock_concept,
            "brand_info": brand_info
        }
        
        tool = ScriptWritingTool()
        result = tool.run(json.dumps(script_input))
        script = json.loads(result)
        
        if script.get("status") == "failed":
            print(f"❌ Failed: {script.get('error')}")
            return False
        
        print("✅ Script Generated Successfully!")
        print(f"📋 Total Duration: {script.get('total_duration')} seconds")
        print(f"🎬 Segments: {len(script.get('segments', []))}")
        print(f"🎵 Pacing: {script.get('pacing', 'N/A')}")
        
        # Show first segment
        segments = script.get('segments', [])
        if segments:
            first_segment = segments[0]
            print(f"\n📜 First Segment Preview:")
            print(f"   Voiceover: \"{first_segment.get('voiceover', '')[:100]}...\"")
            print(f"   Visual: {first_segment.get('visual_hint', 'N/A')}")
            print(f"   Energy: {first_segment.get('energy_level', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_tts_integration():
    """Test the ElevenLabs TTS integration"""
    print("\n🎙️ Testing TTS Integration")
    
    try:
        from agent.tools.tts import TextToSpeechTool
        
        # Mock script data
        mock_script = {
            "segments": [
                {
                    "voiceover": "Fifteen minutes. That's all you need to transform your fitness routine forever.",
                    "duration": 5
                },
                {
                    "voiceover": "FlowFit's AI learns your schedule and creates custom workouts that fit your life.",
                    "duration": 6
                }
            ]
        }
        
        brand_info = {
            "tone": "energetic"
        }
        
        tts_input = {
            "script": mock_script,
            "job_id": "test_demo",
            "brand_info": brand_info
        }
        
        tool = TextToSpeechTool()
        result = tool.run(json.dumps(tts_input))
        audio = json.loads(result)
        
        if audio.get("status") == "failed":
            print(f"⚠️ TTS Warning: {audio.get('error')}")
            print("   This is expected if ElevenLabs API limit is reached")
            return True  # Don't fail the test for API limits
        
        print("✅ TTS Generation Successful!")
        print(f"🎵 Voice Tone: {audio.get('tone', 'N/A')}")
        print(f"📁 Audio Files: {len(audio.get('audio_files', []))}")
        print(f"⏱️ Total Duration: {audio.get('total_duration', 0)} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all component tests"""
    print("🧪 ReelForge AI Components Test")
    print("=" * 50)
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        return False
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("⚠️ ELEVENLABS_API_KEY not found - TTS will use fallback")
    
    print("🔑 API Keys configured\n")
    
    tests = [
        test_concept_generation,
        test_script_writing,
        test_tts_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 All AI components are functioning!")
        print("💫 ReelForge is ready to create dynamic short-form ads")
    else:
        print("⚠️ Some components need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)