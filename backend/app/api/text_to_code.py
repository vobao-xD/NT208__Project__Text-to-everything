from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from grpc import Status
import httpx
from openai import BaseModel
import requests
from db import schemas
from services.ai_services import TextToCodeService as service

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