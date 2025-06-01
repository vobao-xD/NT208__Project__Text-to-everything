from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy.orm import relationship

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

    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String, default="monthly")

class Generator(Base):
    __tablename__ = "generator"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    input_type = Column(String, nullable=False, index=True)
    output_type = Column(String, nullable=False, index=True)
    chat_details = relationship("ChatDetail", back_populates="generator")

class Request(Base):
    __tablename__ = "request"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(UUID(as_uuid=True), ForeignKey("generator.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    input_type = Column(String, ForeignKey("generator.input_type"), nullable=False, index=True)
    text_prompt = Column(String, nullable=True)
    input_file_name = Column(String, nullable=True)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="chats")
    details = relationship("ChatDetail", backref="chat_history", cascade="all, delete-orphan")

class ChatDetail(Base):
    __tablename__ = 'chat_detail'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_history_id = Column(UUID(as_uuid=True), ForeignKey('chat_history.id'), nullable=False, index=True)
    generator_id = Column(UUID(as_uuid=True), ForeignKey('generator.id'), nullable=False, index=True)
    input_type = Column(String, nullable=False, index=True)
    text_prompt = Column(String, nullable=True)
    input_file_name = Column(String, nullable=True)
    output_type = Column(String, nullable=False)
    output_content = Column(Text, nullable=True)
    output_file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    generator = relationship("Generator", back_populates="chat_details")