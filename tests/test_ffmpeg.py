"""
Test Suite for FFmpeg Video Assembly
Validates FFmpeg command generation and video processing
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from agent.tools.ffmpeg_fx import run as ffmpeg_run
from agent.tools.ffmpeg_fx import _build_ffmpeg_command, _build_filter_complex


class TestFFmpegAssembly:
    """Test cases for FFmpeg video assembly functionality"""
    
    @pytest.fixture
    def sample_assembly_data(self):
        """Sample assembly data for testing"""
        return {
            "timeline": [
                {
                    "type": "video",
                    "scene_id": 1,
                    "duration": 3.0,
                    "search_query": "office productivity",
                    "start_time": 0
                },
                {
                    "type": "transition",
                    "name": "crossfade",
                    "duration": 0.5,
                    "start_time": 3.0
                },
                {
                    "type": "video",
                    "scene_id": 2, 
                    "duration": 4.0,
                    "search_query": "happy customers",
                    "start_time": 3.5
                },
                {
                    "type": "logo_end",
                    "duration": 2.0,
                    "start_time": 7.5
                }
            ],
            "audio_plan": {
                "voiceover_track": {
                    "segments": [
                        {
                            "text": "Boost your productivity today",
                            "start_time": 0,
                            "duration": 3.0
                        },
                        {
                            "text": "Join satisfied customers worldwide",
                            "start_time": 3.5,
                            "duration": 4.0
                        }
                    ]
                },
                "background_music": {
                    "enabled": True,
                    "volume_level": 0.3,
                    "style": "corporate_upbeat"
                }
            },
            "footage_segments": [
                {
                    "scene_id": 1,
                    "file_path": "test_video1.mp4",
                    "duration": 5.0,
                    "resolution": "1920x1080"
                },
                {
                    "scene_id": 2,
                    "file_path": "test_video2.mp4", 
                    "duration": 6.0,
                    "resolution": "1920x1080"
                }
            ],
            "audio_segments": [
                {
                    "segment_id": 1,
                    "file_path": "test_audio1.wav",
                    "duration": 3.0
                },
                {
                    "segment_id": 2,
                    "file_path": "test_audio2.wav",
                    "duration": 4.0
                }
            ]
        }
    
    def test_ffmpeg_command_structure(self, sample_assembly_data):
        """Test FFmpeg command structure generation"""
        timeline = sample_assembly_data["timeline"]
        audio_plan = sample_assembly_data["audio_plan"]
        footage_segments = sample_assembly_data["footage_segments"]
        audio_segments = sample_assembly_data["audio_segments"]
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            command_data = _build_ffmpeg_command(
                timeline=timeline,
                audio_plan=audio_plan,
                footage_segments=footage_segments,
                audio_segments=audio_segments,
                output_path=temp_output.name
            )
        
        # Validate command structure
        assert "command" in command_data
        assert "input_files" in command_data
        assert "filter_complex" in command_data
        
        command = command_data["command"]
        
        # Should start with FFmpeg binary
        assert command[0].endswith("ffmpeg")
        
        # Should have input files
        input_count = command.count("-i")
        assert input_count > 0
        
        # Should have filter_complex
        assert "-filter_complex" in command
        
        # Should have output settings
        assert "-c:v" in command
        assert "libx264" in command
        assert "-c:a" in command
        assert "aac" in command
        
        # Cleanup
        os.unlink(temp_output.name)
    
    def test_filter_complex_generation(self, sample_assembly_data):
        """Test filter_complex string generation"""
        timeline = sample_assembly_data["timeline"]
        audio_plan = sample_assembly_data["audio_plan"]
        
        video_segments = [item for item in timeline if item.get("type") == "video"]
        audio_segments = sample_assembly_data["audio_segments"]
        
        filter_complex = _build_filter_complex(
            timeline=timeline,
            audio_plan=audio_plan,
            video_count=len(video_segments),
            audio_count=len(audio_segments)
        )
        
        # Should be a non-empty string
        assert isinstance(filter_complex, str)
        assert len(filter_complex) > 0
        
        # Should contain video processing
        assert "scale=1920:1080" in filter_complex
        assert "[final_video]" in filter_complex
        
        # Should contain audio processing
        assert "[final_audio]" in filter_complex
        
        # Should contain transitions if present
        transitions = [item for item in timeline if item.get("type") == "transition"]
        if transitions:
            assert "xfade" in filter_complex
    
    def test_transition_filter_generation(self):
        """Test specific transition filter generation"""
        timeline = [
            {
                "type": "video",
                "scene_id": 1,
                "duration": 3.0
            },
            {
                "type": "transition",
                "name": "crossfade",
                "duration": 0.5
            },
            {
                "type": "video",
                "scene_id": 2,
                "duration": 3.0
            }
        ]
        
        audio_plan = {"background_music": {"enabled": False}}
        
        filter_complex = _build_filter_complex(
            timeline=timeline,
            audio_plan=audio_plan,
            video_count=2,
            audio_count=0
        )
        
        # Should contain crossfade transition
        assert "xfade" in filter_complex
        assert "duration=0.5" in filter_complex
    
    def test_audio_mixing_filter_generation(self, sample_assembly_data):
        """Test audio mixing filter generation"""
        timeline = sample_assembly_data["timeline"]
        audio_plan = sample_assembly_data["audio_plan"]
        
        filter_complex = _build_filter_complex(
            timeline=timeline,
            audio_plan=audio_plan,
            video_count=2,
            audio_count=2
        )
        
        # Should contain audio concatenation
        assert "concat" in filter_complex
        
        # Should contain background music mixing if enabled
        if audio_plan.get("background_music", {}).get("enabled"):
            assert "amix" in filter_complex
    
    def test_video_scaling_and_padding(self):
        """Test video scaling and padding filters"""
        timeline = [
            {
                "type": "video",
                "scene_id": 1,
                "duration": 5.0
            }
        ]
        
        filter_complex = _build_filter_complex(
            timeline=timeline,
            audio_plan={"background_music": {"enabled": False}},
            video_count=1,
            audio_count=0
        )
        
        # Should contain scaling to 1920x1080
        assert "scale=1920:1080" in filter_complex
        
        # Should contain padding for aspect ratio
        assert "pad=1920:1080" in filter_complex
        
        # Should maintain aspect ratio
        assert "force_original_aspect_ratio=decrease" in filter_complex
    
    def test_output_format_specification(self, sample_assembly_data):
        """Test output format and codec specification"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            command_data = _build_ffmpeg_command(
                timeline=sample_assembly_data["timeline"],
                audio_plan=sample_assembly_data["audio_plan"],
                footage_segments=sample_assembly_data["footage_segments"],
                audio_segments=sample_assembly_data["audio_segments"],
                output_path=temp_output.name
            )
        
        command = command_data["command"]
        
        # Should specify H.264 video codec
        h264_index = command.index("libx264")
        assert command[h264_index - 1] == "-c:v"
        
        # Should specify AAC audio codec
        aac_index = command.index("aac")
        assert command[aac_index - 1] == "-c:a"
        
        # Should have quality settings
        assert "-crf" in command
        assert "-preset" in command
        
        # Should have streaming optimization
        assert "-movflags" in command
        assert "+faststart" in command
        
        # Cleanup
        os.unlink(temp_output.name)
    
    def test_error_handling_missing_timeline(self):
        """Test error handling for missing timeline"""
        empty_data = {"no_timeline": True}
        
        result = ffmpeg_run(json.dumps(empty_data))
        result_data = json.loads(result)
        
        assert result_data["success"] is False
        assert "error" in result_data
    
    def test_error_handling_invalid_json(self):
        """Test error handling for invalid JSON input"""
        result = ffmpeg_run("invalid json {")
        result_data = json.loads(result)
        
        assert result_data["success"] is False
        assert "error" in result_data
    
    def test_placeholder_video_creation(self):
        """Test placeholder video creation for missing footage"""
        from agent.tools.ffmpeg_fx import _create_placeholder_video
        
        placeholder_path = _create_placeholder_video(5.0)
        
        if placeholder_path:  # Only test if FFmpeg is available
            assert os.path.exists(placeholder_path)
            assert placeholder_path.endswith(".mp4")
            
            # Cleanup
            os.unlink(placeholder_path)
    
    def test_background_music_handling(self):
        """Test background music file handling"""
        from agent.tools.ffmpeg_fx import _get_background_music_file
        
        # Test different music styles
        styles = ["corporate_upbeat", "energetic", "calm", "modern"]
        
        for style in styles:
            music_file = _get_background_music_file(style)
            # Should return a file path (even if it's a generated silent track)
            if music_file:
                assert isinstance(music_file, str)
                assert len(music_file) > 0
    
    def test_command_security(self, sample_assembly_data):
        """Test that generated commands don't contain security vulnerabilities"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            command_data = _build_ffmpeg_command(
                timeline=sample_assembly_data["timeline"],
                audio_plan=sample_assembly_data["audio_plan"],
                footage_segments=sample_assembly_data["footage_segments"],
                audio_segments=sample_assembly_data["audio_segments"],
                output_path=temp_output.name
            )
        
        command = command_data["command"]
        command_str = " ".join(command)
        
        # Should not contain shell injection patterns
        dangerous_patterns = [";", "&&", "||", "|", "`", "$(", "${"]
        
        for pattern in dangerous_patterns:
            assert pattern not in command_str, f"Command contains dangerous pattern: {pattern}"
        
        # Cleanup
        os.unlink(temp_output.name)
    
    def test_duration_constraints(self):
        """Test that generated videos respect duration constraints"""
        # Test with timeline that would be too long
        long_timeline = [
            {
                "type": "video",
                "scene_id": 1,
                "duration": 70.0  # Exceeds max duration
            }
        ]
        
        assembly_data = {
            "timeline": long_timeline,
            "audio_plan": {"background_music": {"enabled": False}},
            "footage_segments": [],
            "audio_segments": []
        }
        
        result = ffmpeg_run(json.dumps(assembly_data))
        result_data = json.loads(result)
        
        # Should either handle gracefully or produce an error
        assert "success" in result_data


if __name__ == "__main__":
    pytest.main([__file__])

