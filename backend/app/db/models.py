from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    avatar = Column(String(2048), nullable=True)
    provider = Column(String, nullable=False, default="unknown")
    role = Column(String, nullable=False, default="free")
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String, default="monthly")
    notification_sent = Column(Boolean, default=False)

    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String, default="monthly")

    user = relationship("User", back_populates="transactions")

class Generator(Base):
    __tablename__ = "generators"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    input_type = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    chat_details = relationship("ChatDetail", back_populates="generator")

class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="chat_histories")
    chat_details = relationship("ChatDetail", back_populates="chat_history", cascade="all, delete-orphan")

class ChatDetail(Base):
    __tablename__ = "chat_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_history_id = Column(UUID(as_uuid=True), ForeignKey("chat_histories.id"), nullable=False, index=True)
    generator_id = Column(UUID(as_uuid=True), ForeignKey("generators.id"), nullable=False, index=True)
    input_type = Column(String, nullable=False, default="text")
    text_prompt = Column(Text, nullable=True)
    input_file_path = Column(String(1024), nullable=True)
    output_type = Column(String, nullable=False, default="audio")
    output_content = Column(Text, nullable=True)
    output_file_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat_history = relationship("ChatHistory", back_populates="chat_details")
    generator = relationship("Generator", back_populates="chat_details")