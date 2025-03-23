from sqlalchemy.orm import Session
from db import models, schemas

# Lưu request của người dùng
def create_request(db: Session, request_data: schemas.RequestCreate, user_id: int):
    db_request = models.Request(**request_data.dict(), user_id=user_id)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
    
# Lưu response từ AI
def create_response(db: Session, response_data: schemas.ResponseCreate, request_id: int):
    db_request = models.Request(**response_data.dict(), request_id=request_id)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

# Lấy lịch sử chat của người dùng
def get_chat_history(db: Session, user_id: int, limit: int = 10):
    return (
        db.query(models.Request)
        .filter(models.Request.user_id == user_id)
        .order_by(models.Request.created_at.desc())
        .limit(limit)
        .all()
    )