import os
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import re


def ensure_dir_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
    """
    os.makedirs(directory, exist_ok=True)


def sniff_video_from_webpage(url: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Extract the first video from a webpage using yt-dlp.
    
    Args:
        url: Webpage URL
        output_dir: Directory to save the video in
        
    Returns:
        Path to the extracted video file or None if extraction failed
    """
    try:
        import yt_dlp
        
        if output_dir:
            ensure_dir_exists(output_dir)
        else:
            output_dir = tempfile.gettempdir()
        
        # Generate a unique filename based on the URL
        url_hash = re.sub(r'[^a-zA-Z0-9]', '', url)[-20:]
        output_template = os.path.join(output_dir, f"video_{url_hash}.%(ext)s")
        
        print(f"Extracting video from: {url}")
        print("This may take some time depending on the website...")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer mp4 format
            'outtmpl': output_template,
            'noplaylist': True,  # Extract only the first video
            'quiet': False,
            'no_warnings': True,
            'extractaudio': False,
            'verbose': False
        }
        
        # Extract video information first
        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                # If this is a playlist, get the first video
                info = info['entries'][0] if info['entries'] else None
            
            if not info:
                print("No video found on the webpage")
                return None
                
            video_title = info.get('title', 'unknown_video')
            video_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
            video_title = video_title.replace(" ", "_")
            
            print(f"Found video: {video_title}")
            
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                info = info['entries'][0] if info['entries'] else None
            
            if not info:
                print("Failed to download video")
                return None
            
            # Get the downloaded file path
            if '_filename' in info:
                file_path = info['_filename']
            else:
                # Fallback if _filename is not available
                ext = info.get('ext', 'mp4')
                file_path = os.path.join(output_dir, f"video_{url_hash}.{ext}")
            
            print(f"Video extracted to: {file_path}")
            return file_path
            
    except ImportError:
        print("Error: yt-dlp is required to extract videos from webpages.")
        print("Install it using: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"Error extracting video: {str(e)}")
        return None


def download_youtube_video(url: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Download a YouTube video (legacy function - use sniff_video_from_webpage instead).
    
    Args:
        url: YouTube URL
        output_dir: Directory to save the video in
        
    Returns:
        Path to the downloaded video file or None if download failed
    """
    # Now we just use the more general sniff_video_from_webpage function
    return sniff_video_from_webpage(url, output_dir)


def get_timestamp_str(frame_number: int, fps: float) -> str:
    """
    Convert frame number to timestamp string.
    
    Args:
        frame_number: Frame number in video
        fps: Frames per second
        
    Returns:
        Timestamp string in format HH:MM:SS
    """
    seconds = frame_number / fps
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
