import os
from fastapi import APIRouter, Depends
from db.database import get_db
from db.models import User
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from jose import jwt, JWTError
load_dotenv()   

router = APIRouter()

def get_user_info_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    return {
        "email": user.email,
        "role": user.role,
        "expire": user.expires_at
    }

@router.get("/role")
def get_role(email: str, db: Session = Depends(get_db)):
    data = get_user_info_by_email(email, db)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data

app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

@router.get("/api/user-info")
async def get_user_info(request: Request,db=Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: email not found")
        data=get_user_info_by_email(email,db)
        print(data)
        if not data:
            raise HTTPException(status_code=401,detail="User not found")
        return data
    except JWTError as e:
        print(f"JWT error: {str(e)}")  # Debug log
        raise HTTPException(status_code=401, detail="Invalid token")