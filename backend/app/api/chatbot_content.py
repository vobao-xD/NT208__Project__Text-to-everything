import httpx
from fastapi import APIRouter, HTTPException, Request
from db.schemas import ChatbotContentRequest
from services.authentication_and_authorization import verify_user_access_token

router = APIRouter()

@router.post("/chatbot/content")
async def chatbot_content(
    request: Request,
    payload: ChatbotContentRequest
):
    try:
        user_data = verify_user_access_token(source="cookie", request=request)
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=600.0) as internal_client:
            response = await internal_client.post(
                "/advanced/chatbot-content",
                json=payload.model_dump()
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))