"""
  OpenAI text generation provider implementation.
"""

import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from interfaces.text_generator import TextGenerator


class OpenAIProvider(TextGenerator):
    """OpenAI GPT text generation service implementation."""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}")
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    
    def architect_complete_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete video architecture from brand information."""
        target_duration = brand_info.get('duration', 30)
        
        # Expert modern advertising strategist prompt - product-focused commercial direction
        creative_prompt = f"""You are a world-class modern advertising strategist specializing in product-focused commercials that drive conversions.

Your mission: Create a blueprint for **one single modern advertisement** that showcases the product brilliantly with minimal talking heads.

Critical rules:
- The ad must follow: Hook → Pain → Solution → Call to Action structure
- Exactly **3 scenes**, each **5-6 seconds long** (total 15-18 seconds)
- Focus on PRODUCT DEMONSTRATION and lifestyle integration
- Minimize face-focused shots - prioritize product, environment, and action
- Show the product in use, its benefits, and real-world impact

Brand Information:
- Brand: {brand_info.get('brand_name', 'Brand')}
- Product/Service: {brand_info.get('brand_description', 'Product/service')}
- Target Audience: {brand_info.get('target_audience', 'general')}
- Key Benefits: {brand_info.get('key_benefits', 'benefits')}
- Call to Action: {brand_info.get('call_to_action', 'Take action')}

MODERN AD STRUCTURE REQUIREMENTS:

Scene 1 - HOOK (5-6s): Eye-catching product introduction or lifestyle moment
- Show product in action, stunning environment, or intriguing situation
- Focus on visual impact, not faces - wide shots, product close-ups, lifestyle context
- Create immediate curiosity about the product/service

Scene 2 - PAIN/PROBLEM (5-6s): Show the problem your product solves
- Demonstrate frustration, inefficiency, or limitation WITHOUT close-up faces
- Focus on situations, environments, actions that show the pain point
- Show hands, body language, problematic situations, environmental challenges

Scene 3 - SOLUTION + CTA (5-6s): Product solving the problem + clear call to action
- Demonstrate product benefits through action, results, transformation
- Show the product working, environment improving, lifestyle enhancing
- End with strong product branding and clear call to action

VISUAL DIRECTION REQUIREMENTS:
 Product Focus: Always show the actual product, its features, and benefits in action
 Lifestyle Integration: Show how product fits into real life scenarios
 Cinematic Quality: Professional lighting, camera movement, composition
 Environmental Storytelling: Use settings and situations to tell the story
 Action-Oriented: Show hands using product, situations changing, results happening
 Visual Variety: Mix wide shots, product close-ups, environmental shots, action sequences

For each scene, generate complete modern commercial architecture:
- scene_id: numeric index (1, 2, 3)
- duration: exactly 5-6 seconds (must total 15-18s)
- visual_concept: detailed cinematic description with camera, lighting, emotion, environment
- luma_prompt: cinema-quality prompt with specific cinematography direction, human expressions, lighting, and realistic details
- script_line: powerful narration aligned with 5-6s timing (15-18 words per scene max)
- audio_cues: cinematic sound design, ambient audio that enhances realism
- music_cues: emotional music direction that supports the visual storytelling

Audio Architecture Requirements:
- Total audio duration: exactly 15-18 seconds
- Total script: 45-55 words maximum across all 3 scenes
- Narration/Voiceover must fit within each 5-6s scene (15-18 words per scene)
- Music Layer: 15-18s emotional arc (Hook → Problem/Solution → Resolve)
- Sound FX: transitions between 5-6s segments
- All audio layers perfectly synchronized to 3 × 5-6s scene structure

Validation Requirements:
- Exactly 3 scenes, each exactly 5-6 seconds
- Total duration = 15-18 seconds (video + audio)
- Total script: 45-55 words maximum
- Each script_line fits within 5-6s scene timing (15-18 words max)
- No overspill between scenes
- One cohesive story arc across 15-18 seconds

