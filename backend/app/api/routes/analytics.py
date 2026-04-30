from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.db.database import get_db
from app.models.models import Ticket, TicketStatus, TicketCategory, TicketPriority, SentimentLabel
from app.schemas.schemas import AnalyticsSummary
from app.core.security import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Total counts
    total = (await db.execute(select(func.count(Ticket.id)))).scalar_one()
    open_count = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.OPEN))).scalar_one()
    ai_resolved = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.AI_RESOLVED))).scalar_one()
    human_resolved = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.HUMAN_RESOLVED))).scalar_one()
    escalated = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.ESCALATED))).scalar_one()
    avg_conf = (await db.execute(select(func.avg(Ticket.ai_confidence_score)))).scalar_one() or 0.0

    # Category breakdown
    cat_rows = (await db.execute(
        select(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category)
    )).all()
    category_breakdown = {str(r[0]).split(".")[-1]: r[1] for r in cat_rows}

    # Priority breakdown
    prio_rows = (await db.execute(
        select(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority)
    )).all()
    priority_breakdown = {str(r[0]).split(".")[-1]: r[1] for r in prio_rows}

    # Sentiment breakdown
    sent_rows = (await db.execute(
        select(Ticket.sentiment, func.count(Ticket.id)).group_by(Ticket.sentiment)
    )).all()
    sentiment_breakdown = {str(r[0]).split(".")[-1]: r[1] for r in sent_rows}

    # Daily volume (last 7 days)
    daily_q = text("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM tickets
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    daily_rows = (await db.execute(daily_q)).all()
    daily_volume = [{"date": str(r[0]), "count": r[1]} for r in daily_rows]

    auto_rate = round((ai_resolved / total * 100), 1) if total > 0 else 0.0

    return AnalyticsSummary(
        total_tickets=total,
        open_tickets=open_count,
        ai_resolved=ai_resolved,
        human_resolved=human_resolved,
        escalated=escalated,
        avg_confidence=round(avg_conf, 3),
        auto_resolution_rate=auto_rate,
        category_breakdown=category_breakdown,
        priority_breakdown=priority_breakdown,
        sentiment_breakdown=sentiment_breakdown,
        daily_volume=daily_volume,
    )
