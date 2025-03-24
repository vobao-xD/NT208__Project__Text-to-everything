from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from . import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    conversations = relationship("Conversation", back_populates="user")
    requests = relationship("Request", back_populates="user")
    shares = relationship("Share", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")

class Request(Base):
    __tablename__ = "request"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    input_type = Column(String, nullable=False)  # text, audio, file
    input_text = Column(String, nullable=True)
    input_audio_url = Column(String, nullable=True)
    output_type = Column(String, nullable=False)  # speech, image, video
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="requests")
    responses = relationship("Response", back_populates="request")

class Response(Base):
    __tablename__ = "response"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("request.id"), nullable=False)
    output_type = Column(String, nullable=False)  # speech, image, video
    output_url = Column(String, nullable=False)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    request = relationship("Request", back_populates="responses")
    shares = relationship("Share", back_populates="response")

class Share(Base):
    __tablename__ = "share"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    response_id = Column(Integer, ForeignKey("response.id"), nullable=False)
    platform = Column(String, nullable=False)  # facebook, twitter, etc.
    type = Column(String, nullable=False)  # text, image, video
    shared_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="shares")
    response = relationship("Response", back_populates="shares")