Respond in JSON format:
{{
    "creative_vision": {{
        "overall_concept": "complete brand narrative concept",
        "visual_style": "cinematic style choice",
        "color_palette": ["primary_color", "secondary_color", "accent_color"],
        "mood": "emotional tone and energy",
        "brand_story_arc": "beginning-middle-end emotional journey"
    }},
    "audio_architecture": {{
        "voice_gender": "male/female",
        "voice_tone": "energetic/professional/warm",
        "energy_level": "high/medium/low",
        "music_style": "cinematic/electronic/orchestral",
        "tempo_bpm": 120,
        "total_duration": 18
    }},
    "scene_architecture": {{
        "total_duration": 18,
        "scenes": [
            {{
                "scene_id": 1,
                "duration": 6,
                "visual_concept": "modern commercial visual concept focusing on product introduction, lifestyle context, environmental storytelling, and eye-catching hook without face focus",
                "luma_prompt": "modern commercial prompt featuring product demonstration, lifestyle integration, professional cinematography, environmental action, and visual impact without talking heads",
                "script_line": "precise 6-second narration for hook scene (15-18 words max)",
                "audio_cues": "background sounds and ambient audio",
                "music_cues": "tempo, mood, instruments for this 6s segment"
            }},
            {{
                "scene_id": 2,
                "duration": 6,
                "visual_concept": "modern commercial visual concept showing problem/pain point through environmental situations, product absence, and lifestyle challenges without face-focused shots",
                "luma_prompt": "modern commercial prompt demonstrating problems through action, environmental context, situational challenges, and lifestyle pain points with minimal face shots",
                "script_line": "precise 6-second narration for problem/solution scene (15-18 words max)",
                "audio_cues": "background sounds and ambient audio", 
                "music_cues": "tempo, mood, instruments for this 6s segment"
            }},
            {{
                "scene_id": 3,
                "duration": 6,
                "visual_concept": "modern commercial visual concept showing product solution in action, lifestyle transformation, clear call-to-action, and product branding without face focus",
                "luma_prompt": "modern commercial prompt featuring product benefits demonstration, lifestyle improvement, clear branding, compelling call-to-action, and transformation results with minimal face shots",
                "script_line": "precise 6-second narration for resolution/CTA scene (15-18 words max)",
                "audio_cues": "background sounds and ambient audio",
                "music_cues": "tempo, mood, instruments for this 6s segment"
            }}
        ]
    }},
    "unified_script": "Complete 18-second narration script combining all 3 scene script lines, perfectly timed for 18s duration (45-55 words total)"
}}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": creative_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty architecture response")
        
        architecture = json.loads(content)
        
        print(f"DEBUG: OpenAI raw response total_duration = {architecture.get('scene_architecture', {}).get('total_duration', 'MISSING')}")
        
        # CRITICAL: Force exactly 18s architecture regardless of OpenAI response
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        
        # Ensure exactly 3 scenes with 6s each (3×6s = 18s total)
        while len(scenes) < 3:
            scenes.append({
                'scene_id': len(scenes) + 1,
                'duration': 6,
                'visual_concept': f'Professional scene {len(scenes) + 1}',
                'luma_prompt': f'High-quality scene {len(scenes) + 1}',
                'script_line': f'Scene {len(scenes) + 1} narration',
                'audio_cues': 'Professional audio',
                'music_cues': 'Enterprise music'
            })
        scenes = scenes[:3]  # Limit to exactly 3 scenes
        
        # Force exactly 6s per scene (3×6s = 18s total)
        for i, scene in enumerate(scenes):
            scene['duration'] = 6
            scene['scene_id'] = i + 1
        
        # Force total duration to 18s (3×6s scenes)
        architecture['scene_architecture']['scenes'] = scenes
        architecture['scene_architecture']['total_duration'] = 18
        architecture['audio_architecture']['total_duration'] = 18
        
        print(f"DEBUG: OpenAI forced total_duration = {architecture['scene_architecture']['total_duration']}")
        
        return architecture
    
    def create_cutting_edge_prompts(self, architecture: Dict[str, Any], service_type: str = "hailuo") -> List[Dict[str, Any]]:
        """Generate service-specific prompts for each scene."""
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])
        enhanced_scenes = []
        
        for i, scene in enumerate(scenes):
            # Use existing luma_prompt or visual_concept
            prompt = scene.get('luma_prompt') or scene.get('visual_concept', 'Professional commercial scene')
            
            # Optimize prompt length for service type
            if service_type.lower() == "hailuo":
                # Hailuo prefers shorter, concise prompts
                words = prompt.split()[:20]  # Max 20 words
                optimized_prompt = " ".join(words)
            else:
                # Luma can handle longer prompts
                optimized_prompt = prompt[:300]  # Max 300 chars
            
            enhanced_scene = {
                **scene,
                'hailuo_prompt': optimized_prompt,
                'luma_prompt': prompt,
                'scene_number': i + 1
            }
            enhanced_scenes.append(enhanced_scene)
        
        return enhanced_scenes
    
    def optimize_scene_prompts(self, scenes: List[Dict[str, Any]], service_type: str = "hailuo") -> List[Dict[str, Any]]:
        """
        Optimize scene prompts for specific video generation services.
        Removes legacy prompt generation and focuses on efficiency.
        
        Args:
            scenes: List of scene dictionaries
            service_type: Target service for optimization
            
        Returns:
            Optimized scenes with service-specific prompts
        """
        optimized_scenes = []
        
        for scene in scenes:
            # Get base prompt from luma_prompt or visual_concept
            base_prompt = scene.get('luma_prompt') or scene.get('visual_concept', '')
            
            if service_type.lower() == "hailuo":
                # Hailuo optimization: extract product-focused commercial essence
                # Prioritize: product, action, demonstration, environment, benefits
                words = base_prompt.split()
                
                # Extract essential commercial elements
                essential_keywords = []
                for word in words:
                    if any(key in word.lower() for key in ['product', 'demonstration', 'lifestyle', 'action', 'benefits', 'commercial', 'branding', 'transformation', 'solution', 'professional', 'modern', 'showcase']):
                        essential_keywords.append(word)
                
                # Build concise but product-focused prompt
                core_action = ' '.join(words[:8])  # Core product/action
                commercial_elements = ' '.join(essential_keywords[:4])  # Key commercial elements
                
                if commercial_elements:
                    scene['hailuo_prompt'] = f"{core_action}, {commercial_elements}"
                else:
                    scene['hailuo_prompt'] = ' '.join(words[:12])  # Fallback to first 12 words
                    
                scene['luma_prompt'] = base_prompt  # Keep full commercial description
            else:
                # Luma optimization: detailed descriptions
                scene['luma_prompt'] = base_prompt[:250]  # Optimal length for Luma
                scene['hailuo_prompt'] = " ".join(base_prompt.split()[:15])
            
            optimized_scenes.append(scene)
        
        return optimized_scenes
