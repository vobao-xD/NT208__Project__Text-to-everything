import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from grpc import Status
import httpx

load_dotenv()

class TextToCodeService:
    api_key = os.getenv("TEXT_TO_CODE_API_KEY")

    @staticmethod
    async def text_to_code(prompt: str):
        headers = {
    "Authorization": f"Bearer {TextToCodeService.api_key}",
    "Content-Type": "application/json"
    }

        data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Bạn là một lập trình viên xuất chúng và tinh thông mọi ngôn ngữ lập trình."},
            {"role": "user", "content": prompt}
        ]
    }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                res = response.json()
                return {"code": res["choices"][0]["message"]["content"]}
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=Status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to connect to OpenRouter: {str(e)}"
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"OpenRouter API error: {e.response.text}"
                )
            except (KeyError, IndexError) as e:
                raise HTTPException(
                    status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error parsing OpenRouter response"
                )