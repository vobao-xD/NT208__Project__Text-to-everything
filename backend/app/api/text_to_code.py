from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from grpc import Status
import httpx
from openai import BaseModel
import requests

load_dotenv()

router = APIRouter()
api_key = os.getenv("TEXT_TO_CODE_API_KEY")

class TextToCodeRequest(BaseModel):
    prompt: str
    
@router.post("/text-to-code",response_model=dict)
async def text_to_code(request: TextToCodeRequest):
    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": request.prompt}
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
