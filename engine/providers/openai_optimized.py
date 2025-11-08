"""
Optimized OpenAI provider for Luma AI compatibility.
"""

import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from interfaces.text_generator import TextGenerator


class OptimizedOpenAIProvider(TextGenerator):
    """Optimized OpenAI provider for perfect Luma AI compatibility."""

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)

    def create_cutting_edge_prompts(self, architecture: Dict[str, Any], 
                                  service_type: str = "luma") -> List[Dict[str, Any]]:
        """Generate service-specific prompts for each scene."""
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        return scenes  # Already optimized in architect_complete_video

    def architect_complete_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create Luma-optimized video architecture."""
        
        product_image_note = ""
        if brand_info.get('product_image_url'):
            product_image_note = """
PRODUCT IMAGE KEYFRAME:
- Scene 1 MUST animate FROM the provided product image
- Describe smooth camera movement starting from the static product image
- Example: "Slow dolly out from product close-up revealing environment"
"""

        prompt = f"""You are an expert video architect creating Luma AI Ray-2 compatible prompts.

BRAND: {brand_info.get('brand_name', 'Brand')}
PRODUCT: {brand_info.get('brand_description', 'Product')}
AUDIENCE: {brand_info.get('target_audience', 'general')}
BENEFITS: {brand_info.get('key_benefits', 'benefits')}
CTA: {brand_info.get('call_to_action', 'Take action')}
{product_image_note}

CRITICAL LUMA AI REQUIREMENTS:
🎯 Each luma_prompt MUST be EXACTLY 40-45 words
🎯 MUST include explicit camera movement: dolly in/out, tracking shot, crane up/down, orbit around, slow zoom, static shot
🎯 MUST describe lighting: soft diffused, hard directional, golden hour, rim lighting, ambient glow
🎯 MUST specify composition: shallow/deep depth of field, foreground/background elements
🎯 MUST include colors/textures: metallic, wooden, matte, glossy, vibrant, muted
🎯 Scenes 2&3 MUST start with transition: "Scene transitions to...", "Cut to...", "Camera reveals..."
🎯 NO text, words, letters, signs, readable content
🎯 NO face close-ups or talking heads
🎯 Focus on product, hands, environments, actions

SCRIPT REQUIREMENTS:
🎯 Each script_line: EXACTLY 16-18 words (perfect for 6-second timing)
🎯 Total unified_script: EXACTLY 50-54 words
🎯 Natural speech rhythm, clear pronunciation

Structure: Hook → Problem → Solution (6s each = 18s total)

Respond ONLY in this JSON format:

