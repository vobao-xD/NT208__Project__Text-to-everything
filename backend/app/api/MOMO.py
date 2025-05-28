from fastapi import APIRouter, Depends, FastAPI, Request,HTTPException
import json
import uuid
from fastapi.responses import RedirectResponse
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os
from db.models import User,Transaction

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
    try:  
        data = await request.json() 
        print("Received callback:", data)  

        transaction_status = data.get("resultCode")  
        user_id = data.get("partnerClientId")  
        plan = data.get("plan")  
        order_id=data.get("order_id")

        if not all ([transaction_status is not None,user_id,plan]):
            #Ông tướng nào viết code khó hiểu vậy???
            raise HTTPException(status_code=400,detail="Thiếu thông tin ")
        
        raw_signature = (
                f"accessKey={ACCESS_KEY}&amount={data.get('amount')}&extraData={data.get('extraData')}"
                f"&message={data.get('message')}&orderId={order_id}&orderInfo={data.get('orderInfo')}"
                f"&orderType={data.get('orderType')}&partnerCode={PARTNER_CODE}"
                f"&payType={data.get('payType')}&requestId={data.get('requestId')}"
                f"&responseTime={data.get('responseTime')}&resultCode={transaction_status}"
                f"&transId={data.get('transId')}"
            )
        signature = hmac.new(SECRET_KEY.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()

        if signature != data.get("signature"):
                raise HTTPException(status_code=400, detail="Chữ ký không hợp lệ")

        
        if transaction_status == 0:  
            new_role = "plus" if plan.lower() == "plus" else "pro"

            # UPDATE QUYỀN HẠN USER Ở ĐÂY 
            user=db.query(User).filter(User.id==user_id).first()
            if not user:
                raise HTTPException(status_code=400,detail="User không tồn tại")
            
            user.role=new_role

            transaction = Transaction(
                    order_id=order_id,
                    user_id=user_id,
                    amount=data.get("amount"),
                    plan=plan,
                    status="success"
                )
            db.add(transaction)
            db.commit()

            return {"message": "Cập nhật thành công", "status": "success"}
        else:
                # Lưu giao dịch thất bại
                transaction = Transaction(
                    order_id=order_id,
                    user_id=user_id,
                    amount=data.get("amount"),
                    plan=plan,
                    status="failed"
                )
                db.add(transaction)
                db.commit()

                return {"message": "Thanh toán thất bại", "status": "failed"}
    except Exception as ex:
        raise HTTPException(status_code=400,detail=f"Lỗi xử lý callback: {ex}")
