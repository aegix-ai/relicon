"""
Enhanced AI Video Ad Planner
Creates comprehensive plans for video ads with detailed component breakdown
"""
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

class VideoAdPlanner:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def create_master_plan(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive master plan for video ad
        Step 1: Overall concept and strategy
        """
        concept_prompt = f"""
        Create a comprehensive video ad strategy for the following brand:
        
        Brand: {brand_info.get('brand_name', 'Unknown Brand')}
        Description: {brand_info.get('brand_description', 'No description')}
        Target Audience: {brand_info.get('target_audience', 'General audience')}
        Tone: {brand_info.get('tone', 'professional')}
        Duration: {brand_info.get('duration', 30)} seconds
        Call to Action: {brand_info.get('call_to_action', 'Learn more')}
        
        Create a detailed master plan with:
        1. Core message and hook
        2. Emotional journey (how viewer should feel)
        3. Visual style and aesthetic
        4. Key selling points to highlight
        5. Pacing and energy level
        6. Overall narrative structure
        
        Respond in JSON format with these exact keys:
        {{
            "core_message": "Main message of the ad",
            "hook": "Opening hook to grab attention",
            "emotional_journey": ["emotion1", "emotion2", "emotion3"],
            "visual_style": "Description of visual aesthetic",
            "key_points": ["point1", "point2", "point3"],
            "pacing": "slow/medium/fast",
            "energy_level": "low/medium/high",
            "narrative_structure": "problem-solution/benefit-focused/story-driven"
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": concept_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        master_plan = json.loads(response.choices[0].message.content)
        return master_plan
    
    def break_down_components(self, master_plan: Dict[str, Any], duration: int = 30) -> List[Dict[str, Any]]:
        """
        Step 2: Break down ad into scene components
        """
        # COST OPTIMIZATION: Limit segments based on duration
        if duration <= 15:
            max_scenes = 2
            scene_guidance = "Create exactly 2 scenes: Hook+Build (8-10s) and Climax+CTA (5-7s)"
        elif duration <= 30:
            max_scenes = 3
            scene_guidance = "Create exactly 3 scenes: Hook (5-8s), Build+Climax (8-12s), CTA (5-10s)"
        else:
            max_scenes = 4
            scene_guidance = "Create exactly 4 scenes: Hook (5-10s), Build (7-12s), Climax (8-15s), CTA (5-10s)"
        
        breakdown_prompt = f"""
        Based on this master plan, break down the {duration}-second video ad into exactly {max_scenes} distinct scenes.
        
        CRITICAL COST OPTIMIZATION: Create exactly {max_scenes} scenes - no more, no less.
        Each scene must be substantial (minimum 5 seconds each) to reduce API costs.
        
        {scene_guidance}
        
        Master Plan:
        - Core Message: {master_plan.get('core_message')}
        - Hook: {master_plan.get('hook')}
        - Key Points: {master_plan.get('key_points')}
        - Pacing: {master_plan.get('pacing')}
        - Visual Style: {master_plan.get('visual_style')}
        
        Create scenes that:
        1. Each scene is 5+ seconds (cost efficient)
        2. Total duration equals {duration} seconds
        3. Follow the emotional journey
        4. Build to the call-to-action
        
        Respond in JSON format with this structure:
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "duration": 5,
                    "purpose": "hook/build/climax/cta",
                    "message": "What this scene communicates",
                    "emotion": "curious/excited/confident/urgent",
                    "visual_focus": "product/lifestyle/benefit/brand"
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": breakdown_prompt}],
            response_format={"type": "json_object"},
            temperature=0.6
        )
        
        breakdown = json.loads(response.choices[0].message.content)
        return breakdown.get("scenes", [])
    
    def plan_scene_details(self, scene: Dict[str, Any], master_plan: Dict[str, Any], brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Create detailed plan for individual scene
        """
        detail_prompt = f"""
        Create detailed execution plan for this video scene:
        
        Scene Info:
        - Purpose: {scene.get('purpose')}
        - Duration: {scene.get('duration')} seconds
        - Message: {scene.get('message')}
        - Emotion: {scene.get('emotion')}
        - Visual Focus: {scene.get('visual_focus')}
        
        Brand Context:
        - Brand: {brand_info.get('brand_name')}
        - Visual Style: {master_plan.get('visual_style')}
        - Tone: {brand_info.get('tone')}
        
        Create detailed plan with:
        1. Voiceover script (conversational, engaging)
        2. Visual description for AI video generation
        3. Camera movement and composition
        4. Lighting and mood
        5. Specific visual elements to include
        
        Respond in JSON format:
        {{
            "voiceover": "Exact script to be spoken",
            "visual_prompt": "Detailed prompt for Luma AI video generation",
            "camera_style": "push-in/pull-out/rotate/static/dynamic",
            "lighting": "cinematic/natural/dramatic/soft",
            "mood": "energetic/calm/mysterious/confident",
            "visual_elements": ["element1", "element2"],
            "duration": {scene.get('duration')}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": detail_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        details = json.loads(response.choices[0].message.content)
        return details
    
    def optimize_video_prompts(self, scene_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 4: Optimize prompts for best Luma AI results
        """
        optimized_scenes = []
        
        for i, scene in enumerate(scene_details):
            optimization_prompt = f"""
            Optimize this video prompt for Luma AI generation to create the highest quality result:
            
            Original prompt: {scene.get('visual_prompt')}
            Camera style: {scene.get('camera_style')}
            Lighting: {scene.get('lighting')}
            Mood: {scene.get('mood')}
            Duration: {scene.get('duration')} seconds
            
            Create an optimized prompt that:
            1. Uses Luma AI best practices
            2. Includes specific camera movements
            3. Describes lighting and composition
            4. Maintains 9:16 aspect ratio
            5. Keeps under 10 seconds
            6. Creates engaging visual content
            
            Focus on professional, advertising-quality visuals.
            
            Respond with just the optimized prompt text, no JSON.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.5
            )
            
            optimized_prompt = response.choices[0].message.content.strip()
            
            # Ensure duration is capped at 10 seconds
            duration = min(scene.get('duration', 5), 10)
            
            optimized_scene = {
                **scene,
                'optimized_prompt': optimized_prompt,
                'duration': duration,
                'scene_index': i
            }
            
            optimized_scenes.append(optimized_scene)
        
        return optimized_scenes
    
    def create_complete_plan(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete planning pipeline
        """
        print("Creating master plan...")
        master_plan = self.create_master_plan(brand_info)
        
        print("Breaking down into components...")
        scene_components = self.break_down_components(master_plan, brand_info.get('duration', 30))
        
        print("Planning scene details...")
        detailed_scenes = []
        for scene in scene_components:
            scene_details = self.plan_scene_details(scene, master_plan, brand_info)
            detailed_scenes.append(scene_details)
        
        print("Optimizing video prompts...")
        optimized_scenes = self.optimize_video_prompts(detailed_scenes)
        
        complete_plan = {
            'master_plan': master_plan,
            'scene_components': scene_components,
            'detailed_scenes': optimized_scenes,
            'total_duration': sum(scene.get('duration', 0) for scene in optimized_scenes),
            'scene_count': len(optimized_scenes)
        }
        
        return complete_plan