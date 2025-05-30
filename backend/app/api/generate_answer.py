from fastapi import APIRouter
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
api_key = os.getenv("GENERATE_ANSWER_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

@router.post("/generate_answer")
async def generate_answer(request: dict):
    user_question = request.get("question")
    if not user_question:
        return {"error": "Missing 'question' in request body"}

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[{"role": "user", "content": user_question}]
        )
        answer = response.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
