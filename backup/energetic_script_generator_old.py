#!/usr/bin/env python3
"""
Energetic Script Generator for Advertisement-Style Voiceovers
Creates charismatic, engaging scripts that sound human and professional
"""
import os
import json
from typing import Dict, List, Any
from openai import OpenAI

class EnergeticScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def generate_energetic_segments(self, brand_info: Dict[str, Any], num_segments: int = 3) -> List[Dict[str, Any]]:
        """Generate energetic advertisement-style script segments"""
        
        duration_per_segment = brand_info.get('duration', 30) // num_segments
        
        # Create energetic script with hook questions and excitement
        script_prompt = f"""
        Create {num_segments} ENERGETIC advertisement script segments for {brand_info.get('brand_name')}.
        
        BRAND INFO:
        - Product: {brand_info.get('brand_name')}
        - Description: {brand_info.get('brand_description')}
        - Target Audience: {brand_info.get('target_audience', 'general audience')}
        - Tone: Energetic, charismatic, professional advertisement
        - Call to Action: {brand_info.get('call_to_action', 'Try it today!')}
        
        SCRIPT REQUIREMENTS:
        - Sound like a charismatic TV commercial narrator, NOT like AI reading text
        - Each segment should be {duration_per_segment} seconds of speaking time
        - Start segments with engaging hook questions like:
          * "Have you ever wondered why...?"
          * "Are you tired of...?"
          * "Ready to discover the secret to...?"
          * "What if I told you there's a way to...?"
        - Use excitement, energy, and emotional triggers
        - Include natural speech patterns and emphasis
        - End with compelling transitions or calls-to-action
        - Avoid corporate jargon - make it conversational and human
        
        SEGMENT STRUCTURE:
        1. Hook Question + Problem (first segment)
        2. Solution Reveal + Benefits (middle segments)  
        3. Call-to-Action + Urgency (final segment)
        
        Respond in JSON format:
        {{
            "segments": [
                {{
                    "segment_id": 1,
                    "duration": {duration_per_segment},
                    "voiceover_script": "ENERGETIC script with hook questions and excitement",
                    "energy_level": "high/medium/urgent",
                    "emotional_trigger": "curiosity/excitement/urgency/solution"
                }}
            ],
            "overall_narrative": "Brief description of the story arc",
            "energy_progression": "How energy builds throughout the ad"
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": script_prompt}],
            response_format={"type": "json_object"},
            temperature=0.8  # Higher creativity for energetic content
        )
        
        script_data = json.loads(response.choices[0].message.content)
        return script_data['segments']
    
    def enhance_script_energy(self, script_text: str) -> str:
        """Enhance existing script with more energy and advertisement style"""
        
        enhancement_prompt = f"""
        Transform this script to be MORE ENERGETIC and charismatic for a professional advertisement:
        
        Original: "{script_text}"
        
        Make it:
        - Sound like a professional TV commercial narrator
        - Add hook questions if missing ("Have you ever...?", "Ready to...?")
        - Include excitement and energy markers
        - Use natural speech emphasis and rhythm
        - Make it conversational, not corporate
        - Add emotional triggers
        
        Return ONLY the enhanced script text, no explanations.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": enhancement_prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()

def test_energetic_generator():
    """Test the energetic script generator"""
    
    generator = EnergeticScriptGenerator()
    
    test_brand = {
        "brand_name": "FocusFlow AI",
        "brand_description": "AI-powered productivity app that eliminates distractions and boosts focus for remote workers",
        "target_audience": "remote workers and entrepreneurs", 
        "duration": 15,
        "call_to_action": "Download FocusFlow and reclaim your productivity!"
    }
    
    print("🎙️ TESTING ENERGETIC SCRIPT GENERATOR")
    print("=" * 50)
    
    segments = generator.generate_energetic_segments(test_brand, 3)
    
    for i, segment in enumerate(segments):
        print(f"\n📢 SEGMENT {i+1} ({segment.get('duration')}s)")
        print(f"Energy: {segment.get('energy_level')}")
        print(f"Trigger: {segment.get('emotional_trigger')}")
        print("-" * 30)
        print(f"Script: {segment.get('voiceover_script')}")
    
    print("\n✅ ENERGETIC SCRIPT GENERATION COMPLETE")

if __name__ == "__main__":
    test_energetic_generator()