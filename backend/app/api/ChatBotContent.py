import requests
from fastapi import APIRouter
from pydantic import BaseModel
from db.schemas import ChatRequest
import os
router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.post("/chatbot/content")
def chatbot_content(data: ChatRequest):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-3.5-turbo",  # Hoặc dùng model khác như "mistralai/mixtral-8x7b"
        "messages": [
            {"role": "system", "content": "Bạn là một chatbot sáng tạo nội dung."},
            {"role": "user", "content": data.prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    reply = response.json()
    return {
        "response": reply["choices"][0]["message"]["content"]
    }