from fastapi import APIRouter, Request
from openai import OpenAI
import os
from dotenv import load_dotenv
from services.authentication_and_authorization import verify_user_access_token

load_dotenv()
router = APIRouter()
api_key = os.getenv("GENERATE_ANSWER_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

@router.post("/generate_answer")
async def generate_answer(
    request: Request, 
    generate_request: dict
):
    user_data = verify_user_access_token(source="cookie", request=request)
    user_question = generate_request.get("question")
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
