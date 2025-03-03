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

## Documentation
API documentation is available at /docs when the server is running.
