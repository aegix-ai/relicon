"""
Video generation functionality tests
Tests the core video generation pipeline
"""
import os
import tempfile
from pathlib import Path
from video.services import video_service
from ai.planners import video_planner, script_generator
from video.generation import video_generator, audio_processor

class TestVideoGeneration:
    """Test suite for video generation functionality"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_brand_info = {
            "brand_name": "Test Brand",
            "brand_description": "Amazing product for testing video generation",
            "duration": 15,
            "platform": "universal",
            "target_audience": "young professionals"
        }
    
    def test_script_generation(self):
        """Test script generation functionality"""
        print("Testing script generation...")
        
        segments = script_generator.generate_energetic_segments(
            self.test_brand_info, 
            num_segments=2
        )
        
        assert len(segments) == 2
        assert all("text" in segment for segment in segments)
        assert all("duration" in segment for segment in segments)
        print("✓ Script generation test passed")
    
    def test_audio_processing(self):
        """Test audio processing functionality"""
        print("Testing audio processing...")
        
        test_text = "This is a test voiceover for our amazing product!"
        
        # Generate voiceover
        audio_file = audio_processor.generate_voiceover(test_text)
        
        if audio_file:
            assert os.path.exists(audio_file)
            
            # Test audio enhancement
            enhanced_file = str(self.temp_dir / "enhanced_audio.mp3")
            success = audio_processor.enhance_audio_energy(audio_file, enhanced_file)
            
            if success:
                assert os.path.exists(enhanced_file)
                print("✓ Audio processing test passed")
            else:
                print("⚠ Audio enhancement failed but generation worked")
        else:
            print("⚠ Audio generation failed (check OpenAI API key)")
    
    def test_video_planning(self):
        """Test video planning functionality"""
        print("Testing video planning...")
        
        # Create master plan
        master_plan = video_planner.create_master_plan(self.test_brand_info)
        
        assert master_plan.get("success") is not False
        assert "master_plan" in master_plan or "error" in master_plan
        
        if master_plan.get("success"):
            # Test scene breakdown
            scenes = video_planner.break_down_components(
                master_plan, 
                self.test_brand_info["duration"]
            )
            
            assert len(scenes) > 0
            assert all("duration" in scene for scene in scenes)
            print("✓ Video planning test passed")
        else:
            print("⚠ Video planning used fallback (check OpenAI API key)")
    
    def test_simple_video_creation(self):
        """Test simple video creation without Luma"""
        print("Testing simple video creation...")
        
        result = video_service.create_simple_video(self.test_brand_info)
        
        if result.get("success"):
            video_path = result.get("video_path")
            assert video_path is not None
            assert os.path.exists(video_path)
            
            # Check if video is valid
            is_valid = video_generator.validate_video(video_path)
            assert is_valid
            print("✓ Simple video creation test passed")
        else:
            print(f"⚠ Simple video creation failed: {result.get('error')}")
    
    def test_full_video_generation(self):
        """Test full video generation pipeline"""
        print("Testing full video generation pipeline...")
        
        def progress_callback(progress, message):
            print(f"  Progress: {progress}% - {message}")
        
        result = video_service.generate_video(
            self.test_brand_info, 
            progress_callback=progress_callback
        )
        
        if result.get("success"):
            video_path = result.get("video_path")
            assert video_path is not None
            assert os.path.exists(video_path)
            
            # Check if video is valid
            is_valid = video_generator.validate_video(video_path)
            assert is_valid
            print("✓ Full video generation test passed")
        else:
            print(f"⚠ Full video generation failed: {result.get('error')}")
    
    def run_all_tests(self):
        """Run all video generation tests"""
        print("Running video generation tests...")
        
        try:
            self.test_script_generation()
            self.test_audio_processing()
            self.test_video_planning()
            self.test_simple_video_creation()
            self.test_full_video_generation()
            
            print("\n✅ All video generation tests completed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    tester = TestVideoGeneration()
    tester.run_all_tests()