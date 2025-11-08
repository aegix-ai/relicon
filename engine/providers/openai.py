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

    def _validate_and_clean_architecture(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the JSON architecture structure."""

        # Validate top-level structure
        required_top_level = ['creative_vision', 'audio_architecture', 'scene_architecture', 'unified_script']
        for field in required_top_level:
            if field not in architecture:
                raise ValueError(f"Missing required top-level field: {field}")

        # Validate creative_vision
        creative_vision = architecture.get('creative_vision', {})
        required_cv = ['overall_concept', 'visual_style', 'color_palette', 'mood', 'brand_story_arc']
        for field in required_cv:
            if field not in creative_vision:
                print(f"Warning: Missing creative_vision field: {field}")
                creative_vision[field] = "Not specified"

        # Ensure color_palette is a list
        if not isinstance(creative_vision.get('color_palette'), list):
            creative_vision['color_palette'] = ["Primary", "Secondary", "Accent"]

        # Validate audio_architecture
        audio_arch = architecture.get('audio_architecture', {})
        required_audio = ['voice_gender', 'voice_tone', 'energy_level', 'music_style', 'tempo_bpm', 'total_duration']
        for field in required_audio:
            if field not in audio_arch:
                print(f"Warning: Missing audio_architecture field: {field}")
                # Set defaults
                if field == 'tempo_bpm':
                    audio_arch[field] = 120
                elif field == 'total_duration':
                    audio_arch[field] = 18
                else:
                    audio_arch[field] = "professional"

        # Validate scene_architecture
        scene_arch = architecture.get('scene_architecture', {})
        if 'scenes' not in scene_arch:
            raise ValueError("Missing scenes in scene_architecture")

        scenes = scene_arch['scenes']
        if not isinstance(scenes, list):
            raise ValueError("Scenes must be a list")

        # Validate each scene
        required_scene_fields = [
            'scene_id', 'role', 'purpose', 'duration', 'visual_concept',
            'luma_prompt', 'script_line', 'audio_cues', 'music_cues', 'brand_alignment'
        ]

        for i, scene in enumerate(scenes):
            if not isinstance(scene, dict):
                raise ValueError(f"Scene {i+1} is not a valid object")

            for field in required_scene_fields:
                if field not in scene:
                    print(f"Warning: Scene {i+1} missing field: {field}")
                    # Set defaults
                    if field == 'scene_id':
                        scene[field] = i + 1
                    elif field == 'duration':
                        scene[field] = 6
                    elif field == 'role':
                        roles = ['hook', 'problem', 'solution']
                        scene[field] = roles[min(i, 2)]
                    else:
                        scene[field] = f"Scene {i+1} {field}"

            # Ensure strings are clean (no extra whitespace, newlines)
            for field in ['visual_concept', 'luma_prompt', 'script_line', 'audio_cues', 'music_cues', 'purpose', 'brand_alignment']:
                if field in scene and isinstance(scene[field], str):
                    # Clean up the string: remove extra whitespace and newlines
                    scene[field] = ' '.join(scene[field].split())

        # Validate unified_script
        if not isinstance(architecture.get('unified_script'), str):
            architecture['unified_script'] = ' '.join(
                scene.get('script_line', '') for scene in scenes
            )
        else:
            # Clean unified script
            architecture['unified_script'] = ' '.join(architecture['unified_script'].split())

        print(f"✅ Architecture JSON validated successfully")
        return architecture

    def _log_architecture_debug(self, architecture: Dict[str, Any]) -> None:
        """Log architecture in clean JSON format for debugging."""
        try:
            # Pretty print the JSON structure
            clean_json = json.dumps(architecture, indent=2, ensure_ascii=False)
            print("\n" + "="*80)
            print("CLEAN VIDEO ARCHITECTURE JSON:")
            print("="*80)
            print(clean_json)
            print("="*80 + "\n")

            # Log summary
            scenes = architecture.get('scene_architecture', {}).get('scenes', [])
            print(f"📋 Architecture Summary:")
            print(f"   Total Duration: {architecture.get('scene_architecture', {}).get('total_duration')}s")
            print(f"   Number of Scenes: {len(scenes)}")
            for scene in scenes:
                print(f"   - Scene {scene.get('scene_id')}: {scene.get('role')} ({scene.get('duration')}s)")
                print(f"     Prompt: {scene.get('luma_prompt', '')[:80]}...")
            print()

        except Exception as e:
            print(f"Warning: Could not log architecture debug: {e}")

    def architect_complete_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete video architecture from brand information."""
        target_duration = brand_info.get('duration', 30)
        product_image_url = brand_info.get('product_image_url')

        # Add product image context to the prompt
        product_image_note = ""
        if product_image_url:
            product_image_note = """
IMPORTANT - PRODUCT IMAGE PROVIDED:
- A product image has been provided and will be used as the STARTING KEYFRAME for Scene 1
- Scene 1 must describe a smooth, natural animation FROM this product image
- The luma_prompt for Scene 1 should describe how the product image comes to life, animates, or transitions into action
- Example: If the image shows a product on a table, Scene 1 could show the camera slowly pulling back to reveal the environment, or the product rotating to show its features
- The transition should feel natural and cinematic, building from the static product image
- Scenes 2 and 3 will be generated normally without keyframes
"""

        # Expert modern advertising strategist prompt - product-focused commercial direction
        creative_prompt = f"""You are a world-class modern advertising strategist specializing in product-focused commercials that drive conversions.

Your mission: Create a blueprint for **one single modern advertisement** that showcases the product brilliantly with minimal talking heads.

Critical rules:
- The ad must follow: Hook → Pain → Solution → Call to Action structure
- Exactly **3 scenes**, each **EXACTLY 5 seconds long** (total 15 seconds)
- Focus on PRODUCT DEMONSTRATION and lifestyle integration
- Minimize face-focused shots - prioritize product, environment, and action
- Show the product in use, its benefits, and real-world impact
- CRITICAL: Each scene MUST be 5 seconds (not 6, not 4) for perfect audio sync

Brand Information:
- Brand: {brand_info.get('brand_name', 'Brand')}
- Product/Service: {brand_info.get('brand_description', 'Product/service')}
- Target Audience: {brand_info.get('target_audience', 'general')}
- Key Benefits: {brand_info.get('key_benefits', 'benefits')}
- Call to Action: {brand_info.get('call_to_action', 'Take action')}
{product_image_note}
MODERN AD STRUCTURE REQUIREMENTS:

Scene 1 - HOOK (5s): Eye-catching product introduction or lifestyle moment
- Show product in action, stunning environment, or intriguing situation
- Focus on visual impact, not faces - wide shots, product close-ups, lifestyle context
- Create immediate curiosity about the product/service
{"- If product image provided: Describe smooth animation FROM the product image (camera movement, product rotation, environment reveal)" if product_image_url else ""}

Scene 2 - PAIN/PROBLEM (5s): Show the problem your product solves
- Demonstrate realistic scenarios where current solutions are inadequate or problematic
- Show authentic situations that highlight the need for a better solution
- Focus on genuine pain points: slow performance, inconvenience, inefficiency, or limitations
- Show hands interacting with problematic alternatives, frustrated body language, challenging situations
- Ensure all products shown are complete and functional (no disconnected parts or incomplete items)

Scene 3 - SOLUTION + CTA (5s): Product solving the problem + clear call to action
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
 REALISM RULES: 
 - All products must be shown as complete, functional units
 - No floating, disconnected, or incomplete components
 - Technology must have all necessary parts visible and connected
 - All interactions must be physically realistic and logical
 - Products should be shown in their proper context and environment

PRODUCT-AGNOSTIC EXAMPLES:
✅ GOOD Scene 2 Examples:
- Person struggling with slow, outdated version of the product
- Hands dealing with heavy, bulky, or inconvenient alternatives
- Frustration with malfunctioning or inefficient current solutions
- Environmental challenges showing need for better product

❌ BAD Scene 2 Examples:
- Incomplete products or floating components
- Disconnected parts without context
- Unrealistic interactions or impossible scenarios
- Products shown without necessary components

For each scene, generate complete modern commercial architecture:
- scene_id: numeric index (1, 2, 3)
- duration: EXACTLY 5 seconds (MUST total 15s)
- visual_concept: detailed cinematic description with camera, lighting, emotion, environment
- luma_prompt: cinema-quality prompt with specific cinematography direction, realistic details, NO faces
- script_line: powerful narration aligned with 5s timing (12-15 words per scene max)
- audio_cues: cinematic sound design, ambient audio that enhances realism
- music_cues: emotional music direction that supports the visual storytelling

Audio Architecture Requirements:
- Total audio duration: EXACTLY 15 seconds (not 16, not 18)
- Total script: 36-45 words maximum across all 3 scenes
- Narration/Voiceover must fit within each 5s scene (12-15 words per scene)
- Music Layer: 15s emotional arc (Hook → Problem/Solution → Resolve)
- Sound FX: transitions between 5s segments
- All audio layers perfectly synchronized to 3 × 5s scene structure

Validation Requirements:
- Exactly 3 scenes, each EXACTLY 5 seconds
- Total duration = EXACTLY 15 seconds (video + audio)
- Total script: 36-45 words maximum
- Each script_line fits within 5s scene timing (12-15 words max)
- No overspill between scenes
- One cohesive story arc across 15 seconds

LUMA AI RAY-2 BEST PRACTICES (CRITICAL FOR REALISTIC VIDEO GENERATION):

⚠️ PROMPT LENGTH: Each luma_prompt MUST be 40-55 words for optimal results

⚠️ CAMERA MOVEMENT (REQUIRED - Choose ONE per scene):
   - Slow dolly in/out (reveals subject gradually)
   - Smooth tracking shot (follows action/movement)
   - Gentle crane up/down (changes perspective)
   - Subtle arc/orbit around subject
   - Steady static shot with subject movement

⚠️ LIGHTING (REQUIRED - Be specific):
   - Natural: "soft window light", "golden hour glow", "overcast diffused light"
   - Studio: "soft key light with subtle rim lighting", "three-point lighting setup"
   - Environment: "warm ambient lighting", "cool blue workspace illumination"

⚠️ DEPTH & COMPOSITION (REQUIRED):
   - "shallow depth of field" (blurred background, subject focus)
   - "deep depth of field" (everything sharp from foreground to background)
   - Specify foreground/background elements for depth

⚠️ REALISTIC ELEMENTS (Make videos believable):
   - Use real-world environments: offices, cafes, homes, outdoors
   - Simple, achievable actions: hands typing, product rotating, walking, picking up objects
   - Natural physics: smooth movements, realistic speeds, gravity-appropriate
   - Avoid: complex transformations, impossible physics, overly dramatic effects

⚠️ SCENE TRANSITIONS (Scenes 2 & 3):
   - Start with: "Cut to...", "Scene transitions to...", "Camera reveals...", "Following..."
   - Ensure visual continuity between scenes

⚠️ NEVER INCLUDE:
   - Text, words, letters, signs, readable content, UI elements
   - Face close-ups, talking heads, faces as primary focus
   - Unrealistic effects, magic, impossible actions

✅ DO INCLUDE:
   - Product features and benefits in action
   - Hands using products naturally
   - Real environments (offices, homes, cafes, streets)
   - Smooth, natural movements
   - Clear product visibility

Respond ONLY in valid JSON format following this exact structure:

{{
    "creative_vision": {{
        "overall_concept": "string - complete brand narrative concept (1-2 sentences)",
        "visual_style": "string - cinematic style (e.g., modern, luxury, minimal)",
        "color_palette": ["string", "string", "string"],
        "mood": "string - emotional tone (e.g., energetic, inspiring, professional)",
        "brand_story_arc": "string - narrative flow (beginning → middle → end)"
    }},
    "audio_architecture": {{
        "voice_gender": "male|female",
        "voice_tone": "energetic|professional|warm|friendly|authoritative",
        "energy_level": "high|medium|low",
        "music_style": "cinematic|electronic|orchestral|ambient|upbeat",
        "tempo_bpm": 120,
        "total_duration": 15
    }},
    "scene_architecture": {{
        "total_duration": 15,
        "scenes": [
            {{
                "scene_id": 1,
                "role": "hook",
                "purpose": "string - what this scene achieves (e.g., introduces product with visual impact)",
                "duration": 5,
                "visual_concept": "string - high-level creative description of the scene (2-3 sentences, focus on product, environment, mood)",
                "luma_prompt": "string - CRITICAL: Detailed Luma AI Ray-2 video generation prompt (MUST BE 40-55 words for realistic results). REQUIRED elements: (1) ONE specific camera movement (slow dolly in/out, smooth tracking, gentle crane, subtle orbit, or static), (2) Specific lighting (natural/studio/ambient with details), (3) Depth of field specification (shallow/deep), (4) Real-world environment details, (5) Simple, realistic product action. Focus on REALISTIC, ACHIEVABLE visuals. NO text/words. NO face close-ups. NO impossible effects.",
                "script_line": "string - exact voiceover narration for this 5-second scene (12-15 words maximum)",
                "audio_cues": "string - background sounds and ambient audio (e.g., soft whoosh, product click, environmental ambience)",
                "music_cues": "string - music direction for this segment (e.g., building tension, uplifting crescendo)",
                "brand_alignment": "string - how this scene reinforces brand identity"
            }},
            {{
                "scene_id": 2,
                "role": "problem",
                "purpose": "string - what this scene achieves (e.g., demonstrates pain point or need)",
                "duration": 5,
                "visual_concept": "string - high-level creative description (2-3 sentences, show problem/challenge)",
                "luma_prompt": "string - CRITICAL: Detailed Luma AI Ray-2 prompt (MUST BE 40-55 words). Start with transition: 'Cut to...' or 'Scene transitions to...'. REQUIRED: (1) Camera movement, (2) Lighting, (3) Depth of field, (4) Real environment, (5) Simple, realistic problem demonstration through hands/objects/environment. Keep actions NATURAL and ACHIEVABLE. NO text/words. NO face close-ups. NO magic effects.",
                "script_line": "string - exact voiceover narration for this 5-second scene (12-15 words maximum)",
                "audio_cues": "string - background sounds that emphasize the problem",
                "music_cues": "string - music tension or concern",
                "brand_alignment": "string - how this scene sets up the solution"
            }},
            {{
                "scene_id": 3,
                "role": "solution",
                "purpose": "string - what this scene achieves (e.g., shows product solving problem + CTA)",
                "duration": 5,
                "visual_concept": "string - high-level creative description (2-3 sentences, show transformation and CTA)",
                "luma_prompt": "string - CRITICAL: Detailed Luma AI Ray-2 prompt (MUST BE 40-55 words). Start with transition. REQUIRED: (1) Smooth camera movement, (2) Bright/uplifting lighting, (3) Depth of field, (4) Real environment, (5) Clear product benefit through SIMPLE, REALISTIC actions. Show actual product features working naturally. NO text/words. NO face close-ups. NO unrealistic transformations.",
                "script_line": "string - exact voiceover narration with CTA for this 5-second scene (12-15 words maximum)",
                "audio_cues": "string - positive, resolution sounds",
                "music_cues": "string - uplifting, resolution music",
                "brand_alignment": "string - how this scene drives conversion"
            }}
        ]
    }},
    "unified_script": "string - complete 15-second narration combining all 3 scene scripts (36-45 words total)"
}}

CRITICAL JSON REQUIREMENTS:
- Output ONLY valid JSON (no markdown, no code blocks, no explanations)
- All string values must be properly escaped
- All fields are required - no null or missing values
- Follow exact field names and structure above
- Each luma_prompt must be EXACTLY 40-55 words (count carefully!) with realistic, achievable visuals
- Each script_line must be 12-15 words to fit 5 seconds
- Total unified_script must be 36-45 words (for 15 seconds total)
- Camera movements, lighting, depth of field, and realistic environments are MANDATORY in every luma_prompt
- Focus on SIMPLE, NATURAL actions that Luma can realistically generate"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": creative_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty architecture response")

        # Parse and validate JSON
        try:
            architecture = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw content: {content[:500]}")
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")

        # Validate JSON structure
        architecture = self._validate_and_clean_architecture(architecture)

        print(f"DEBUG: OpenAI validated response total_duration = {architecture.get('scene_architecture', {}).get('total_duration', 'MISSING')}")

        # CRITICAL: Force exactly 15s architecture for perfect Luma sync (3×5s scenes)
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])

        # Ensure exactly 3 scenes with 5s each (3×5s = 15s total for Luma compatibility)
        while len(scenes) < 3:
            scenes.append({
                'scene_id': len(scenes) + 1,
                'duration': 5,
                'visual_concept': f'Professional scene {len(scenes) + 1}',
                'luma_prompt': f'High-quality scene {len(scenes) + 1}',
                'script_line': f'Scene {len(scenes) + 1} narration',
                'audio_cues': 'Professional audio',
                'music_cues': 'Enterprise music'
            })
        scenes = scenes[:3]  # Limit to exactly 3 scenes

        # Force exactly 5s per scene (3×5s = 15s total - matches Luma output)
        for i, scene in enumerate(scenes):
            scene['duration'] = 5
            scene['scene_id'] = i + 1

        # Force total duration to 15s (3×5s scenes for perfect audio-video sync)
        architecture['scene_architecture']['scenes'] = scenes
        architecture['scene_architecture']['total_duration'] = 15
        architecture['audio_architecture']['total_duration'] = 15

        # Store product image URL in architecture if provided
        if product_image_url:
            architecture['product_image_url'] = product_image_url

        print(f"DEBUG: OpenAI forced total_duration = {architecture['scene_architecture']['total_duration']}")
        if product_image_url:
            print(f"DEBUG: Product image will be used as keyframe for Scene 1")

        # Log clean JSON structure for debugging
        self._log_architecture_debug(architecture)

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
