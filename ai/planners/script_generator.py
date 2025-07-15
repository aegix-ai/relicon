"""
Script generation system for energetic advertisement voiceovers
Creates compelling, energetic scripts optimized for conversion
"""
import json
from typing import Dict, Any, List, Optional
from external.apis import openai_client

class ScriptGenerator:
    """Generates energetic advertisement scripts"""
    
    def __init__(self):
        self.client = openai_client
        self.energy_patterns = [
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
    
    def generate_energetic_segments(self, brand_info: Dict[str, Any], 
                                  num_segments: int = 3) -> List[Dict[str, Any]]:
        """
        Generate energetic advertisement-style script segments
        
        Args:
            brand_info: Brand information including name, description, target audience
            num_segments: Number of script segments to generate
            
        Returns:
            list: List of script segments with timing and energy indicators
        """
        try:
            system_prompt = """
            You are a world-class copywriter specializing in high-converting advertisement scripts.
            Create energetic, engaging scripts that sound natural when spoken aloud.
            
            Focus on:
            1. Powerful hooks that grab attention immediately
            2. Emotional triggers that create desire
            3. Clear value propositions
            4. Strong calls to action
            5. Natural speech patterns with energy
            
            Return JSON with this structure:
            {
                "segments": [
                    {
                        "segment_index": 0,
                        "text": "Energetic script text",
                        "duration": 8.5,
                        "energy_level": "high|medium|low",
                        "emotional_trigger": "curiosity|desire|urgency|fear|excitement",
                        "voice_direction": "Specific voice direction",
                        "purpose": "hook|value|proof|cta"
                    }
                ]
            }
            """
            
            user_prompt = f"""
            Create {num_segments} energetic script segments for this brand:
            
            Brand Name: {brand_info.get('brand_name', 'Unknown')}
            Brand Description: {brand_info.get('brand_description', 'No description')}
            Target Duration: {brand_info.get('duration', 30)} seconds total
            Platform: {brand_info.get('platform', 'universal')}
            
            Make each segment sound natural, energetic, and conversion-focused.
            Distribute the total duration across all segments.
            """
            
            response = self.client.generate_json(user_prompt, system_prompt)
            
            if response and "segments" in response:
                segments = response["segments"]
                # Enhance each segment with energy
                for segment in segments:
                    segment["text"] = self.enhance_script_energy(segment["text"])
                
                return segments
            else:
                return self._create_fallback_segments(brand_info, num_segments)
                
        except Exception as e:
            print(f"Error generating script segments: {e}")
            return self._create_fallback_segments(brand_info, num_segments)
    
    def enhance_script_energy(self, script_text: str) -> str:
        """
        Enhance existing script with more energy and advertisement style
        
        Args:
            script_text: Original script text
            
        Returns:
            str: Enhanced energetic script
        """
        energetic_text = script_text
        
        # Apply energy patterns
        for old, new in self.energy_patterns:
            energetic_text = energetic_text.replace(old, new)
        
        # Add hook questions at the start if not present
        if not any(starter in energetic_text.lower() for starter in 
                  ["have you", "are you", "do you", "ready to", "discover", "imagine"]):
            if "tired" in energetic_text.lower() or "problem" in energetic_text.lower():
                energetic_text = "Have you ever faced this problem? " + energetic_text
            elif "solution" in energetic_text.lower() or "help" in energetic_text.lower():
                energetic_text = "Ready for the solution you've been waiting for? " + energetic_text
            elif "new" in energetic_text.lower() or "discover" in energetic_text.lower():
                energetic_text = "Ready to discover something amazing? " + energetic_text
            else:
                energetic_text = "Have you ever wondered about this? " + energetic_text
        
        # Ensure energetic ending
        if not energetic_text.endswith(('!', '?')):
            energetic_text += "!"
        
        return energetic_text
    
    def generate_hook_variations(self, brand_info: Dict[str, Any], 
                               count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple hook variations for A/B testing
        
        Args:
            brand_info: Brand information
            count: Number of hook variations to generate
            
        Returns:
            list: List of hook variations with metadata
        """
        try:
            system_prompt = """
            You are a master of creating attention-grabbing hooks for video advertisements.
            Create diverse, compelling hooks that make people stop scrolling and watch.
            
            Hook types to consider:
            1. Question hooks (curiosity)
            2. Statement hooks (bold claims)
            3. Story hooks (personal narratives)
            4. Statistic hooks (surprising numbers)
            5. Emotional hooks (feelings)
            
            Return JSON with this structure:
            {
                "hooks": [
                    {
                        "text": "Hook text",
                        "type": "question|statement|story|statistic|emotional",
                        "emotional_trigger": "curiosity|surprise|fear|desire|urgency",
                        "target_audience": "specific audience segment",
                        "estimated_performance": "high|medium|low"
                    }
                ]
            }
            """
            
            user_prompt = f"""
            Create {count} diverse hook variations for this brand:
            
            Brand Name: {brand_info.get('brand_name', 'Unknown')}
            Brand Description: {brand_info.get('brand_description', 'No description')}
            Target Audience: {brand_info.get('target_audience', 'General consumers')}
            
            Make each hook unique and compelling for different audience segments.
            """
            
            response = self.client.generate_json(user_prompt, system_prompt)
            
            if response and "hooks" in response:
                hooks = response["hooks"]
                # Enhance each hook with energy
                for hook in hooks:
                    hook["text"] = self.enhance_script_energy(hook["text"])
                
                return hooks
            else:
                return self._create_fallback_hooks(brand_info, count)
                
        except Exception as e:
            print(f"Error generating hook variations: {e}")
            return self._create_fallback_hooks(brand_info, count)
    
    def optimize_for_platform(self, script: str, platform: str) -> str:
        """
        Optimize script for specific platform requirements
        
        Args:
            script: Original script text
            platform: Target platform (meta, tiktok, universal)
            
        Returns:
            str: Platform-optimized script
        """
        if platform == "tiktok":
            # TikTok prefers more casual, trend-aware language
            script = script.replace("Discover", "Check out")
            script = script.replace("Experience", "Try")
            script = script.replace("Purchase", "Get")
            
            # Add trending phrases
            if "amazing" not in script.lower():
                script = script.replace("great", "amazing")
            
        elif platform == "meta":
            # Meta prefers more direct, benefit-focused language
            script = script.replace("Check out", "Discover")
            script = script.replace("Try", "Experience")
            script = script.replace("Get", "Invest in")
            
            # Add trust signals
            if "trusted" not in script.lower() and "proven" not in script.lower():
                script = script.replace("solution", "proven solution")
        
        return script
    
    def _create_fallback_segments(self, brand_info: Dict[str, Any], 
                                num_segments: int) -> List[Dict[str, Any]]:
        """Create fallback segments when AI generation fails"""
        brand_name = brand_info.get('brand_name', 'our product')
        total_duration = brand_info.get('duration', 30)
        
        segments = []
        
        if num_segments == 1:
            segments.append({
                "segment_index": 0,
                "text": f"Ready to discover {brand_name}? This revolutionary solution will transform your experience! Don't miss out - take action now!",
                "duration": total_duration,
                "energy_level": "high",
                "emotional_trigger": "curiosity",
                "voice_direction": "Energetic and compelling throughout",
                "purpose": "complete"
            })
        
        elif num_segments == 2:
            segments.extend([
                {
                    "segment_index": 0,
                    "text": f"Have you ever wondered what {brand_name} could do for you?",
                    "duration": total_duration * 0.4,
                    "energy_level": "high",
                    "emotional_trigger": "curiosity",
                    "voice_direction": "Attention-grabbing and energetic",
                    "purpose": "hook"
                },
                {
                    "segment_index": 1,
                    "text": f"Get ready to experience the transformation! {brand_name} delivers exactly what you need. Take action today!",
                    "duration": total_duration * 0.6,
                    "energy_level": "high",
                    "emotional_trigger": "urgency",
                    "voice_direction": "Compelling and urgent",
                    "purpose": "value_cta"
                }
            ])
        
        else:  # 3+ segments
            segment_duration = total_duration / num_segments
            
            segments.extend([
                {
                    "segment_index": 0,
                    "text": f"Have you ever wondered about {brand_name}?",
                    "duration": segment_duration,
                    "energy_level": "high",
                    "emotional_trigger": "curiosity",
                    "voice_direction": "Attention-grabbing",
                    "purpose": "hook"
                },
                {
                    "segment_index": 1,
                    "text": f"Discover how {brand_name} transforms your experience!",
                    "duration": segment_duration,
                    "energy_level": "medium",
                    "emotional_trigger": "desire",
                    "voice_direction": "Compelling and clear",
                    "purpose": "value"
                },
                {
                    "segment_index": 2,
                    "text": f"Ready to get started? Take action now!",
                    "duration": segment_duration,
                    "energy_level": "high",
                    "emotional_trigger": "urgency",
                    "voice_direction": "Urgent and direct",
                    "purpose": "cta"
                }
            ])
        
        return segments
    
    def _create_fallback_hooks(self, brand_info: Dict[str, Any], 
                             count: int) -> List[Dict[str, Any]]:
        """Create fallback hooks when AI generation fails"""
        brand_name = brand_info.get('brand_name', 'our product')
        
        hooks = [
            {
                "text": f"Have you ever wondered what {brand_name} could do for you?",
                "type": "question",
                "emotional_trigger": "curiosity",
                "target_audience": "General consumers",
                "estimated_performance": "high"
            },
            {
                "text": f"This changes everything you thought you knew about {brand_name}!",
                "type": "statement",
                "emotional_trigger": "surprise",
                "target_audience": "Innovators",
                "estimated_performance": "medium"
            },
            {
                "text": f"Ready to discover the secret behind {brand_name}?",
                "type": "question",
                "emotional_trigger": "curiosity",
                "target_audience": "Curious buyers",
                "estimated_performance": "high"
            },
            {
                "text": f"Don't miss out on this incredible {brand_name} opportunity!",
                "type": "emotional",
                "emotional_trigger": "urgency",
                "target_audience": "FOMO-driven buyers",
                "estimated_performance": "medium"
            },
            {
                "text": f"Get ready to experience {brand_name} like never before!",
                "type": "statement",
                "emotional_trigger": "excitement",
                "target_audience": "Enthusiasts",
                "estimated_performance": "high"
            }
        ]
        
        return hooks[:count]

# Global script generator instance
script_generator = ScriptGenerator()