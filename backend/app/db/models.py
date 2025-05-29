from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

# ==================== User ==================== 

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)  
    avatar = Column(String(2048), nullable=True)
    provider = Column(String, nullable=False, default="google")
    role = Column(String, nullable=False, default="free")
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    billing_cycle = Column(String, default="monthly")
    notification_sent = Column(Boolean, default=False)

# ==================== Khác ==================== 

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


class Request(Base):
    __tablename__ = "request"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id = Column(UUID(as_uuid=True), ForeignKey("generator.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    input_type = Column(String, ForeignKey("generator.input_type"), nullable=False, index=True)
    text_prompt = Column(String, nullable=True)
    input_file_name = Column(String, nullable=True)


    
