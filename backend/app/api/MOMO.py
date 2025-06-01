from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, FastAPI, Request, HTTPException
from pydantic import BaseModel
import json
import uuid
from fastapi.responses import RedirectResponse
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os
from db.models import User, Transaction
from db.schemas import PaymentRequest, UserSubscription

from db import get_db

load_dotenv()

router = APIRouter()

MOMO_ENDPOINT = os.getenv("MOMO_ENDPOINT")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY_MOMO")
PARTNER_CODE = "MOMO"
REDIRECT_URL = os.getenv("REDIRECT_URL")
IPN_URL = os.getenv("IPN_URL")


@router.post("/momo/create-payment")
async def create_payment(request: PaymentRequest):
    amount = request.amount
    email = request.email
    plan = request.plan
    order_id = str(uuid.uuid4())  
    request_id = str(uuid.uuid4())  
    order_info = "Thanh toán qua MoMo"
    request_type = "captureWallet"
    billing_cycle = request.billing_cycle
    current_role = request.current_role
    current_billing_cycle = request.current_billing_cycle

    # Lưu thông tin user_id và plan vào extraData
    extra_data = json.dumps({"email": email, "plan": plan, "billing_cycle": billing_cycle, "current_role": current_role, "current_billing_cycle": current_billing_cycle})
    
    raw_signature = f"accessKey={ACCESS_KEY}&amount={amount}&extraData={extra_data}&ipnUrl={IPN_URL}&orderId={order_id}" \
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
        "extraData": extra_data,  
        "signature": signature
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(MOMO_ENDPOINT, json=payload, headers=headers)

    return response.json()


@router.post("/momo/callback")
async def callback(request: Request, db=Depends(get_db)):
    print("=== CALLBACK ĐƯỢC GỌI ===")
    try:  
        data = await request.json() 
        print("Received callback:", data)  

        transaction_status = data.get("resultCode")  
        order_id = data.get("orderId")  # Sửa từ order_id thành orderId
        
        # Lấy thông tin từ extraData
        extra_data_str = data.get("extraData", "")
        email = None
        plan = None
        billing_cycle = None
        current_role = None
        current_billing_cycle = None
        if extra_data_str:
            try:
                extra_data = json.loads(extra_data_str)
                email = extra_data.get("email")
                plan = extra_data.get("plan")
                billing_cycle = extra_data.get("billing_cycle")
                current_role = extra_data.get("current_role")
                current_billing_cycle = extra_data.get("current_billing_cycle")
            except json.JSONDecodeError:
                print("Error parsing extraData")

        if not all([transaction_status is not None, email, plan, billing_cycle]):
            raise HTTPException(status_code=400, detail="Thiếu thông tin cần thiết")
        
        # Xác thực signature
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

        if transaction_status == 0:  # Thanh toán thành công

            if current_billing_cycle == "monthly":
                expires_at = datetime.now() + timedelta(days=30)
            elif current_billing_cycle == "yearly":
                expires_at = datetime.now() + timedelta(days=365)
            else:
                raise HTTPException(status_code=400, detail="Loại hợp đồng không hợp lệ")

            new_role = "plus" if plan.lower() == "plus" else "pro"

            new_billing_cycle = billing_cycle

            # Cập nhật quyền hạn user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=400, detail="User không tồn tại")
            
            # Cập nhật role
            user.role = new_role
            user.billing_cycle = new_billing_cycle
            user.expires_at = expires_at
            print(f"Updated user {email} role to {new_role}")
            
            # Tạo transaction record
            transaction = Transaction(
                order_id=order_id,
                email=email,
                amount=data.get("amount"),
                plan=plan,
                status="success",
                expires_at=expires_at,
                billing_cycle=billing_cycle
            )
            db.add(transaction)
            
            # QUAN TRỌNG: Commit cả user update và transaction
            db.commit()
            db.refresh(user)  # Refresh để đảm bảo user được cập nhật
            
            print(f"Transaction completed successfully for user {email}")
            return {"message": "Cập nhật thành công", "status": "success"}
        else:
            # Lưu giao dịch thất bại
            transaction = Transaction(
                order_id=order_id,
                email=email,
                amount=data.get("amount"),
                plan=plan,
                status="failed",
                expires_at=None,
                billing_cycle=billing_cycle
            )
            db.add(transaction)
            db.commit()

            return {"message": "Thanh toán thất bại", "status": "failed"}
            
    except Exception as ex:
        db.rollback()  # Rollback nếu có lỗi
        print(f"Error in callback: {ex}")
        raise HTTPException(status_code=400, detail=f"Lỗi xử lý callback: {ex}")
@router.get("/user-subscription", response_model=UserSubscription)
async def get_user_subscription(email: str, db=Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserSubscription(role=user.role, billingCycle=user.billing_cycle)
    finally:
        db.close()