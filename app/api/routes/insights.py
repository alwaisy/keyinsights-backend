from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.schemas import InsightsRequest, InsightsResponse, ErrorResponse
from app.services.insights_service import InsightsService

router = APIRouter()


@router.post(
    "/",
    response_model=InsightsResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Generate insights from text",
    description="Extracts key insights from text using an AI model"
)
async def generate_insights(request: InsightsRequest):
    """
    Generate key insights from text.

    - **text**: Text to analyze
    - **model**: AI model to use (default: openai/gpt-4o)
    """
    insights = await InsightsService.get_insights(request.text, request.model)
    return InsightsResponse(insights=insights)