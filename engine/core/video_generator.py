# type: ignore

# 3rd

"""
    Video generation service with Redis caching.
    Generates video scenes and caches results to avoid redundant API calls.
"""

import os
import time
import hashlib
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from providers.luma import LumaProvider
from providers.mock_video import MockVideoProvider
from core.logger import get_logger

logger = get_logger("video_service")

class VideoService:
    """Video generation service with caching support"""

    def __init__(self):
        self.providers = {
            'luma': LumaProvider(),
            'mock': MockVideoProvider()
        }

        # Provider priority order
        self.provider_order = ['luma', 'mock']        # Check if we're in mock mode
        self.mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        if self.mock_mode:
            self.provider_order = ['mock']
            logger.info("Video service running in mock mode")

        # Initialize Redis cache (optional)
        self.redis_cache = self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection for caching (optional)"""
        try:
            import redis
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=False
            )
            redis_client.ping()
            logger.info("Redis cache initialized")
            return redis_client
        except Exception as e:
            logger.info(f"Redis not available, caching disabled: {e}")
            return None

    def _get_cache_key(self,
                       prompt: str,
                       image_url: Optional[str] = None) -> str:
        """Generate cache key from prompt and image URL"""
        cache_data = f"{prompt}:{image_url or ''}"
        return f"video:{hashlib.md5(cache_data.encode()).hexdigest()}"

    def _get_cached_video(self,
                          cache_key: str) -> Optional[str]:
        """Retrieve cached video path if available"""
        if not self.redis_cache:
            return None

        try:
            cached_path = self.redis_cache.get(cache_key)
            if cached_path and os.path.exists(cached_path.decode()):
                logger.info(f"Cache hit for {cache_key}")
                return cached_path.decode()
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")

        return None

    def _cache_video(self,
                     cache_key: str,
                     video_path: str,
                     ttl: int = 86400):
        """Cache video path with TTL (default 24 hours)"""
        if not self.redis_cache:
            return

        try:
            self.redis_cache.setex(cache_key, ttl, video_path)
            logger.info(f"Cached video: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def generate_scene_video(self,
                             scene: Dict[str, Any],
                             temp_dir: str,
                             product_image_url: Optional[str] = None) -> Optional[str]:
        """Generate video for a single scene with caching support"""

        scene_number = scene.get('scene_number', 1)

        # Get architecture for product context
        architecture = scene.get('architecture', {})
        if not product_image_url:
            product_image_url = architecture.get('product_image_url')

        # Get prompt from scene
        if 'luma_prompt' in scene:
            prompt = scene['luma_prompt']
        elif 'visual_concept' in scene:
            prompt = scene['visual_concept']
        else:
            prompt = scene.get('luma_prompt', scene.get('visual_concept', ''))

        if not prompt:
            logger.warning(f"No prompt found for scene {scene_number}")
            return None

        # Check cache first
        image_url = product_image_url if scene_number == 1 else None
        cache_key = self._get_cache_key(prompt, image_url)
        cached_video = self._get_cached_video(cache_key)

        if cached_video:
            logger.info(f"Using cached video for scene {scene_number}")
            return cached_video

        # Create output directory
        output_dir = os.path.join(temp_dir, "videos")
        os.makedirs(output_dir, exist_ok=True)
        enhanced_prompt = prompt

        if product_image_url:
            if scene_number == 1:
                # Use product image as keyframe for first scene
                image_url = product_image_url

                # Enhance prompt for better product integration
                product_focused_prompt = (
                    f"Professional product showcase starting with the exact product shown in the image, "
                    f"{prompt}, emphasizing product features and benefits, commercial photography style, "
                    f"product-centric composition, high-quality product demonstration"
                )
                enhanced_prompt = product_focused_prompt
                logger.info(f"Scene 1: Using product image as keyframe with enhanced prompt")

            elif scene_number == 2:
                # For second scene, add realism validation and product consistency
                realism_rules = "complete laptop with screen visible, realistic technology interaction, no floating components"
                enhanced_prompt = (
                    f"{prompt}, featuring the same product from previous scene, "
                    f"maintaining visual consistency, product demonstration focus, "
                    f"seamless transition from product showcase, {realism_rules}"
                )
                logger.info(f"Scene 2: Enhanced prompt for product consistency with realism rules")

            elif scene_number == 3:
                # For third scene, focus on product benefits and call-to-action
                enhanced_prompt = (
                    f"{prompt}, showcasing the product benefits and results, "
                    f"compelling call-to-action presentation, product satisfaction focus"
                )
                logger.info(f"Scene 3: Enhanced prompt for product benefits")

        # Try each provider in order
        for provider_name in self.provider_order:
            try:
                video_generator = self.providers[provider_name]
                logger.info(f"Attempting scene {scene_number} generation with {provider_name}")

                # Generate video with enhanced prompt and product image
                video_url = video_generator.generate_video(
                    prompt=enhanced_prompt,
                    aspect_ratio="9:16",
                    image_url=image_url,
                    force_unique=True
                )

                if not video_url:
                    logger.warning(f"{provider_name} returned no video URL for scene {scene_number}")
                    continue

                # Download video
                output_filename = f"scene_{scene_number:02d}_{int(time.time())}.mp4"
                output_path = os.path.join(output_dir, output_filename)

                if video_generator.download_video(video_url, output_path):
                    logger.info(f"Scene {scene_number} generated successfully with {provider_name}")

                    # Cache the result
                    self._cache_video(cache_key, output_path)

                    return output_path
                else:
                    logger.warning(f"Failed to download video from {provider_name} for scene {scene_number}")
                    continue

            except Exception as e:
                logger.error(f"Error with {provider_name} for scene {scene_number}: {str(e)}")
                continue

        logger.error(f"All providers failed for scene {scene_number}")
        return None

    def generate_videos_for_architecture(self,
                                         architecture: Dict[str, Any],
                                         temp_dir: str) -> Dict[str, str]:
        """Generate videos for all scenes in architecture with product image integration"""

        scenes = architecture.get('scenes', [])
        if not scenes:
            logger.error("No scenes found in architecture")
            return {}

        # Get product image URL from architecture
        product_image_url = architecture.get('product_image_url')
        if product_image_url:
            logger.info(f"Product image available for video generation: {product_image_url}")

        # Create output directory
        output_dir = os.path.join(temp_dir, "videos")
        os.makedirs(output_dir, exist_ok=True)

        generated_videos = {}

        for i, scene in enumerate(scenes, 1):
            scene_number = scene.get('scene_number', i)

            logger.info(f"Generating video for scene {scene_number}/{len(scenes)}")

            # Add scene number and architecture to scene data
            scene_with_context = {
                **scene,
                'scene_number': scene_number,
                'architecture': architecture
            }

            video_path = self.generate_scene_video(
                scene_with_context,
                temp_dir,
                product_image_url
            )

            if video_path:
                generated_videos[f"scene_{scene_number}"] = video_path
                logger.info(f"Scene {scene_number} completed: {video_path}")
            else:
                logger.error(f"Failed to generate scene {scene_number}")
                # Continue with other scenes even if one fails

        logger.info(f"Video generation completed: {len(generated_videos)}/{len(scenes)} scenes successful")
        return generated_videos

    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all video providers"""
        status = {}
        for name, provider in self.providers.items():
            try:
                # Simple health check - try to access the provider
                status[name] = hasattr(provider, 'generate_video')
            except Exception:
                status[name] = False
        return status
