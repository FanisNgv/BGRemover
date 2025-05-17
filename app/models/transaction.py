from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base

class TransactionType(str, enum.Enum):
    CREDIT_ADD = "credit_add"
    CREDIT_USE = "credit_use"
    CREDIT_REFUND = "credit_refund"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions") 