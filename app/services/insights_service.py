import json
import requests
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.exceptions import AIModelError


class InsightsService:
    @staticmethod
    async def get_insights(text: str, model: str = "openai/gpt-4o") -> str:
        """
        Extracts key insights from text using an AI model.

        Args:
            text: Text to analyze
            model: AI model to use

        Returns:
            Key insights extracted from the text

        Raises:
            AIModelError: If insights cannot be generated
        """
        try:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }

            # Add optional headers if configured
            if settings.OPENROUTER_SITE_URL:
                headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
            if settings.OPENROUTER_SITE_NAME:
                headers["X-Title"] = settings.OPENROUTER_SITE_NAME

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "I found transcript of Youtube video. Be concise. I need key insights from it not the whole video."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code != 200:
                raise AIModelError(f"API request failed with status {response.status_code}: {response.text}")

            response_data = response.json()
            insights = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not insights:
                raise AIModelError("No insights were generated")

            return insights

        except requests.RequestException as e:
            raise AIModelError(f"Request error: {str(e)}")
        except json.JSONDecodeError:
            raise AIModelError("Failed to parse API response")
        except Exception as e:
            raise AIModelError(f"Unexpected error: {str(e)}")