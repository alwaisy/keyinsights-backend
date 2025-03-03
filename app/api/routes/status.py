from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import uuid

from app.models.schemas import ProcessingStatusResponse, ErrorResponse
from app.services.redis_service import RedisService

router = APIRouter()


@router.get(
    "/{request_id}",
    response_model=ProcessingStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Check processing status",
    description="Check the status of a long-running request"
)
async def check_status(request_id: str):
    """
    Check the status of a processing request.

    - **request_id**: The ID of the request to check
    """
    redis = RedisService()
    status = await redis.get_status(request_id)

    if status.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    return ProcessingStatusResponse(**status)