from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    provider = Column(String, nullable=False, default="google")
    created_at = Column(DateTime, default=datetime.utcnow)
class TextInput(BaseModel):
    user_text: str
class ChatRequest(BaseModel):
    prompt: str