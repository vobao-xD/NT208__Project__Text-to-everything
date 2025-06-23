from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Session
from services.authentication_and_authorization import verify_user_access_token
from db.database import get_db
from services import TextToCodeService as service
from dotenv import load_dotenv
from db.schemas import TTCRequest, TTCResponse 
import os

load_dotenv()

router = APIRouter()
api_key = os.getenv("TEXT_TO_CODE_API_KEY")

@router.post("/", response_model=TTCResponse)
async def text_to_code(
    request: Request,
    TTC_request: TTCRequest
    ):
    try:
        user_data = verify_user_access_token(source="cookie", request=request)
        return await service.text_to_code(user_data, TTC_request.prompt)
    except HTTPException as e:
        return {"Status": e.status_code, "Error": e.detail}
    except Exception as e:
        return {"Status": 500, "Error": str(e)}