"""
Database models for the AI Support System.
Tables: users, tickets, ticket_logs, ai_responses, agents
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    Boolean, ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AI_RESOLVED = "ai_resolved"
    HUMAN_RESOLVED = "human_resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, enum.Enum):
    BILLING_INQUIRY = "billing_inquiry"
    ACCOUNT_INFO = "account_info"
    PASSWORD_RESET = "password_reset"
    ORDER_STATUS = "order_status"
    TECHNICAL_ISSUE = "technical_issue"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"
    FAQ = "faq"
    OTHER = "other"


class SentimentLabel(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    URGENT = "urgent"


# ──────────────────────────────────────────────
# User
# ──────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tickets = relationship("Ticket", back_populates="customer", foreign_keys="Ticket.customer_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_agent", foreign_keys="Ticket.assigned_agent_id")


# ──────────────────────────────────────────────
# Ticket
# ──────────────────────────────────────────────
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Content
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # AI Classification
    category = Column(SAEnum(TicketCategory), default=TicketCategory.OTHER)
    priority = Column(SAEnum(TicketPriority), default=TicketPriority.MEDIUM)
    sentiment = Column(SAEnum(SentimentLabel), default=SentimentLabel.NEUTRAL)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.OPEN)

    # AI Metadata
    ai_confidence_score = Column(Float, default=0.0)
    ai_processed = Column(Boolean, default=False)
    auto_resolved = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    suggested_tags = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("User", back_populates="tickets", foreign_keys=[customer_id])
    assigned_agent = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_agent_id])
    ai_responses = relationship("AIResponse", back_populates="ticket", cascade="all, delete-orphan")
    logs = relationship("TicketLog", back_populates="ticket", cascade="all, delete-orphan")


# ──────────────────────────────────────────────
# AI Response
# ──────────────────────────────────────────────
class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)

    # Pipeline Step
    pipeline_step = Column(String(100), nullable=False)  # classify | analyze | generate | escalate
    prompt_used = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)
    parsed_response = Column(JSON, nullable=True)

    # Metrics
    confidence_score = Column(Float, default=0.0)
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="ai_responses")


# ──────────────────────────────────────────────
# Ticket Log (audit trail)
# ──────────────────────────────────────────────
class TicketLog(Base):
    __tablename__ = "ticket_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    actor = Column(String(100), nullable=False)  # "system", "ai", "agent", or user email
    action = Column(String(255), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", back_populates="logs")
