from fastapi import APIRouter, HTTPException
from services import TextToCodeService as service
from dotenv import load_dotenv
from db import schemas
import os

load_dotenv()

router = APIRouter()
api_key = os.getenv("TEXT_TO_CODE_API_KEY")


@router.post("/",response_model=dict)
async def text_to_code(request: schemas.TTCRequest):
    try:
        code = await service.text_to_code(request.prompt)
        if (not code):
            return {"status": 500,"error": "unknown error"}
        return {"status": 500, "code": code}
    except HTTPException as e:
        return {"status": e.status_code, "Error": e.detail}
    except Exception as e:
        return {"status": 500, "Error": str(e)}