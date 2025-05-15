from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    provider = Column(String, nullable=False, default="google")
    created_at = Column(DateTime, default=datetime.utcnow)
    role=Column(String,nullable=False,default="basic")
class TextInput(BaseModel):
    user_text: str
class ChatRequest(BaseModel):
    prompt: str

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())