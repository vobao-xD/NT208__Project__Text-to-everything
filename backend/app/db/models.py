from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    email = Column(String(255), primary_key=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    avatar = Column(String(2048), nullable=True)
    provider = Column(String(50), nullable=False, default="unknown")
    role = Column(String(50), nullable=False, default="free")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String(50), default="monthly", nullable=False)
    notification_sent = Column(Boolean, default=False, nullable=False)

    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    plan = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String(50), default="monthly", nullable=False)

    user = relationship("User", back_populates="transactions")

class Generator(Base):
    __tablename__ = "generators"
    name = Column(String(100), primary_key=True, index=True, nullable=False)
    input_type = Column(String(50), nullable=False)
    output_type = Column(String(50), nullable=False)
    chat_details = relationship("ChatDetail", back_populates="generator", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    user = relationship("User", back_populates="chat_histories")
    chat_details = relationship("ChatDetail", back_populates="chat_history", cascade="all, delete-orphan")

class ChatDetail(Base):
    __tablename__ = "chat_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_history_id = Column(UUID(as_uuid=True), ForeignKey("chat_histories.id", ondelete="CASCADE"), nullable=False, index=True)
    generator_name = Column(String(100), ForeignKey("generators.name", ondelete="RESTRICT"), nullable=False, index=True)
    input_type = Column(String(50), nullable=False)
    text_prompt = Column(Text, nullable=True)
    input_file_path = Column(String(1024), nullable=True)
    output_type = Column(String(50), nullable=False)
    output_content = Column(Text, nullable=True)
    output_file_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    chat_history = relationship("ChatHistory", back_populates="chat_details")
    generator = relationship("Generator", back_populates="chat_details")