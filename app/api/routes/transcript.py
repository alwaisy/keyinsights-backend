from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional

from app.models.schemas import TranscriptRequest, TranscriptResponse, ErrorResponse
from app.services.transcript_service import TranscriptService
from app.utils.validators import extract_youtube_id, validate_youtube_id
from app.core.exceptions import YouTubeTranscriptError

router = APIRouter()


@router.post(
    "/",
    response_model=TranscriptResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate transcript from YouTube video",
    description="Extracts transcript text from a YouTube video using its ID"
)
async def generate_transcript(request: TranscriptRequest):
    """
    Generate transcript from a YouTube video.

    - **video_id**: YouTube video ID (the part after v= in the URL)
    """
    if not validate_youtube_id(request.video_id):
        raise YouTubeTranscriptError("Invalid YouTube video ID format")

    transcript = await TranscriptService.get_transcript(request.video_id)
    return TranscriptResponse(video_id=request.video_id, transcript=transcript)


@router.get(
    "/",
    response_model=TranscriptResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Generate transcript from YouTube URL",
    description="Extracts transcript text from a YouTube video using its URL"
)
async def generate_transcript_from_url(
        url: str = Query(..., description="YouTube video URL")
):
    """
    Generate transcript from a YouTube video URL.

    - **url**: Full YouTube video URL
    """
    video_id = extract_youtube_id(url)
    if not video_id:
        raise YouTubeTranscriptError("Could not extract a valid YouTube video ID from the URL")

    transcript = await TranscriptService.get_transcript(video_id)
    return TranscriptResponse(video_id=video_id, transcript=transcript)