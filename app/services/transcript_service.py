from typing import List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.core.exceptions import YouTubeTranscriptError


class TranscriptService:
    @staticmethod
    async def get_transcript(video_id: str) -> str:
        """
        Fetches transcript for a YouTube video and returns it as plain text.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript text as a string

        Raises:
            YouTubeTranscriptError: If transcript cannot be retrieved
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Convert transcript list to plain text
            formatter = TextFormatter()
            text_transcript = formatter.format_transcript(transcript_list)

            return text_transcript

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise YouTubeTranscriptError(f"Failed to retrieve transcript: {str(e)}")
        except Exception as e:
            raise YouTubeTranscriptError(f"Unexpected error: {str(e)}")