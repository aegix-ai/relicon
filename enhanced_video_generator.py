#!/usr/bin/env python3
"""
Enhanced AI Video Generation System with Comprehensive Planning
Creates professional videos with Luma AI and intelligent planning
"""
import argparse
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import requests
from openai import OpenAI
from luma_service import LumaVideoService
from ai_planner import VideoAdPlanner
from energetic_script_generator import EnergeticScriptGenerator

def make_advertisement_energetic(text):
    """Transform text to be more energetic and advertisement-style"""
    # Add engaging questions and energy
    energetic_patterns = [
        ("Are you", "Have you ever wondered if you're"),
        ("Do you", "Have you ever thought about whether you"),
        ("This is", "This is exactly what you've been looking for!"),
        ("We offer", "Get ready to experience"),
        ("Our product", "Discover the revolutionary"),
        ("You can", "You're about to"),
        ("It helps", "Watch how it transforms"),
        ("Benefits include", "Get ready for incredible benefits like"),
        ("Join", "Don't miss out - join"),
        ("Try", "Ready to try"),
        (".", "!"),  # Make statements more exciting
    ]
    
    energetic_text = text
    for old, new in energetic_patterns:
        energetic_text = energetic_text.replace(old, new)
    
    # Add hook questions at the start if not present
    if not any(starter in energetic_text.lower() for starter in ["have you", "are you", "do you", "ready to", "discover"]):
        if "tired" in energetic_text.lower() or "problem" in energetic_text.lower():
            energetic_text = "Have you ever faced this problem? " + energetic_text
        elif "solution" in energetic_text.lower() or "help" in energetic_text.lower():
            energetic_text = "Ready for the solution you've been waiting for? " + energetic_text
        else:
            energetic_text = "Have you ever wondered about this? " + energetic_text
    
    return energetic_text

def enhance_audio_energy(input_file, output_file):
    """Enhance audio with volume boost and energy processing using FFmpeg"""
    try:
        # FFmpeg command to boost volume by 10dB and add slight compression for punch
        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-af', 'volume=10dB,compand=attacks=0.3:decays=0.8:points=-80/-900|-45/-15|-27/-9:gain=5',
            '-c:a', 'libmp3lame', '-b:a', '320k',  # High quality MP3
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Audio enhancement failed: {result.stderr}")
            # Fall back to simple volume boost
            simple_cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-af', 'volume=8dB',
                output_file
            ]
            subprocess.run(simple_cmd, capture_output=True)
    except Exception as e:
        print(f"Error enhancing audio: {e}")
        # Copy original if enhancement fails
        shutil.copy2(input_file, output_file)

def progress_update(progress, message):
    """Send progress update that the Node.js server can parse"""
    print(f"PROGRESS:{progress}:{message}")
    sys.stdout.flush()

