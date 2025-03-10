# app/services/transcript_service.py

from typing import List, Dict, Any

from app.core.exceptions import YouTubeTranscriptError
from app.utils.youtube_transcript import (
    YoutubeTranscript,
    YoutubeTranscriptError as BaseYoutubeTranscriptError
)


class TranscriptService:
    @staticmethod
    async def get_transcript(video_id: str, lang: str = "en") -> str:
        """
        Fetches transcript for a YouTube video and returns it as plain text.

        Args:
            video_id: YouTube video ID
            lang: Language code (default: "en")

        Returns:
            Transcript text as a string

        Raises:
            YouTubeTranscriptError: If transcript cannot be retrieved
        """
        try:
            youtube_transcript = YoutubeTranscript()
            transcript_items, video_title = youtube_transcript.fetch_transcript(video_id, lang)

            # Convert transcript items to plain text
            text_parts = [item.text for item in transcript_items]
            text_transcript = " ".join(text_parts)

            return text_transcript

        except BaseYoutubeTranscriptError as e:
            # Map our custom exceptions to the API's exception
            raise YouTubeTranscriptError(str(e))
        except Exception as e:
            raise YouTubeTranscriptError(f"Unexpected error: {str(e)}")

    @staticmethod
    async def get_transcript_with_timing(video_id: str, lang: str = "en") -> List[Dict[str, Any]]:
        """
        Fetches transcript for a YouTube video and returns it with timing information.

        Args:
            video_id: YouTube video ID
            lang: Language code (default: "en")

        Returns:
            List of transcript segments with timing information

        Raises:
            YouTubeTranscriptError: If transcript cannot be retrieved
        """
        try:
            youtube_transcript = YoutubeTranscript()
            transcript_items, video_title = youtube_transcript.fetch_transcript(video_id, lang)

            # Convert transcript items to dictionary format
            result = []
            for item in transcript_items:
                result.append({
                    "text": item.text,
                    "start": item.offset,
                    "duration": item.duration
                })

            return result

        except BaseYoutubeTranscriptError as e:
            # Map our custom exceptions to the API's exception
            raise YouTubeTranscriptError(str(e))
        except Exception as e:
            raise YouTubeTranscriptError(f"Unexpected error: {str(e)}")

    @staticmethod
    async def get_transcript_and_title(video_id: str, lang: str = "en") -> Dict[str, Any]:
        """
        Fetches transcript and title for a YouTube video.

        Args:
            video_id: YouTube video ID
            lang: Language code (default: "en")

        Returns:
            Dictionary with transcript text and video title

        Raises:
            YouTubeTranscriptError: If transcript cannot be retrieved
        """
        try:
            youtube_transcript = YoutubeTranscript()
            transcript_items, video_title = youtube_transcript.fetch_transcript(video_id, lang)

            # Convert transcript items to plain text
            text_parts = [item.text for item in transcript_items]
            text_transcript = " ".join(text_parts)

            return {
                "transcript": text_transcript,
                "title": video_title
            }

        except BaseYoutubeTranscriptError as e:
            # Map our custom exceptions to the API's exception
            raise YouTubeTranscriptError(str(e))
        except Exception as e:
            raise YouTubeTranscriptError(f"Unexpected error: {str(e)}")
