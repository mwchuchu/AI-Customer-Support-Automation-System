from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import Ticket, User, UserRole, TicketStatus
from app.schemas.schemas import (
    TicketCreate, TicketOut, TicketListOut, TicketUpdate, PaginatedTickets
)
from app.services.pipeline_service import process_ticket_pipeline
from app.core.security import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=TicketOut, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a new support ticket — triggers the full AI pipeline."""
    logger.info("New ticket submitted", user_id=current_user.id, subject=ticket_data.subject[:40])
    ticket = await process_ticket_pipeline(db, ticket_data, current_user.id)
    ticket_id = ticket.id

    result = await db.execute(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            selectinload(Ticket.customer),
            selectinload(Ticket.assigned_agent),
            selectinload(Ticket.ai_responses),
            selectinload(Ticket.logs),
        )
    )
    ticket = result.scalar_one()
    return TicketOut.model_validate(ticket)


@router.get("/", response_model=PaginatedTickets)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tickets. Customers see their own; agents/admins see all."""
    query = select(Ticket).options(selectinload(Ticket.customer))

    if current_user.role == UserRole.CUSTOMER:
        query = query.where(Ticket.customer_id == current_user.id)
    if status:
        query = query.where(Ticket.status == status)
    if category:
        query = query.where(Ticket.category == category)
    if priority:
        query = query.where(Ticket.priority == priority)

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Paginate
    query = query.order_by(desc(Ticket.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tickets = result.scalars().all()

    return PaginatedTickets(total=total, page=page, page_size=page_size, tickets=tickets)


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            selectinload(Ticket.customer),
            selectinload(Ticket.assigned_agent),
            selectinload(Ticket.ai_responses),
            selectinload(Ticket.logs),
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == UserRole.CUSTOMER and ticket.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.AGENT, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only agents/admins can update tickets")

    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.customer), selectinload(Ticket.assigned_agent),
                 selectinload(Ticket.ai_responses), selectinload(Ticket.logs))
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if update_data.status:
        ticket.status = update_data.status
    if update_data.priority:
        ticket.priority = update_data.priority
    if update_data.assigned_agent_id:
        ticket.assigned_agent_id = update_data.assigned_agent_id

    await db.flush()
    await db.refresh(ticket)
    logger.info("Ticket updated", ticket_id=ticket_id, updated_by=current_user.email)
    return ticket