def create_enhanced_video_generation(brand_info, output_file):
    """
    Complete enhanced video generation pipeline
    """
    try:
        # Step 1: Create comprehensive AI plan with energetic script generation
        progress_update(10, "Creating comprehensive AI marketing plan")
        planner = VideoAdPlanner()
        script_generator = EnergeticScriptGenerator()
        
        # Generate energetic script segments first
        num_segments = min(4, max(2, brand_info.get('duration', 30) // 10))  # Smart segment calculation
        energetic_segments = script_generator.generate_energetic_segments(brand_info, num_segments)
        
        # Create comprehensive plan with energetic scripts integrated
        complete_plan = planner.create_complete_plan(brand_info)
        
        # Override with energetic scripts for better audio
        for i, scene in enumerate(complete_plan['detailed_scenes'][:len(energetic_segments)]):
            energetic_script = energetic_segments[i].get('voiceover_script', scene.get('voiceover', ''))
            scene['voiceover'] = energetic_script
            scene['energy_level'] = energetic_segments[i].get('energy_level', 'high')
            scene['emotional_trigger'] = energetic_segments[i].get('emotional_trigger', 'excitement')
            
        print("Enhanced plan now includes:")
        print(f"  📹 Video optimization: {len(complete_plan['detailed_scenes'])} scenes")
        print(f"  🎙️ Audio optimization: Energetic scripts with volume boost")
        print(f"  🎵 Music optimization: Component-specific prompts")
        print(f"  🖼️ Image optimization: Thumbnail and key frame guidance")
        
        print(f"Master Plan: {complete_plan['master_plan']}")
        print(f"Total scenes: {complete_plan['scene_count']} (with energetic scripts)")
        print(f"Total duration: {complete_plan['total_duration']}s")
        
        # Step 2: Generate energetic, charismatic voiceover audio
        progress_update(30, "Creating energetic advertisement-style voiceover")
        audio_files = []
        temp_dir = "/tmp/audio_segments"
        os.makedirs(temp_dir, exist_ok=True)
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        for i, scene in enumerate(complete_plan['detailed_scenes']):
            voiceover_text = scene.get('voiceover', '')
            if not voiceover_text:
                continue
                
            progress_update(30 + (i * 5), f"Generating energetic audio for scene {i+1}")
            
            # Transform text to be more energetic and advertisement-style
            energetic_text = make_advertisement_energetic(voiceover_text)
            
            # Generate TTS audio with energetic settings
            try:
                response = client.audio.speech.create(
                    model="tts-1-hd",  # Higher quality model
                    voice="alloy",     # More energetic voice
                    input=energetic_text,
                    speed=1.1          # Slightly faster for energy
                )
                
                raw_audio_file = f"{temp_dir}/scene_{i}_raw.mp3"
                response.stream_to_file(raw_audio_file)
                
                # Enhance audio with volume boost and energy processing
                enhanced_audio_file = f"{temp_dir}/scene_{i}_audio.mp3"
                enhance_audio_energy(raw_audio_file, enhanced_audio_file)
                
                if os.path.exists(enhanced_audio_file) and os.path.getsize(enhanced_audio_file) > 0:
                    audio_files.append(enhanced_audio_file)
                    os.remove(raw_audio_file)  # Clean up raw file
                else:
                    print(f"Warning: Enhanced audio file {i} is empty or missing")
                    
            except Exception as e:
                print(f"Error generating audio for scene {i}: {e}")
                continue
        
        if not audio_files:
            raise Exception("No audio files were generated")
        
        # Step 3: Generate video segments with Luma AI
        progress_update(50, "Generating professional video segments with Luma AI")
        
        luma_service = LumaVideoService()
        
        # Prepare segments for Luma AI with COST SAFEGUARD
        luma_segments = []
        max_segments = min(4, len(complete_plan['detailed_scenes']))  # Never exceed 4 segments
        
        print(f"COST SAFEGUARD: Limiting to {max_segments} segments (was {len(complete_plan['detailed_scenes'])})")
        
        for i, scene in enumerate(complete_plan['detailed_scenes'][:max_segments]):
            if i < len(audio_files):  # Only process scenes with audio
                segment = {
                    'index': i,
                    'duration': min(scene.get('duration', 5), 10),  # Cap at 10 seconds
                    'voiceover': scene.get('voiceover', ''),
                    'visual_prompt': scene.get('optimized_prompt', scene.get('visual_prompt', '')),
                    'aspect_ratio': '9:16'
                }
                luma_segments.append(segment)
        
        # Generate videos in parallel
        video_files = luma_service.generate_multiple_segments(
            luma_segments,
            progress_callback=progress_update
        )
        
        if not video_files:
            raise Exception("No video segments were generated by Luma AI")
        
        if len(video_files) != len(audio_files):
            print(f"Warning: Video count ({len(video_files)}) != Audio count ({len(audio_files)})")
            # Match arrays by taking minimum length
            min_length = min(len(video_files), len(audio_files))
            video_files = video_files[:min_length]
            audio_files = audio_files[:min_length]
        
        # Step 4: Combine video + audio segments
        progress_update(85, "Assembling final video with synchronized audio")
        
        combined_segments = []
        for i, (video_file, audio_file) in enumerate(zip(video_files, audio_files)):
            combined_file = f"/tmp/combined_segment_{i}.mp4"
            
            # Combine video with audio
            combine_cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                combined_file
            ]
            
            result = subprocess.run(combine_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(combined_file):
                combined_segments.append(combined_file)
            else:
                print(f"Warning: Failed to combine segment {i}, using video only")
                combined_segments.append(video_file)
        
        # Step 5: Concatenate all segments
        progress_update(95, "Finalizing complete video")
        
        if len(combined_segments) == 1:
            shutil.copy2(combined_segments[0], output_file)
        else:
            # Create concat list
            concat_list = "/tmp/concat_list.txt"
            with open(concat_list, "w") as f:
                for segment in combined_segments:
                    f.write(f"file '{segment}'\n")
            
            # Concatenate
            concat_cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list,
                "-c", "copy",
                output_file
            ]
            
            result = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")
        
        # Verify output
        if not os.path.exists(output_file):
            raise Exception("Output video file was not created")
        
        file_size = os.path.getsize(output_file)
        if file_size < 1000:
            raise Exception("Output video file is too small")
        
        # Cleanup
        for segment in combined_segments:
            try:
                os.remove(segment)
            except:
                pass
        
        progress_update(100, "Video generation completed successfully!")
        return True
        
    except Exception as e:
        raise Exception(f"Enhanced video generation failed: {e}")

def main():
    """Main entry point for video generation"""
    parser = argparse.ArgumentParser(description="Enhanced AI Video Generator")
    parser.add_argument("--brand-name", required=True, help="Brand name")
    parser.add_argument("--brand-description", required=True, help="Brand description")
    parser.add_argument("--target-audience", help="Target audience")
    parser.add_argument("--tone", default="professional", help="Tone")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    parser.add_argument("--call-to-action", help="Call to action")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--job-id", help="Job ID for tracking (optional)")
    
    args = parser.parse_args()
    
    try:
        progress_update(10, "Starting enhanced AI video generation")
        
        # Prepare brand info
        brand_info = {
            'brand_name': args.brand_name,
            'brand_description': args.brand_description,
            'target_audience': args.target_audience,
            'tone': args.tone,
            'duration': args.duration,
            'call_to_action': args.call_to_action
        }
        
        # Generate video
        create_enhanced_video_generation(brand_info, args.output)
        
        print(f"SUCCESS: Enhanced video generated at {args.output}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()