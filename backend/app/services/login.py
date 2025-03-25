# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session

# from db import models
# from db import database
# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def authenticate_user(username: str, password: str):
#     db = next(database.get_db())  # Lấy session từ generator
#     user = db.query(models.User).filter(models.User.username == username).first()
#     #if not user or not verify_password(password, user.password_hash):
#     #    return None
#     return user

