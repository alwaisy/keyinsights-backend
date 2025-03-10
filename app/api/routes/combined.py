import asyncio
import time
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status as http_status, BackgroundTasks, Request

from app.core.exceptions import YouTubeTranscriptError
from app.models.schemas import CombinedRequest, CombinedResponse, ErrorResponse, ProcessingStatusResponse, \
    TranscriptResponse
from app.services.insights_service import InsightsService
from app.services.redis_service import RedisService
from app.services.transcript_service import TranscriptService
from app.utils.validators import extract_youtube_id, validate_youtube_id

router = APIRouter()


def process_video(
        request_id: str,
        video_id: str,
        model: str,
        redis_service: RedisService
):
    """Background task to process video and generate insights"""
    start_time = time.time()
    loop = None

    try:
        # Create async event loop for this background task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Step 1: Update status to processing (2 hour TTL)
        loop.run_until_complete(redis_service.set_status(
            request_id,
            {
                "status": "processing",
                "progress": 0.1,
                "message": "Fetching transcript...",
                "video_id": video_id,  # Include video_id in all status updates
                "estimated_completion_time": (datetime.utcnow() + timedelta(minutes=2)).isoformat()
            },
            ttl=7200  # 2 hours
        ))

        # Step 2: Get transcript
        transcript_service = TranscriptService()
        transcript = loop.run_until_complete(transcript_service.get_transcript(video_id))

        # Step 3: Update status with transcript included
        loop.run_until_complete(redis_service.set_status(
            request_id,
            {
                "status": "processing",
                "progress": 0.5,
                "message": "Transcript ready. Generating insights...",
                "video_id": video_id,
                "estimated_completion_time": (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                "transcript": transcript  # Include transcript in status
            },
            ttl=7200  # 2 hours
        ))

        # Step 4: Store partial result with just transcript (1 hour TTL)
        partial_result = {
            "video_id": video_id,
            "transcript": transcript,
            "insights": None,
            "processing_time": time.time() - start_time
        }

        # Cache partial result
        loop.run_until_complete(redis_service.set(
            f"result:{request_id}",
            partial_result,
            ttl=3600,  # 1 hour
            compress=True
        ))

        # Step 5: Generate insights
        insights_service = InsightsService()
        try:
            insights = loop.run_until_complete(insights_service.get_insights(transcript, model))

            # Step 6: Store complete result (24 hour TTL)
            complete_result = {
                "video_id": video_id,
                "transcript": transcript,
                "insights": insights,
                "processing_time": time.time() - start_time
            }

            # Cache complete result
            loop.run_until_complete(redis_service.set(
                f"result:{request_id}",
                complete_result,
                ttl=86400,  # 24 hours
                compress=True
            ))

            # Step 7: Update status to completed
            loop.run_until_complete(redis_service.set_status(
                request_id,
                {
                    "status": "completed",
                    "progress": 1.0,
                    "message": "Processing complete",
                    "request_id": request_id,
                    "video_id": video_id,
                    "transcript": transcript,
                    "insights": insights
                },
                ttl=7200  # 2 hours
            ))

        except Exception as insights_error:
            # Handle AI model error gracefully
            print(f"Error generating insights: {str(insights_error)}")

            # Create a user-friendly error message
            error_message = "We couldn't generate insights for this video."
            if "no insights were generated" in str(insights_error).lower():
                error_message += " The AI model couldn't extract meaningful information from the transcript."
            elif "api request failed" in str(insights_error).lower():
                error_message += " There was an issue connecting to the AI service."

            # Update status with partial success
            loop.run_until_complete(redis_service.set_status(
                request_id,
                {
                    "status": "partial_success",
                    "progress": 0.5,
                    "message": error_message,
                    "error": str(insights_error),
                    "video_id": video_id,
                    "request_id": request_id,
                    "transcript": transcript,
                    "insights": None
                },
                ttl=7200  # 2 hours
            ))

            # Store partial result with just transcript and error info
            partial_result = {
                "video_id": video_id,
                "transcript": transcript,
                "insights": None,
                "error": str(insights_error),
                "processing_time": time.time() - start_time
            }

            # Cache partial result
            loop.run_until_complete(redis_service.set(
                f"result:{request_id}",
                partial_result,
                ttl=86400,  # 24 hours - keep it for as long as a successful result
                compress=True
            ))

    except Exception as e:
        # Log the exception for debugging
        import traceback
        print(f"Error in process_video: {str(e)}")
        print(traceback.format_exc())

        try:
            # Ensure we have a working event loop
            if loop is None or loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Update status to failed
            loop.run_until_complete(redis_service.set_status(
                request_id,
                {
                    "status": "failed",
                    "progress": 0,
                    "message": f"Processing failed: {str(e)}",
                    "error": str(e),
                    "video_id": video_id
                },
                ttl=7200  # 2 hours
            ))
        except Exception as inner_e:
            print(f"Error updating failure status: {str(inner_e)}")
            print(traceback.format_exc())
    finally:
        # Always ensure the loop is closed properly
        if loop is not None and not loop.is_closed():
            try:
                # Run any pending tasks before closing
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as close_error:
                print(f"Error cleaning up pending tasks: {str(close_error)}")
            finally:
                loop.close()


@router.post(
    "/",
    response_model=ProcessingStatusResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate transcript and insights from YouTube video",
    description="Starts processing a YouTube video to extract transcript and insights"
)
async def generate_transcript_and_insights(
        request: CombinedRequest,
        background_tasks: BackgroundTasks,
        req: Request
):
    """
    Start processing a YouTube video to extract transcript and insights.

    - **video_id**: YouTube video ID (optional if url is provided)
    - **url**: YouTube video URL (optional if video_id is provided)
    - **model**: AI model to use for insights (default: deepseek/deepseek-chat:free)

    Returns a request ID that can be used to check processing status.
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

    # Generate request ID
    request_id = str(uuid.uuid4())
    redis = RedisService()

    # Set initial status
    await redis.set_status(
        request_id,
        {
            "status": "pending",
            "progress": 0,
            "message": "Request queued",
            "estimated_completion_time": (datetime.utcnow() + timedelta(minutes=3)).isoformat(),
            "request_id": request_id
        }
    )

    # Start background processing - THIS IS THE KEY PART
    background_tasks.add_task(
        process_video,
        request_id,
        video_id,
        request.model,
        redis
    )

    # Return status response IMMEDIATELY without waiting for processing
    return ProcessingStatusResponse(
        status="pending",
        progress=0,
        message="Your request is being processed. Check status endpoint for updates.",
        request_id=request_id,
        estimated_completion_time=(datetime.utcnow() + timedelta(minutes=3)).isoformat()
    )


@router.get(
    "/result/{request_id}",
    response_model=CombinedResponse,
    responses={
        404: {"model": ErrorResponse},
        202: {"model": ProcessingStatusResponse}
    },
    summary="Get processing result",
    description="Get the result of a processed YouTube video"
)
@router.get(
    "/result/{request_id}",
    response_model=CombinedResponse,
    responses={
        404: {"model": ErrorResponse},
        202: {"model": ProcessingStatusResponse}
    },
    summary="Get processing result",
    description="Get the result of a processed YouTube video"
)
async def get_processing_result(request_id: str, include_partial: bool = True):
    """
    Get the result of a processed YouTube video.

    - **request_id**: The ID of the request to get results for
    - **include_partial**: If True, return partial results when available
    """
    redis = RedisService()

    # Check if result exists
    result = await redis.get(f"result:{request_id}", decompress=True)
    if result:
        # If we have a result with insights or user wants partial results
        if result.get("insights") or include_partial:
            return CombinedResponse(**result)

    # Check status
    status = await redis.get_status(request_id)
    if status.get("status") == "not_found":
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Return 202 Accepted with status
    raise HTTPException(
        status_code=http_status.HTTP_202_ACCEPTED,
        detail=status
    )


@router.get(
    "/transcript/{request_id}",
    response_model=TranscriptResponse,
    responses={
        404: {"model": ErrorResponse},
        202: {"model": ProcessingStatusResponse}
    },
    summary="Get transcript only",
    description="Get just the transcript of a processed YouTube video"
)
async def get_transcript_only(request_id: str):
    """
    Get just the transcript of a processed YouTube video.

    - **request_id**: The ID of the request to get transcript for
    """
    redis = RedisService()

    # Check if result exists
    result = await redis.get(f"result:{request_id}", decompress=True)
    if result and result.get("transcript"):
        return TranscriptResponse(
            video_id=result["video_id"],
            transcript=result["transcript"]
        )

    # Check status
    status = await redis.get_status(request_id)
    if status.get("status") == "not_found":
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # If transcript is in status but not in result yet
    if status.get("transcript"):
        return TranscriptResponse(
            video_id=status.get("video_id", "unknown"),
            transcript=status["transcript"]
        )

    # Return 202 Accepted with status
    raise HTTPException(
        status_code=http_status.HTTP_202_ACCEPTED,
        detail=status
    )
