# YouTube Insights API

A FastAPI application for extracting and analyzing YouTube video transcripts.

## Features

- Extract transcripts from YouTube videos
- Generate key insights from text using AI models

## Setup

1. Clone the repository
2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Create a `.env` file based on `.env.example` and add your OpenRouter API key
5. Run the application:
```
 uvicorn app.main:app --reload
```

## API Endpoints

### Generate Transcript
```
POST /api/transcript/
```
Request body:
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```
### Generate Insights

```
POST /api/insights/
```

Request body:
```json
{
  "text": "Your text here...",
  "model": "openai/gpt-4o"
}
```

### Combined Transcript and Insights
Request body:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "model": "openai/gpt-4o"
}
```
OR 
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "model": "openai/gpt-4o"
}
```

Response:
```json
{
  "status": "pending",
  "progress": 0,
  "message": "Your request is being processed. Check status endpoint for updates.",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "estimated_completion_time": "2023-04-01T12:30:45.123456"
}
```

### Check Processing Status

`GET /api/status/{request_id}`

Response:
```json
{
  "status": "processing",
  "progress": 0.5,
  "message": "Generating insights...",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "estimated_completion_time": "2023-04-01T12:30:45.123456"
}
```

### Get Processing Result

`GET /api/combined/result/{request_id}`

Response:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcript": "Never gonna give you up, never gonna let you down...",
  "insights": "This song is about unwavering loyalty and commitment...",
  "processing_time": 12.34
}
```

### Rate Limiting

The API implements rate limiting of 10 requests per hour per IP address. When rate limit is exceeded, you'll receive a 429 response:

```json 
{
  "detail": "Rate limit exceeded. Try again later.",
  "error_code": "rate_limit_exceeded",
  "requests_remaining": 0,
  "reset_at": "2023-04-01T13:00:00.000000"
}
```

Rate limit information is also available in response headers:

- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets


## Documentation
API documentation is available at /docs when the server is running.
