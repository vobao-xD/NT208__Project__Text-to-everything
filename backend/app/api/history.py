from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import schemas, crud, database

router = APIRouter()

# # Lưu lại request đã tạo
# @router.post("/save_request", response_model=schemas.RequestResponse)
# def save_request(
#     request_data: schemas.RequestCreate,
#     db: Session = Depends(database.get_db),
#     user: s
# )