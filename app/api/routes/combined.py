from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional

from app.models.schemas import CombinedRequest, CombinedResponse, ErrorResponse
from app.services.transcript_service import TranscriptService
from app.services.insights_service import InsightsService
from app.utils.validators import extract_youtube_id, validate_youtube_id
from app.core.exceptions import YouTubeTranscriptError, AIModelError

router = APIRouter()


@router.post(
    "/",
    response_model=CombinedResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate transcript and insights from YouTube video",
    description="Extracts transcript from a YouTube video and generates key insights"
)
async def generate_transcript_and_insights(request: CombinedRequest):
    """
    Generate transcript and insights from a YouTube video.

    - **video_id**: YouTube video ID (optional if url is provided)
    - **url**: YouTube video URL (optional if video_id is provided)
    - **model**: AI model to use for insights (default: openai/gpt-4o)
    """
    # Determine video_id from either direct input or URL
    video_id = request.video_id
    if not video_id and request.url:
        video_id = extract_youtube_id(request.url)
        if not video_id:
            raise YouTubeTranscriptError("Could not extract a valid YouTube video ID from the URL")

    # Validate video_id format
    if not validate_youtube_id(video_id):
        raise YouTubeTranscriptError("Invalid YouTube video ID format")

    try:
        # Get transcript
        transcript = await TranscriptService.get_transcript(video_id)

        # Generate insights
        insights = await InsightsService.get_insights(transcript, request.model)

        return CombinedResponse(
            video_id=video_id,
            transcript=transcript,
            insights=insights
        )
    except YouTubeTranscriptError as e:
        raise e
    except AIModelError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )