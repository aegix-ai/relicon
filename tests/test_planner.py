"""
Test Suite for Timeline Planner
Validates planning logic and timeline generation
"""
import pytest
import json
from agent.tools.planner import run as planner_run
from agent.planning import create_comprehensive_plan, validate_timeline


class TestTimelinePlanner:
    """Test cases for the timeline planner functionality"""
    
    def test_basic_timeline_creation(self):
        """Test basic timeline creation from script segments"""
        script_data = {
            "script_segments": [
                {
                    "scene": 1,
                    "voiceover": "Discover the future of productivity.",
                    "visual_hint": "Modern office environment with technology",
                    "duration": 3.5,
                    "emotional_tone": "professional"
                },
                {
                    "scene": 2, 
                    "voiceover": "Experience seamless workflow like never before.",
                    "visual_hint": "Person using product with satisfaction",
                    "duration": 4.0,
                    "emotional_tone": "engaging"
                },
                {
                    "scene": 3,
                    "voiceover": "Join thousands who trust our solution.",
                    "visual_hint": "Happy customers and success metrics",
                    "duration": 3.0,
                    "emotional_tone": "compelling"
                }
            ],
            "total_estimated_duration": 10.5
        }
        
        result = planner_run(json.dumps(script_data))
        timeline_data = json.loads(result)
        
        # Basic validation
        assert "timeline" in timeline_data
        assert "total_duration" in timeline_data
        assert "audio_plan" in timeline_data
        
        timeline = timeline_data["timeline"]
        
        # Should have video segments
        video_segments = [item for item in timeline if item.get("type") == "video"]
        assert len(video_segments) == 3
        
        # Should have transitions (between segments)
        transitions = [item for item in timeline if item.get("type") == "transition"]
        assert len(transitions) >= 2  # At least n-1 transitions for n segments
        
        # Should have proper timing
        assert timeline_data["total_duration"] > 0
        assert timeline_data["total_duration"] <= 60  # Within max duration
    
    def test_timeline_validation(self):
        """Test timeline validation logic"""
        valid_timeline = [
            {
                "type": "video",
                "scene_id": 1,
                "duration": 4.0,
                "search_query": "product introduction"
            },
            {
                "type": "transition",
                "name": "crossfade",
                "duration": 0.5
            },
            {
                "type": "video", 
                "scene_id": 2,
                "duration": 3.5,
                "search_query": "happy customers"
            },
            {
                "type": "logo_end",
                "duration": 2.0,
                "properties": {"call_to_action": True}
            }
        ]
        
        validation_result = validate_timeline(valid_timeline)
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_timeline_validation_fails_on_too_long(self):
        """Test timeline validation fails for overly long content"""
        long_timeline = [
            {
                "type": "video",
                "scene_id": 1,
                "duration": 70.0,  # Exceeds max duration
                "search_query": "very long content"
            }
        ]
        
        validation_result = validate_timeline(long_timeline)
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        assert any("exceeds maximum" in error for error in validation_result["errors"])
    
    def test_comprehensive_plan_creation(self):
        """Test comprehensive plan creation with concept and script"""
        concept = {
            "concept": "Revolutionary productivity app showcase",
            "tone": "professional",
            "visual_style": "modern and clean",
            "key_points": ["Efficiency", "Innovation", "Results"]
        }
        
        script_segments = [
            {
                "scene": 1,
                "voiceover": "Transform your workflow today.",
                "visual_hint": "Productivity tools in action",
                "duration": 4.0
            },
            {
                "scene": 2,
                "voiceover": "See results that matter.",
                "visual_hint": "Success metrics and growth",
                "duration": 3.5
            }
        ]
        
        plan = create_comprehensive_plan(concept, script_segments)
        
        # Validate plan structure
        assert "timeline" in plan
        assert "audio_plan" in plan
        assert "total_duration" in plan
        assert "quality_settings" in plan
        
        # Validate timeline content
        timeline = plan["timeline"]
        video_segments = [item for item in timeline if item.get("type") == "video"]
        assert len(video_segments) == 2
        
        # Validate audio plan
        audio_plan = plan["audio_plan"]
        assert "voiceover_track" in audio_plan
        assert "background_music" in audio_plan
        assert "mixing_settings" in audio_plan
    
    def test_transition_selection_logic(self):
        """Test intelligent transition selection"""
        from agent.planning import _select_optimal_transition
        
        # Test different scene type combinations
        transition1 = _select_optimal_transition(
            "product bottle close-up shot",
            "happy customer using product"
        )
        
        transition2 = _select_optimal_transition(
            "person exercising with energy",
            "product package and branding"
        )
        
        # Should return valid transition names
        valid_transitions = ['fade', 'crossfade', 'dissolve', 'wipe', 'slide', 'zoom', 'rotate']
        assert transition1 in valid_transitions
        assert transition2 in valid_transitions
        
        # Different contexts should potentially give different transitions
        # (though specific logic may vary)
        assert isinstance(transition1, str)
        assert isinstance(transition2, str)
    
    def test_audio_mixing_plan_creation(self):
        """Test audio mixing plan generation"""
        from agent.planning import _create_audio_mixing_plan
        
        script_segments = [
            {
                "voiceover": "First segment of the ad",
                "duration": 3.0
            },
            {
                "voiceover": "Second segment continues the story",
                "duration": 4.0
            }
        ]
        
        audio_plan = _create_audio_mixing_plan(script_segments, 7.0)
        
        # Validate structure
        assert "voiceover_track" in audio_plan
        assert "background_music" in audio_plan
        assert "mixing_settings" in audio_plan
        
        # Validate voiceover track
        voiceover_track = audio_plan["voiceover_track"]
        assert "segments" in voiceover_track
        assert len(voiceover_track["segments"]) == 2
        
        # Validate mixing settings
        mixing_settings = audio_plan["mixing_settings"]
        assert "voiceover_volume" in mixing_settings
        assert "background_volume" in mixing_settings
        assert mixing_settings["voiceover_volume"] >= mixing_settings["background_volume"]
    
    def test_error_handling_invalid_input(self):
        """Test error handling for invalid input"""
        # Test empty input
        result = planner_run("")
        result_data = json.loads(result)
        assert "error" in result_data
        
        # Test invalid JSON
        result = planner_run("invalid json {")
        result_data = json.loads(result)
        assert "error" in result_data
        
        # Test missing script segments
        result = planner_run('{"no_segments": true}')
        result_data = json.loads(result)
        assert "error" in result_data
    
    def test_timeline_duration_calculation(self):
        """Test accurate timeline duration calculation"""
        script_data = {
            "script_segments": [
                {
                    "scene": 1,
                    "voiceover": "Short intro.",
                    "visual_hint": "opening scene",
                    "duration": 2.5
                },
                {
                    "scene": 2,
                    "voiceover": "Longer middle section with more detail.",
                    "visual_hint": "main content",
                    "duration": 5.0
                },
                {
                    "scene": 3,
                    "voiceover": "Quick close.",
                    "visual_hint": "call to action",
                    "duration": 2.0
                }
            ]
        }
        
        result = planner_run(json.dumps(script_data))
        timeline_data = json.loads(result)
        
        # Calculate expected duration (segments + transitions + logo)
        segment_duration = sum(seg["duration"] for seg in script_data["script_segments"])
        timeline_duration = timeline_data["total_duration"]
        
        # Timeline should be longer than just segments (includes transitions and logo)
        assert timeline_duration > segment_duration
        assert timeline_duration <= 60  # Still within max limit


if __name__ == "__main__":
    pytest.main([__file__])

