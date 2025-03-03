from fastapi import HTTPException, status


class YouTubeTranscriptError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"X-Error-Code": "youtube_transcript_error"}
        )


class AIModelError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers={"X-Error-Code": "ai_model_error"}
        )


class RateLimitExceededError(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded. Try again later."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"X-Error-Code": "rate_limit_exceeded"}
        )


class ProcessingError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers={"X-Error-Code": "processing_error"}
        )


class RequestNotFoundError(HTTPException):
    def __init__(self, request_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found",
            headers={"X-Error-Code": "request_not_found"}
        )