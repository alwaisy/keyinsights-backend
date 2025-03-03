from pydantic import BaseModel, HttpUrl, Field, model_validator
from typing import List, Dict, Any, Optional


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
    video_id: str
    transcript: str
    insights: str

class CombinedResponse(BaseModel):
    video_id: str
    transcript: str
    insights: str

class ErrorResponse(BaseModel):
    detail: str

