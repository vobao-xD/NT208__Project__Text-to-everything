from fastapi import APIRouter, Depends, FastAPI, Request
import json
import uuid
from fastapi.responses import RedirectResponse
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os

from db import get_db
load_dotenv()

router = APIRouter()


MOMO_ENDPOINT = os.getenv("MOMO_ENDPOINT")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
PARTNER_CODE = "MOMO"
REDIRECT_URL = os.getenv("REDIRECT_URL")
IPN_URL = os.getenv("IPN_URL")


@router.post("/momo/create-payment")
async def create_payment(amount: int):
    order_id = str(uuid.uuid4())  
    request_id = str(uuid.uuid4())  
    order_info = "Thanh toán qua MoMo"
    request_type = "captureWallet"  

    
    raw_signature = f"accessKey={ACCESS_KEY}&amount={amount}&extraData=&ipnUrl={IPN_URL}&orderId={order_id}" \
                    f"&orderInfo={order_info}&partnerCode={PARTNER_CODE}&redirectUrl={REDIRECT_URL}" \
                    f"&requestId={request_id}&requestType={request_type}"

    
    signature = hmac.new(SECRET_KEY.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()

    
    payload = {
        "partnerCode": PARTNER_CODE,
        "orderId": order_id,
        "partnerName": "MoMo Payment",
        "storeId": "Test Store",
        "ipnUrl": IPN_URL,
        "amount": amount,
        "lang": "vi",
        "requestType": request_type,
        "redirectUrl": REDIRECT_URL,
        "autoCapture": True,
        "orderInfo": order_info,
        "requestId": request_id,
        "extraData": "",
        "signature": signature
    }

    
    headers = {"Content-Type": "application/json"}
    response = requests.post(MOMO_ENDPOINT, json=payload, headers=headers)

    
    return response.json()
@router.post("/momo/callback")
async def callback(request: Request, db=Depends(get_db)):
    data = await request.json() 
    print("Received callback:", data)  

    transaction_status = data.get("resultCode")  
    user_id = data.get("partnerClientId")  
    plan = data.get("plan")  

    if transaction_status == 0:  
        new_role = "plus" if plan == "plus" else "pro"
        
        # UPDATE QUYỀN HẠN USER Ở ĐÂY 
        # await db.execute("UPDATE users SET role = $1 WHERE id = $2", new_role, user_id)

        return {"message": "Cập nhật thành công", "status": "success"}
    
    return {"message": "Thanh toán thất bại", "status": "failed"}
