from fastapi import APIRouter
from openai import OpenAI

router = APIRouter()

client = OpenAI(
    api_key="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",
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
