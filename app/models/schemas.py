from pydantic import BaseModel, HttpUrl, Field, model_validator
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid


class TranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")


class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str


class InsightsRequest(BaseModel):
    text: str = Field(..., description="Text to extract insights from")
    model: Optional[str] = Field("openai/gpt-4o", description="AI model to use")


class InsightsResponse(BaseModel):
    insights: str


class CombinedRequest(BaseModel):
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    url: Optional[str] = Field(None, description="YouTube video URL")
    model: Optional[str] = Field("openai/gpt-4o", description="AI model to use")

    @model_validator(mode='after')
    def check_video_source(self):
        """Validate that either video_id or url is provided."""
        if not self.video_id and not self.url:
            raise ValueError("Either video_id or url must be provided")
        return self


class CombinedResponse(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    transcript: str = Field(..., description="Video transcript")
    insights: Optional[str] = Field(None, description="AI-generated insights about the video")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class ProcessingStatusResponse(BaseModel):
    status: str = Field(..., description="Status of the request: pending, processing, completed, failed")
    progress: float = Field(..., description="Progress from 0.0 to 1.0")
    message: str = Field(..., description="Status message")
    request_id: Optional[str] = Field(None, description="Request ID")
    estimated_completion_time: Optional[str] = Field(None, description="Estimated completion time in ISO format")
    error: Optional[str] = Field(None, description="Error message if status is failed")
    transcript: Optional[str] = Field(None, description="Transcript if available")
    insights: Optional[str] = Field(None, description="Insights if available")

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None