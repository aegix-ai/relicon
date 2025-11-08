"""
Mock text generation provider for testing without OpenAI API.
"""

import time
from typing import Dict, Any, List
from interfaces.text_generator import TextGenerator


class MockTextProvider(TextGenerator):
    """Mock text generator for testing without API calls."""

    def __init__(self):
        print("🎭 Mock Text Provider initialized (no API key required)")

    def architect_complete_video(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock video architecture without calling OpenAI."""

        brand_name = brand_info.get('brand_name', 'Test Brand')
        product_name = brand_info.get('product_name', 'Test Product')
        product_description = brand_info.get('product_description', 'Amazing product')
        target_audience = brand_info.get('target_audience', 'general audience')
        product_image_url = brand_info.get('product_image_url')

        print(f"🎭 Generating mock architecture for: {brand_name} - {product_name}")

        # Simulate AI thinking time
        time.sleep(1)

        # Create realistic mock architecture
        architecture = {
            "creative_vision": {
                "overall_concept": f"A modern commercial showcasing {product_name} with compelling storytelling that resonates with {target_audience}.",
                "visual_style": "modern premium",
                "color_palette": ["Deep Blue", "Silver", "White"],
                "mood": "inspiring and professional",
                "brand_story_arc": "Curiosity → Problem → Solution"
            },
            "audio_architecture": {
                "voice_gender": "male",
                "voice_tone": "professional",
                "energy_level": "medium",
                "music_style": "cinematic",
                "tempo_bpm": 120,
                "total_duration": 18
            },
            "scene_architecture": {
                "total_duration": 18,
                "scenes": [
                    {
                        "scene_id": 1,
                        "role": "hook",
                        "purpose": f"Introduce {product_name} with visual impact and lifestyle context",
                        "duration": 6,
                        "visual_concept": f"Opening shot showcasing {product_name} in premium environment with elegant cinematography.",
                        "luma_prompt": f"Smooth cinematic reveal of {product_name} on modern minimalist surface, golden hour lighting streaming through windows. Professional product photography with shallow depth of field, camera slowly pulling back to reveal premium lifestyle setting. Modern commercial aesthetic, no face close-ups, emphasis on product design and environment.",
                        "script_line": f"Discover {product_name} - the innovation that transforms how you work and play every day.",
                        "audio_cues": "Soft ambient sounds, gentle product interaction, professional environment",
                        "music_cues": "Gentle piano intro building anticipation",
                        "brand_alignment": "Establishes premium positioning and introduces core product benefits"
                    },
                    {
                        "scene_id": 2,
                        "role": "problem",
                        "purpose": "Demonstrate the pain point or challenge that the product solves",
                        "duration": 6,
                        "visual_concept": "Show the frustration and limitations of traditional solutions through environmental storytelling.",
                        "luma_prompt": "Wide shot of cluttered workspace showing inefficiency and frustration. Hands gesturing through disorganized materials, muted color grading emphasizing the problem. Overhead camera angle revealing chaotic environment, environmental storytelling with minimal face shots, tension-building cinematography showing clear pain point.",
                        "script_line": "Tired of the old way? Traditional solutions hold you back from reaching your full potential.",
                        "audio_cues": "Cluttered sounds, frustrated movement, tension-building ambience",
                        "music_cues": "Subtle tension with minor chords building problem awareness",
                        "brand_alignment": "Creates clear problem awareness that our solution addresses"
                    },
                    {
                        "scene_id": 3,
                        "role": "solution",
                        "purpose": f"Show {product_name} solving the problem with clear call-to-action",
                        "duration": 6,
                        "visual_concept": f"Dynamic transformation showing confident usage of {product_name}, ending with branding and CTA.",
                        "luma_prompt": f"Dynamic reveal of person successfully using {product_name}, moving confidently in bright modern space. Smooth tracking shot following natural productive flow, showcasing product benefits in action. Product branding prominently displayed with elegant animation, uplifting color grading, ending with clear call-to-action overlay text.",
                        "script_line": f"Experience the difference with {product_name}. Premium quality, effortless results. Get yours today and transform your workflow.",
                        "audio_cues": "Confident movement, success indicators, positive environmental ambience",
                        "music_cues": "Uplifting crescendo with full instrumentation, resolving to major key",
                        "brand_alignment": "Demonstrates product solving problem while driving immediate action"
                    }
                ]
            },
            "unified_script": f"Discover {product_name} - the innovation that transforms how you work and play every day. Tired of the old way? Traditional solutions hold you back from reaching your full potential. Experience the difference with {product_name}. Premium quality, effortless results. Get yours today and transform your workflow."
        }

        # Add product image URL if provided
        if product_image_url:
            architecture['product_image_url'] = product_image_url
            print(f"🎭 Mock architecture includes product image: {product_image_url[:50]}...")

        print(f"✅ Mock architecture created: 3 scenes, 18s duration")
        return architecture

    def create_cutting_edge_prompts(self, architecture: Dict[str, Any], service_type: str = "luma") -> List[Dict[str, Any]]:
        """Generate mock service-specific prompts."""
        scenes = architecture.get('scene_architecture', {}).get('scenes', [])

        enhanced_scenes = []
        for scene in scenes:
            enhanced_scene = scene.copy()
            enhanced_scene['enhanced_prompt'] = scene.get('luma_prompt', '')
            enhanced_scenes.append(enhanced_scene)

        return enhanced_scenes

    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate mock text response."""
        return f"Mock response to: {prompt[:50]}..."
