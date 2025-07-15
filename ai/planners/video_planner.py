"""
Video planning system for AI-generated advertisements
Creates comprehensive plans for video generation with strategic thinking
"""
import json
from typing import Dict, Any, List, Optional
from external.apis import openai_client
from config.settings import settings

class VideoPlanner:
    """Strategic video planning system"""
    
    def __init__(self):
        self.client = openai_client
        self.default_duration = settings.DEFAULT_VIDEO_DURATION
        self.max_duration = settings.MAX_VIDEO_DURATION
    
    def create_master_plan(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive master plan for video ad
        
        Args:
            brand_info: Brand information including name, description, target audience
            
        Returns:
            dict: Master plan with strategic overview and key messaging
        """
        try:
            system_prompt = """
            You are a world-class creative director specializing in video advertising.
            Create a comprehensive master plan for a video advertisement that will drive conversions.
            
            Focus on:
            1. Strategic messaging and positioning
            2. Target audience psychology
            3. Compelling narrative structure
            4. Visual and audio elements
            5. Call-to-action strategy
            
            Return your response as JSON with this structure:
            {
                "concept": "Main creative concept",
                "target_audience": "Primary target audience",
                "key_message": "Core message to communicate",
                "emotional_triggers": ["trigger1", "trigger2"],
                "narrative_structure": "Beginning-middle-end structure",
                "visual_style": "Visual approach and style",
                "audio_style": "Audio/music approach",
                "call_to_action": "Specific CTA strategy",
                "success_metrics": ["metric1", "metric2"]
            }
            """
            
            user_prompt = f"""
            Create a master plan for a video advertisement with this brand information:
            
            Brand Name: {brand_info.get('brand_name', 'Unknown')}
            Brand Description: {brand_info.get('brand_description', 'No description provided')}
            Target Duration: {brand_info.get('duration', self.default_duration)} seconds
            Platform: {brand_info.get('platform', 'universal')}
            
            Additional Context:
            {json.dumps(brand_info, indent=2)}
            """
            
            response = self.client.generate_json(user_prompt, system_prompt)
            
            if response:
                return {
                    "success": True,
                    "master_plan": response,
                    "duration": brand_info.get('duration', self.default_duration)
                }
            else:
                return self._create_fallback_master_plan(brand_info)
                
        except Exception as e:
            print(f"Error creating master plan: {e}")
            return self._create_fallback_master_plan(brand_info)
    
    def break_down_components(self, master_plan: Dict[str, Any], 
                            duration: int = 30) -> List[Dict[str, Any]]:
        """
        Break down master plan into scene components
        
        Args:
            master_plan: The master plan from create_master_plan
            duration: Total video duration in seconds
            
        Returns:
            list: List of scene components with timing and content
        """
        try:
            # Determine optimal scene breakdown
            if duration <= 15:
                scenes = self._create_short_scenes(master_plan, duration)
            elif duration <= 30:
                scenes = self._create_medium_scenes(master_plan, duration)
            else:
                scenes = self._create_long_scenes(master_plan, duration)
            
            return scenes
            
        except Exception as e:
            print(f"Error breaking down components: {e}")
            return self._create_fallback_scenes(duration)
    
    def _create_short_scenes(self, master_plan: Dict[str, Any], 
                           duration: int) -> List[Dict[str, Any]]:
        """Create scenes for short videos (≤15 seconds)"""
        plan_data = master_plan.get("master_plan", {})
        
        # For short videos, use 2-3 quick scenes
        scenes = [
            {
                "scene_index": 0,
                "duration": duration * 0.4,  # 40% for hook
                "type": "hook",
                "content": f"Hook: {plan_data.get('key_message', 'Attention-grabbing opener')}",
                "visual_style": plan_data.get('visual_style', 'dynamic'),
                "audio_style": "energetic",
                "emotional_trigger": plan_data.get('emotional_triggers', ['curiosity'])[0]
            },
            {
                "scene_index": 1,
                "duration": duration * 0.6,  # 60% for value + CTA
                "type": "value_cta",
                "content": f"Value & CTA: {plan_data.get('call_to_action', 'Take action now')}",
                "visual_style": plan_data.get('visual_style', 'clear'),
                "audio_style": "compelling",
                "emotional_trigger": plan_data.get('emotional_triggers', ['urgency'])[-1]
            }
        ]
        
        return scenes
    
    def _create_medium_scenes(self, master_plan: Dict[str, Any], 
                            duration: int) -> List[Dict[str, Any]]:
        """Create scenes for medium videos (16-30 seconds)"""
        plan_data = master_plan.get("master_plan", {})
        
        # For medium videos, use 3-4 scenes
        scenes = [
            {
                "scene_index": 0,
                "duration": duration * 0.25,  # 25% for hook
                "type": "hook",
                "content": f"Hook: {plan_data.get('key_message', 'Attention-grabbing opener')}",
                "visual_style": plan_data.get('visual_style', 'dynamic'),
                "audio_style": "energetic",
                "emotional_trigger": plan_data.get('emotional_triggers', ['curiosity'])[0]
            },
            {
                "scene_index": 1,
                "duration": duration * 0.35,  # 35% for problem/solution
                "type": "problem_solution",
                "content": f"Problem/Solution: {plan_data.get('concept', 'Present solution')}",
                "visual_style": plan_data.get('visual_style', 'clear'),
                "audio_style": "explanatory",
                "emotional_trigger": "pain_relief"
            },
            {
                "scene_index": 2,
                "duration": duration * 0.25,  # 25% for benefits
                "type": "benefits",
                "content": f"Benefits: Transform your experience",
                "visual_style": "aspirational",
                "audio_style": "inspiring",
                "emotional_trigger": "desire"
            },
            {
                "scene_index": 3,
                "duration": duration * 0.15,  # 15% for CTA
                "type": "cta",
                "content": f"CTA: {plan_data.get('call_to_action', 'Take action now')}",
                "visual_style": "direct",
                "audio_style": "urgent",
                "emotional_trigger": "urgency"
            }
        ]
        
        return scenes
    
    def _create_long_scenes(self, master_plan: Dict[str, Any], 
                          duration: int) -> List[Dict[str, Any]]:
        """Create scenes for long videos (>30 seconds)"""
        plan_data = master_plan.get("master_plan", {})
        
        # For long videos, use 5-6 scenes with detailed narrative
        scenes = [
            {
                "scene_index": 0,
                "duration": duration * 0.15,  # 15% for hook
                "type": "hook",
                "content": f"Hook: {plan_data.get('key_message', 'Compelling opener')}",
                "visual_style": plan_data.get('visual_style', 'dynamic'),
                "audio_style": "energetic",
                "emotional_trigger": plan_data.get('emotional_triggers', ['curiosity'])[0]
            },
            {
                "scene_index": 1,
                "duration": duration * 0.2,  # 20% for problem identification
                "type": "problem",
                "content": "Problem: Identify pain points",
                "visual_style": "relatable",
                "audio_style": "empathetic",
                "emotional_trigger": "frustration"
            },
            {
                "scene_index": 2,
                "duration": duration * 0.25,  # 25% for solution presentation
                "type": "solution",
                "content": f"Solution: {plan_data.get('concept', 'Present solution')}",
                "visual_style": "clear",
                "audio_style": "confident",
                "emotional_trigger": "hope"
            },
            {
                "scene_index": 3,
                "duration": duration * 0.2,  # 20% for benefits/transformation
                "type": "benefits",
                "content": "Benefits: Show transformation",
                "visual_style": "aspirational",
                "audio_style": "inspiring",
                "emotional_trigger": "desire"
            },
            {
                "scene_index": 4,
                "duration": duration * 0.1,  # 10% for social proof
                "type": "social_proof",
                "content": "Social Proof: Build credibility",
                "visual_style": "trustworthy",
                "audio_style": "authentic",
                "emotional_trigger": "trust"
            },
            {
                "scene_index": 5,
                "duration": duration * 0.1,  # 10% for CTA
                "type": "cta",
                "content": f"CTA: {plan_data.get('call_to_action', 'Take action now')}",
                "visual_style": "direct",
                "audio_style": "urgent",
                "emotional_trigger": "urgency"
            }
        ]
        
        return scenes
    
    def plan_scene_details(self, scene: Dict[str, Any], master_plan: Dict[str, Any], 
                         brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create detailed plan for individual scene
        
        Args:
            scene: Scene component from break_down_components
            master_plan: Master plan context
            brand_info: Brand information
            
        Returns:
            dict: Detailed scene plan with specific instructions
        """
        try:
            system_prompt = """
            You are a video production expert. Create detailed scene instructions 
            for video generation that will produce engaging, high-converting content.
            
            Return JSON with this structure:
            {
                "video_prompt": "Detailed prompt for video generation",
                "audio_script": "Exact script for voiceover",
                "visual_elements": ["element1", "element2"],
                "timing_notes": "Specific timing instructions",
                "transition_style": "How to transition to next scene"
            }
            """
            
            user_prompt = f"""
            Create detailed instructions for this scene:
            
            Scene Info:
            {json.dumps(scene, indent=2)}
            
            Master Plan Context:
            {json.dumps(master_plan.get('master_plan', {}), indent=2)}
            
            Brand Info:
            {json.dumps(brand_info, indent=2)}
            
            Make it specific, actionable, and optimized for conversion.
            """
            
            response = self.client.generate_json(user_prompt, system_prompt)
            
            if response:
                return {
                    "success": True,
                    "scene_details": response,
                    "original_scene": scene
                }
            else:
                return self._create_fallback_scene_details(scene)
                
        except Exception as e:
            print(f"Error planning scene details: {e}")
            return self._create_fallback_scene_details(scene)
    
    def _create_fallback_master_plan(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback master plan when AI generation fails"""
        return {
            "success": False,
            "master_plan": {
                "concept": f"Showcase {brand_info.get('brand_name', 'the product')} benefits",
                "target_audience": "General consumers",
                "key_message": f"Discover {brand_info.get('brand_name', 'our solution')}",
                "emotional_triggers": ["curiosity", "desire", "urgency"],
                "narrative_structure": "Hook-Problem-Solution-CTA",
                "visual_style": "Clean and professional",
                "audio_style": "Energetic and confident",
                "call_to_action": "Learn more today",
                "success_metrics": ["engagement", "conversions"]
            },
            "duration": brand_info.get('duration', self.default_duration)
        }
    
    def _create_fallback_scenes(self, duration: int) -> List[Dict[str, Any]]:
        """Create fallback scenes when planning fails"""
        return [
            {
                "scene_index": 0,
                "duration": duration * 0.3,
                "type": "hook",
                "content": "Attention-grabbing opener",
                "visual_style": "dynamic",
                "audio_style": "energetic",
                "emotional_trigger": "curiosity"
            },
            {
                "scene_index": 1,
                "duration": duration * 0.5,
                "type": "value",
                "content": "Present value proposition",
                "visual_style": "clear",
                "audio_style": "compelling",
                "emotional_trigger": "desire"
            },
            {
                "scene_index": 2,
                "duration": duration * 0.2,
                "type": "cta",
                "content": "Strong call to action",
                "visual_style": "direct",
                "audio_style": "urgent",
                "emotional_trigger": "urgency"
            }
        ]
    
    def _create_fallback_scene_details(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback scene details when planning fails"""
        return {
            "success": False,
            "scene_details": {
                "video_prompt": f"Create {scene.get('type', 'generic')} scene with {scene.get('visual_style', 'professional')} style",
                "audio_script": scene.get('content', 'Generic content'),
                "visual_elements": ["Professional visuals", "Brand colors", "Clear messaging"],
                "timing_notes": f"Duration: {scene.get('duration', 5)} seconds",
                "transition_style": "Smooth fade"
            },
            "original_scene": scene
        }

# Global video planner instance
video_planner = VideoPlanner()