from fastapi import APIRouter, Depends
from db.database import get_db
from db.models import User
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/role")
def get_role(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return user.role
from fastapi import FastAPI, Request, HTTPException
from jose import jwt, JWTError

app = FastAPI()
SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256"

@router.get("/api/user-info")
async def get_user_info(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: email not found")
        return {"email": email}
    except JWTError as e:
        print(f"JWT error: {str(e)}")  # Debug log
        raise HTTPException(status_code=401, detail="Invalid token")