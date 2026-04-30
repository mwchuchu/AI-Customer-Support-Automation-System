from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from app.models.models import (
    UserRole, TicketStatus, TicketPriority, TicketCategory, SentimentLabel
)


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ──────────────────────────────────────────────
# Ticket Schemas
# ──────────────────────────────────────────────
class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_agent_id: Optional[int] = None


class AIResponseOut(BaseModel):
    id: int
    pipeline_step: str
    confidence_score: float
    tokens_used: int
    latency_ms: int
    model_used: Optional[str]
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketLogOut(BaseModel):
    id: int
    actor: str
    action: str
    details: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: int
    ticket_number: str
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    sentiment: SentimentLabel
    status: TicketStatus
    ai_confidence_score: float
    ai_processed: bool
    auto_resolved: bool
    escalation_reason: Optional[str]
    ai_summary: Optional[str]
    suggested_tags: Optional[List[str]]
    customer: UserOut
    assigned_agent: Optional[UserOut]
    ai_responses: List[AIResponseOut] = []
    logs: List[TicketLogOut] = []
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    first_response_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketListOut(BaseModel):
    id: int
    ticket_number: str
    subject: str
    category: TicketCategory
    priority: TicketPriority
    sentiment: SentimentLabel
    status: TicketStatus
    ai_processed: bool
    auto_resolved: bool
    ai_confidence_score: float
    customer: UserOut
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedTickets(BaseModel):
    total: int
    page: int
    page_size: int
    tickets: List[TicketListOut]


# ──────────────────────────────────────────────
# Analytics Schemas
# ──────────────────────────────────────────────
class AnalyticsSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    ai_resolved: int
    human_resolved: int
    escalated: int
    avg_confidence: float
    auto_resolution_rate: float
    category_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]
    daily_volume: List[Dict[str, Any]]
