"""Dynamic scene planning for colorful and creative video backgrounds"""
import random
from typing import Dict, Any, List
from pathlib import Path
import subprocess
from config.settings import settings

class DynamicScenePlanner:
    """Plans dynamic, colorful, and creative video scenes"""
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUT_DIR) / "scenes"
        self.output_dir.mkdir(exist_ok=True)
        
        # Color palettes for different moods
        self.color_palettes = {
            "energetic": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#F9CA24", "#F0932B"],
            "professional": ["#2C3E50", "#3498DB", "#E74C3C", "#F39C12", "#27AE60"],
            "warm": ["#E67E22", "#E74C3C", "#F39C12", "#D35400", "#C0392B"],
            "cool": ["#3498DB", "#2ECC71", "#1ABC9C", "#9B59B6", "#34495E"],
            "vibrant": ["#FF3838", "#FF9F43", "#7ED321", "#50E3C2", "#B794F6"],
            "gradient": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
        }
        
        # Animation patterns
        self.animations = [
            "gradient_flow", "particle_burst", "wave_motion", "geometric_shift",
            "color_transition", "plasma_effect", "mandala_spin", "liquid_motion"
        ]
        
        # Scene types based on content
        self.scene_types = {
            "hook": {"mood": "energetic", "animation": "particle_burst"},
            "problem": {"mood": "cool", "animation": "wave_motion"},
            "solution": {"mood": "vibrant", "animation": "gradient_flow"},
            "benefits": {"mood": "warm", "animation": "color_transition"},
            "cta": {"mood": "professional", "animation": "geometric_shift"}
        }
    
    def plan_scene_components(self, script_segments: List[Dict[str, Any]], 
                            brand_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan complete scene components with visual effects"""
        try:
            planned_scenes = []
            
            for i, segment in enumerate(script_segments):
                # Determine scene type based on content
                scene_type = self._determine_scene_type(segment.get("text", ""), i)
                
                # Get scene configuration
                scene_config = self.scene_types.get(scene_type, self.scene_types["hook"])
                
                # Plan visual components
                scene_plan = {
                    "index": i,
                    "type": scene_type,
                    "text": segment.get("text", ""),
                    "duration": segment.get("duration", 5),
                    "visual_config": self._create_visual_config(scene_config, brand_info),
                    "animation_config": self._create_animation_config(scene_config["animation"]),
                    "color_palette": self._select_color_palette(scene_config["mood"]),
                    "effects": self._plan_visual_effects(scene_type, segment.get("duration", 5))
                }
                
                planned_scenes.append(scene_plan)
            
            return planned_scenes
            
        except Exception as e:
            print(f"Scene planning error: {e}")
            return []
    
    def create_dynamic_background(self, scene_plan: Dict[str, Any], output_path: str) -> bool:
        """Create dynamic background video based on scene plan"""
        try:
            duration = scene_plan["duration"]
            colors = scene_plan["color_palette"]
            animation = scene_plan["animation_config"]
            
            # Create FFmpeg filter for dynamic background
            filter_complex = self._build_dynamic_filter(colors, animation, duration)
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", filter_complex,
                "-t", str(duration),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-s", "1080x1920",  # 9:16 aspect ratio
                "-aspect", "9:16",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Dynamic background creation error: {e}")
            return False
    
    def _determine_scene_type(self, text: str, index: int) -> str:
        """Determine scene type based on content"""
        text_lower = text.lower()
        
        # Keywords for different scene types
        if any(word in text_lower for word in ["introducing", "discover", "new", "amazing"]):
            return "hook"
        elif any(word in text_lower for word in ["problem", "struggle", "difficult", "challenge"]):
            return "problem"
        elif any(word in text_lower for word in ["solution", "answer", "fix", "solves"]):
            return "solution"
        elif any(word in text_lower for word in ["benefits", "advantages", "results", "experience"]):
            return "benefits"
        elif any(word in text_lower for word in ["buy", "order", "get", "visit", "try"]):
            return "cta"
        else:
            # Default based on position
            if index == 0:
                return "hook"
            elif index == len(text) - 1:
                return "cta"
            else:
                return "solution"
    
    def _create_visual_config(self, scene_config: Dict[str, Any], brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create visual configuration for scene"""
        return {
            "style": scene_config["mood"],
            "intensity": 0.7,
            "brand_alignment": brand_info.get("style", "professional"),
            "visual_complexity": "medium",
            "motion_speed": "moderate"
        }
    
    def _create_animation_config(self, animation_type: str) -> Dict[str, Any]:
        """Create animation configuration"""
        configs = {
            "gradient_flow": {
                "type": "gradient",
                "direction": "diagonal",
                "speed": "slow",
                "blend_mode": "normal"
            },
            "particle_burst": {
                "type": "particles",
                "count": 50,
                "size": "medium",
                "movement": "burst"
            },
            "wave_motion": {
                "type": "wave",
                "frequency": 2,
                "amplitude": 0.3,
                "direction": "horizontal"
            },
            "geometric_shift": {
                "type": "geometric",
                "shapes": ["circle", "square", "triangle"],
                "transformation": "rotation"
            },
            "color_transition": {
                "type": "color_fade",
                "transition_speed": "smooth",
                "pattern": "radial"
            }
        }
        
        return configs.get(animation_type, configs["gradient_flow"])
    
    def _select_color_palette(self, mood: str) -> List[str]:
        """Select color palette based on mood"""
        palette = self.color_palettes.get(mood, self.color_palettes["energetic"])
        return random.sample(palette, min(3, len(palette)))
    
    def _plan_visual_effects(self, scene_type: str, duration: float) -> List[Dict[str, Any]]:
        """Plan visual effects for scene"""
        effects = []
        
        if scene_type == "hook":
            effects.append({
                "type": "zoom_in",
                "start_time": 0,
                "duration": duration * 0.5,
                "intensity": 0.8
            })
        elif scene_type == "problem":
            effects.append({
                "type": "blur_focus",
                "start_time": 0,
                "duration": duration,
                "intensity": 0.3
            })
        elif scene_type == "solution":
            effects.append({
                "type": "brightness_increase",
                "start_time": duration * 0.3,
                "duration": duration * 0.7,
                "intensity": 0.6
            })
        
        return effects
    
    def _build_dynamic_filter(self, colors: List[str], animation: Dict[str, Any], duration: float) -> str:
        """Build FFmpeg filter for dynamic background"""
        animation_type = animation.get("type", "gradient")
        
        if animation_type == "gradient":
            # Create flowing gradient
            color1 = colors[0].replace("#", "0x")
            color2 = colors[1] if len(colors) > 1 else colors[0].replace("#", "0x")
            
            return (
                f"color=c={color1}:s=1920x1080:d={duration}[base];"
                f"color=c={color2}:s=1920x1080:d={duration}[overlay];"
                "[base][overlay]blend=all_mode=overlay:all_opacity=0.5"
            )
        
        elif animation_type == "particles":
            # Create particle effect
            return (
                f"color=c=black:s=1920x1080:d={duration}[base];"
                f"color=c={colors[0].replace('#', '0x')}:s=20x20:d={duration}[particle];"
                "[base][particle]overlay=x='if(gte(t,0),100*sin(t*2),0)':y='if(gte(t,0),100*cos(t*2),0)'"
            )
        
        else:
            # Default gradient
            return f"color=c={colors[0].replace('#', '0x')}:s=1920x1080:d={duration}"

# Global instance
dynamic_scene_planner = DynamicScenePlanner()