{{
    "creative_vision": {{
        "overall_concept": "Complete brand narrative in 1-2 sentences",
        "visual_style": "modern|luxury|minimal|dynamic",
        "color_palette": ["Primary color", "Secondary color", "Accent color"],
        "mood": "energetic|inspiring|professional|warm",
        "brand_story_arc": "hook → problem → solution"
    }},
    "audio_architecture": {{
        "voice_gender": "male|female",
        "voice_tone": "energetic|professional|warm|friendly",
        "energy_level": "high|medium|low",
        "music_style": "cinematic|upbeat|ambient|electronic",
        "tempo_bpm": 120,
        "total_duration": 18
    }},
    "scene_architecture": {{
        "total_duration": 18,
        "scenes": [
            {{
                "scene_id": 1,
                "role": "hook",
                "purpose": "Product introduction with visual impact",
                "duration": 6,
                "visual_concept": "High-level scene description focusing on product and environment (2-3 sentences)",
                "luma_prompt": "EXACTLY 40-45 words. MUST include: (1) Camera movement (dolly/tracking/crane/orbit/zoom/static), (2) Lighting type, (3) Depth of field, (4) Colors/textures, (5) Product-focused action. NO text/faces.",
                "script_line": "EXACTLY 16-18 words for 6-second narration",
                "audio_cues": "Background sounds and ambient audio",
                "music_cues": "Music direction for this segment",
                "brand_alignment": "How this reinforces brand identity"
            }},
            {{
                "scene_id": 2,
                "role": "problem",
                "purpose": "Demonstrate pain point or challenge",
                "duration": 6,
                "visual_concept": "Problem demonstration through environment and action (2-3 sentences)",
                "luma_prompt": "EXACTLY 40-45 words. START with 'Scene transitions to...' or 'Cut to...'. MUST include: (1) Camera movement, (2) Lighting, (3) Depth of field, (4) Colors/textures, (5) Problem visualization. NO text/faces.",
                "script_line": "EXACTLY 16-18 words for 6-second narration",
                "audio_cues": "Sounds that emphasize the problem",
                "music_cues": "Music tension or concern",
                "brand_alignment": "How this sets up the solution"
            }},
            {{
                "scene_id": 3,
                "role": "solution",
                "purpose": "Product solving problem with clear CTA",
                "duration": 6,
                "visual_concept": "Solution demonstration and transformation (2-3 sentences)",
                "luma_prompt": "EXACTLY 40-45 words. START with 'Scene transitions to...' or 'Cut to...'. MUST include: (1) Dynamic camera movement, (2) Bright/uplifting lighting, (3) Depth of field, (4) Brand colors/textures, (5) Solution demonstration. NO text/faces.",
                "script_line": "EXACTLY 16-18 words including clear call to action",
                "audio_cues": "Positive resolution sounds",
                "music_cues": "Uplifting resolution music",
                "brand_alignment": "How this drives conversion"
            }}
        ]
    }},
    "unified_script": "EXACTLY 50-54 words combining all 3 scene scripts"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            architecture = json.loads(content)
            
            # Validate and optimize
            return self._validate_and_optimize(architecture)
            
        except Exception as e:
            raise ValueError(f"OpenAI generation failed: {e}")

    def _validate_and_optimize(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and optimize for Luma compatibility."""
        
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        
        for i, scene in enumerate(scenes):
            # Validate Luma prompt word count
            luma_prompt = scene.get('luma_prompt', '')
            words = luma_prompt.split()
            
            if len(words) < 40:
                # Expand prompt to meet requirements
                scene['luma_prompt'] = self._expand_luma_prompt(luma_prompt, scene.get('role'))
            elif len(words) > 45:
                # Trim prompt to meet requirements
                scene['luma_prompt'] = ' '.join(words[:45])
            
            # Validate script timing
            script = scene.get('script_line', '')
            script_words = script.split()
            
            if len(script_words) < 16:
                # Expand script
                scene['script_line'] = self._expand_script(script, scene.get('role'))
            elif len(script_words) > 18:
                # Trim script
                scene['script_line'] = ' '.join(script_words[:18])
        
        # Update unified script
        all_scripts = [s.get('script_line', '') for s in scenes]
        architecture['unified_script'] = ' '.join(all_scripts)
        
        return architecture

    def _expand_luma_prompt(self, prompt: str, role: str) -> str:
        """Expand Luma prompt to meet 40-45 word requirement."""
        
        additions = {
            'hook': 'with cinematic composition and professional color grading showcasing premium product details',
            'problem': 'emphasizing environmental chaos and visual contrast through strategic lighting and framing techniques',
            'solution': 'highlighting brand transformation with dynamic visual storytelling and compelling product presentation'
        }
        
        addition = additions.get(role, 'with enhanced visual storytelling and cinematic production value')
        expanded = f"{prompt} {addition}"
        
        # Ensure exactly 40-45 words
        words = expanded.split()
        if len(words) > 45:
            return ' '.join(words[:45])
        elif len(words) < 40:
            return f"{expanded} featuring professional cinematography and compelling visual narrative"
        
        return expanded

    def _expand_script(self, script: str, role: str) -> str:
        """Expand script to meet 16-18 word requirement."""
        
        if role == 'hook':
            return f"{script} Experience the difference today."
        elif role == 'problem':
            return f"{script} It's time for a better solution."
        else:  # solution
            return f"{script} Don't wait, act now."
