from fastapi import APIRouter, Depends
from db.database import get_db
from db.models import User
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/role")
def get_role(user_email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    return user.role