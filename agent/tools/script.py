"""
Script Writing Tool
Creates dynamic, engaging scripts for short-form video ads
"""
import json
import os
from openai import OpenAI

class ScriptWritingTool:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            concept = data.get('concept', {})
            brand_info = data.get('brand_info', {})
            
            # Extract key information
            brand_name = brand_info.get('brand_name', 'Unknown Brand')
            description = brand_info.get('brand_description', '')
            target_audience = brand_info.get('target_audience', 'general audience')
            tone = brand_info.get('tone', 'professional')
            duration = brand_info.get('duration', 30)
            cta = brand_info.get('call_to_action', 'Learn more')
            
            concept_text = concept.get('concept', 'Revolutionary solution')
            hook = concept.get('hook', 'Transform your business today')
            
            prompt = f"""
            Create a DYNAMIC, ENGAGING script for a {duration}-second short-form video ad that will captivate viewers instantly.
            
            BRAND CONTEXT:
            - Brand: {brand_name}
            - Description: {description}
            - Target: {target_audience}
            - Tone: {tone}
            - Call to Action: {cta}
            
            CREATIVE DIRECTION:
            - Concept: {concept_text}
            - Opening Hook: {hook}
            
            SCRIPT REQUIREMENTS:
            1. INSTANT ATTENTION - Hook viewers in the first 3 seconds
            2. EMOTIONAL CONNECTION - Create desire and urgency
            3. CLEAR VALUE PROPOSITION - Show tangible benefits
            4. STRONG CALL TO ACTION - Drive immediate action
            5. PERFECT PACING - Match the {duration}-second timeframe
            
            STRUCTURE REQUIREMENTS:
            - 3-5 segments with precise timing
            - Each segment 5-10 seconds max
            - Natural speech patterns optimized for AI voice generation
            - Visual descriptions that guide dynamic video creation
            - Seamless transitions between segments
            
            OUTPUT FORMAT (JSON):
            {{
                "segments": [
                    {{
                        "segment": 1,
                        "start_time": 0,
                        "duration": 6,
                        "voiceover": "Compelling voiceover text",
                        "visual_hint": "Dynamic visual description",
                        "energy_level": "high/medium/low",
                        "emotion": "excitement/trust/urgency"
                    }}
                ],
                "total_duration": {duration},
                "script_style": "Dynamic short-form ad",
                "voice_notes": "Delivery instructions for TTS",
                "pacing": "Fast-paced with strategic pauses"
            }}
            
            Make this script irresistible and memorable - the kind that stops thumbs mid-scroll!
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert short-form video script writer who creates viral-worthy content. Your scripts stop scrollers in their tracks and drive immediate action."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8  # Higher creativity for dynamic content
            )
            
            script_result = response.choices[0].message.content
            
            # Parse and enhance the result
            script_data = json.loads(script_result)
            
            # Add metadata
            script_data.update({
                "brand_name": brand_name,
                "target_tone": tone,
                "generated_for": target_audience,
                "optimization": "short_form_engagement",
                "generated_at": "2024-06-29T09:05:00Z",
                "tool": "script_writing",
                "status": "success"
            })
            
            return json.dumps(script_data)
            
        except Exception as e:
            return json.dumps({
                "error": f"Script writing failed: {str(e)}",
                "status": "failed",
                "tool": "script_writing"
            })