"""
Stock Footage Tool
Searches and downloads relevant stock footage based on visual hints
"""
import json
import os
import hashlib
import requests
from typing import Dict, Any, List
from pathlib import Path
import time

from config.settings import settings, logger


def run(timeline_data: str) -> str:
    """
    Search and download stock footage based on timeline visual requirements
    
    Args:
        timeline_data: JSON string containing timeline with visual hints
        
    Returns:
        JSON string with downloaded stock footage information
    """
    try:
        # Parse timeline data
        if isinstance(timeline_data, str):
            try:
                timeline_info = json.loads(timeline_data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in timeline data")
                raise ValueError("Timeline data must be valid JSON")
        else:
            timeline_info = timeline_data
            
        timeline = timeline_info.get('timeline', [])
        if not timeline:
            raise ValueError("No timeline found in input data")
        
        # Extract video segments that need stock footage
        video_segments = [item for item in timeline if item.get('type') == 'video']
        if not video_segments:
            raise ValueError("No video segments found in timeline")
            
        logger.info("Starting stock footage search", segments=len(video_segments))
        
        # Initialize stock provider
        stock_provider = _get_stock_provider()
        
        # Search and download footage for each segment
        footage_results = []
        
        for i, segment in enumerate(video_segments):
            search_query = segment.get('search_query', segment.get('visual_hint', ''))
            duration = segment.get('duration', 5.0)
            scene_id = segment.get('scene_id', i + 1)
            
            if not search_query:
                logger.warning(f"No search query for segment {scene_id}")
                continue
            
            # Search and download stock footage
            footage_result = _search_and_download_footage(
                stock_provider,
                search_query,
                duration,
                scene_id,
                segment.get('properties', {})
            )
            
            if footage_result:
                footage_results.append(footage_result)
                
                # Update timeline segment with footage information
                segment['footage_file'] = footage_result['file_path']
                segment['footage_duration'] = footage_result['duration']
                segment['footage_resolution'] = footage_result['resolution']
                segment['footage_source'] = footage_result['source']
        
        # Create comprehensive stock footage results
        stock_results = {
            "footage_segments": footage_results,
            "total_segments": len(footage_results),
            "stock_provider": settings.stock_provider,
            "search_settings": {
                "quality": "HD",
                "format": "MP4",
                "orientation": "landscape"
            },
            "timeline_updated": timeline,
            "download_summary": {
                "successful": len(footage_results),
                "total_requested": len(video_segments),
                "total_size_mb": sum(result.get('file_size_mb', 0) for result in footage_results)
            },
            "generated_by": "ReelForge Stock Footage Tool",
            "version": "1.0"
        }
        
        logger.info("Stock footage search completed",
                   segments_found=len(footage_results),
                   total_size=stock_results["download_summary"]["total_size_mb"])
        
        return json.dumps(stock_results, indent=2)
        
    except Exception as e:
        error_msg = f"Stock footage search failed: {str(e)}"
        logger.error("Stock footage error", error=str(e))
        
        # Return error in expected format
        error_response = {
            "error": error_msg,
            "footage_segments": [],
            "total_segments": 0,
            "generated_by": "ReelForge Stock Footage Tool (Error)"
        }
        
        return json.dumps(error_response, indent=2)


def _get_stock_provider():
    """Initialize the appropriate stock footage provider"""
    if settings.stock_provider == "pexels":
        if not settings.pexels_api_key:
            logger.error("Pexels API key not configured")
            raise ValueError("Pexels API key required for stock footage")
        return {
            "type": "pexels",
            "api_key": settings.pexels_api_key,
            "base_url": "https://api.pexels.com/v1"
        }
    else:
        logger.warning(f"Unknown stock provider {settings.stock_provider}, using Pexels")
        return {
            "type": "pexels", 
            "api_key": settings.pexels_api_key,
            "base_url": "https://api.pexels.com/v1"
        }


def _search_and_download_footage(provider: Dict[str, Any], query: str, duration: float, scene_id: int, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Search for and download stock footage for a single segment"""
    try:
        # Create output directory
        output_dir = Path("outputs/footage")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate search keywords from query
        search_keywords = _extract_search_keywords(query, properties)
        
        logger.info(f"Searching footage for scene {scene_id}", query=query, keywords=search_keywords)
        
        # Search for videos
        if provider["type"] == "pexels":
            video_results = _search_pexels_videos(provider, search_keywords, duration)
        else:
            raise ValueError(f"Unsupported stock provider: {provider['type']}")
        
        if not video_results:
            logger.warning(f"No footage found for scene {scene_id}", query=query)
            return _create_fallback_footage(scene_id, duration, query)
        
        # Select best video
        selected_video = _select_best_video(video_results, duration, properties)
        
        # Download video
        video_filename = f"footage_{scene_id}_{hashlib.md5(query.encode()).hexdigest()[:8]}.mp4"
        video_path = output_dir / video_filename
        
        # Check if already downloaded (cache)
        if video_path.exists():
            logger.info(f"Using cached footage for scene {scene_id}")
            file_info = _get_video_info(str(video_path))
            return {
                "scene_id": scene_id,
                "file_path": str(video_path),
                "filename": video_filename,
                "duration": file_info["duration"],
                "resolution": file_info["resolution"],
                "search_query": query,
                "source": selected_video.get("source", "unknown"),
                "cached": True,
                "file_size_mb": os.path.getsize(video_path) / (1024 * 1024)
            }
        
        # Download the video
        success = _download_video(selected_video["url"], str(video_path))
        
        if not success:
            logger.error(f"Failed to download footage for scene {scene_id}")
            return _create_fallback_footage(scene_id, duration, query)
        
        # Get video information
        file_info = _get_video_info(str(video_path))
        
        logger.info(f"Downloaded footage for scene {scene_id}", 
                   duration=file_info["duration"],
                   resolution=file_info["resolution"])
        
        return {
            "scene_id": scene_id,
            "file_path": str(video_path),
            "filename": video_filename,
            "duration": file_info["duration"],
            "resolution": file_info["resolution"],
            "search_query": query,
            "source": selected_video.get("source", "pexels"),
            "video_id": selected_video.get("id"),
            "cached": False,
            "file_size_mb": os.path.getsize(video_path) / (1024 * 1024),
            "download_time": "now"  # In production, use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Failed to get footage for scene {scene_id}", error=str(e))
        return _create_fallback_footage(scene_id, duration, query)


def _extract_search_keywords(query: str, properties: Dict[str, Any]) -> str:
    """Extract and optimize search keywords from visual hint"""
    # Remove common filler words
    filler_words = {'the', 'a', 'an', 'with', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but'}
    words = query.lower().split()
    filtered_words = [word for word in words if word not in filler_words]
    
    # Add property-based keywords
    scene_type = properties.get('scene_type', '')
    if scene_type == 'product_focus':
        filtered_words.extend(['product', 'commercial'])
    elif scene_type == 'human_focus':
        filtered_words.extend(['people', 'lifestyle'])
    elif scene_type == 'action':
        filtered_words.extend(['dynamic', 'movement'])
    
    # Limit to most relevant keywords
    return ' '.join(filtered_words[:5])


def _search_pexels_videos(provider: Dict[str, Any], keywords: str, duration: float) -> List[Dict[str, Any]]:
    """Search Pexels for videos matching keywords"""
    try:
        headers = {
            "Authorization": provider["api_key"]
        }
        
        params = {
            "query": keywords,
            "per_page": 15,  # Get multiple options
            "size": "large",  # HD quality
            "orientation": "landscape"
        }
        
        response = requests.get(
            f"{provider['base_url']}/videos/search",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error("Pexels API error", status_code=response.status_code)
            return []
        
        data = response.json()
        videos = []
        
        for video in data.get('videos', []):
            # Find appropriate video file
            video_files = video.get('video_files', [])
            hd_file = None
            
            # Prefer HD quality
            for file_info in video_files:
                if file_info.get('quality') == 'hd' and file_info.get('file_type') == 'video/mp4':
                    hd_file = file_info
                    break
            
            if not hd_file:
                # Fallback to any MP4 file
                for file_info in video_files:
                    if file_info.get('file_type') == 'video/mp4':
                        hd_file = file_info
                        break
            
            if hd_file:
                videos.append({
                    "id": video.get('id'),
                    "url": hd_file.get('link'),
                    "duration": video.get('duration', 10),
                    "width": hd_file.get('width', 1920),
                    "height": hd_file.get('height', 1080),
                    "source": "pexels",
                    "tags": video.get('tags', []),
                    "user": video.get('user', {}).get('name', 'Unknown')
                })
        
        logger.info(f"Found {len(videos)} videos on Pexels", keywords=keywords)
        return videos
        
    except Exception as e:
        logger.error("Pexels search failed", error=str(e))
        return []


def _select_best_video(videos: List[Dict[str, Any]], target_duration: float, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Select the best video from search results"""
    if not videos:
        return None
    
    # Score videos based on multiple factors
    scored_videos = []
    
    for video in videos:
        score = 0
        
        # Duration score (prefer videos close to target duration)
        duration_diff = abs(video.get('duration', 10) - target_duration)
        if duration_diff <= 2:
            score += 3
        elif duration_diff <= 5:
            score += 2
        else:
            score += 1
        
        # Quality score (prefer HD)
        width = video.get('width', 0)
        if width >= 1920:
            score += 3
        elif width >= 1280:
            score += 2
        else:
            score += 1
        
        # Tag relevance (basic implementation)
        tags = video.get('tags', [])
        if len(tags) > 0:
            score += min(len(tags), 2)
        
        scored_videos.append((video, score))
    
    # Sort by score and return best
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    return scored_videos[0][0]


def _download_video(url: str, output_path: str) -> bool:
    """Download video file from URL"""
    try:
        logger.info("Downloading video", url=url[:50] + "...")
        
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify file was downloaded
        if os.path.getsize(output_path) < 1000:  # Less than 1KB
            logger.error("Downloaded file is too small")
            return False
        
        return True
        
    except Exception as e:
        logger.error("Video download failed", error=str(e))
        return False


def _get_video_info(video_path: str) -> Dict[str, Any]:
    """Get video information using FFmpeg"""
    try:
        import subprocess
        
        # Use FFprobe to get video info
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if video_stream:
                duration = float(info.get('format', {}).get('duration', 0))
                width = video_stream.get('width', 1920)
                height = video_stream.get('height', 1080)
                
                return {
                    "duration": duration,
                    "resolution": f"{width}x{height}",
                    "width": width,
                    "height": height,
                    "codec": video_stream.get('codec_name', 'unknown')
                }
        
        # Fallback values
        return {
            "duration": 10.0,
            "resolution": "1920x1080",
            "width": 1920,
            "height": 1080,
            "codec": "h264"
        }
        
    except Exception as e:
        logger.error("Failed to get video info", error=str(e))
        return {
            "duration": 10.0,
            "resolution": "1920x1080",
            "width": 1920,
            "height": 1080,
            "codec": "unknown"
        }


def _create_fallback_footage(scene_id: int, duration: float, query: str) -> Dict[str, Any]:
    """Create fallback footage when stock footage is unavailable"""
    try:
        # Create a simple colored background with text
        output_dir = Path("outputs/footage")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fallback_filename = f"fallback_{scene_id}.mp4"
        fallback_path = output_dir / fallback_filename
        
        # Generate simple video with FFmpeg
        import subprocess
        
        # Create colored background with text overlay
        cmd = [
            settings.ffmpeg_binary_path,
            "-f", "lavfi",
            "-i", f"color=color=0x333333:size=1920x1080:duration={duration}",
            "-vf", f"drawtext=text='{query[:30]}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-t", str(duration),
            "-y",  # Overwrite
            str(fallback_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Created fallback footage for scene {scene_id}")
            
            return {
                "scene_id": scene_id,
                "file_path": str(fallback_path),
                "filename": fallback_filename,
                "duration": duration,
                "resolution": "1920x1080",
                "search_query": query,
                "source": "fallback_generated",
                "cached": False,
                "file_size_mb": os.path.getsize(fallback_path) / (1024 * 1024),
                "is_fallback": True
            }
        else:
            logger.error("Failed to create fallback footage", error=result.stderr)
            return None
            
    except Exception as e:
        logger.error("Fallback footage creation failed", error=str(e))
        return None
