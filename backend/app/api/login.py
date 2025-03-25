# from fastapi import FastAPI, APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db import schemas,database 
# from services.login import authenticate_user, create_access_token

# router = APIRouter()

# SECRET_KEY = "SOMETHING"
# ALGORITH = "HS256"
# login_access_token = 30

# @router.post("/login/")
# def login_access_token(user: schemas.User):

#     user = authenticate_user(user.username, user.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
