from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json

# Step 1: Get YouTube transcript
video_id = 'CD-doKLl3-M'  # Replace with your YouTube video ID
captions = YouTubeTranscriptApi.get_transcript(video_id)

# Step 2: Format transcript (using plain text concatenation)
full_transcript = ' '.join([item['text'] for item in captions])

print(full_transcript)

# Step 3: Send to AI model via OpenRouter
response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",  # Replace with your actual API key
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "deepseek/deepseek-chat:free",  # You can use "deepseek/deepseek-chat:free" or other models
    "messages": [
      {
        "role": "system",
        "content": "I found transcript of Youtube video. Be concise. I need key insights from it not the whole video."
      },
      {
        "role": "user",
        "content": full_transcript
      }
    ]
  })
)

# Step 4: Print the response
print(response.json())
