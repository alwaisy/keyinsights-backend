import re
from typing import Optional


def validate_youtube_id(video_id: str) -> bool:
    """
    Validates if a string is a valid YouTube video ID.

    Args:
        video_id: String to validate

    Returns:
        True if valid, False otherwise
    """
    # YouTube IDs are typically 11 characters long and contain alphanumeric chars, underscores, and hyphens
    pattern = r'^[A-Za-z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))


def extract_youtube_id(url: str) -> Optional[str]:
    """
    Extracts YouTube video ID from various URL formats.

    Args:
        url: YouTube URL

    Returns:
        Video ID if found, None otherwise
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?.*v=)([A-Za-z0-9_-]{11})',
        r'youtube\.com\/shorts\/([A-Za-z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None