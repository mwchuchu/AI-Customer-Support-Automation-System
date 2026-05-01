"""
AI Pipeline Orchestrator
Coordinates the full ticket processing pipeline:
  1. Receive ticket
  2. Classify (category, priority, sentiment)
  3. Generate response
  4. Decide: auto-resolve or escalate to human
  5. Persist everything + audit log
"""
import random
import string
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Ticket, AIResponse, TicketLog, TicketStatus, User
from app.schemas.schemas import TicketCreate
from app.services.gemini_service import gemini_service
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_ticket_number() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TKT-{suffix}"


async def log_action(db: AsyncSession, ticket_id: int, actor: str, action: str, details: dict = None):
    log = TicketLog(ticket_id=ticket_id, actor=actor, action=action, details=details or {})
    db.add(log)


async def save_ai_response(db: AsyncSession, ticket_id: int, step: str, data: dict, success: bool = True, error: str = None):
    ai_resp = AIResponse(
        ticket_id=ticket_id,
        pipeline_step=step,
        parsed_response=data,
        confidence_score=data.get("confidence_score", 0.0),
        tokens_used=data.get("tokens_used", 0),
        latency_ms=data.get("latency_ms", 0),
        model_used=data.get("model_used", "gemini-1.5-flash"),
        success=success,
        error_message=error,
    )
    db.add(ai_resp)


async def process_ticket_pipeline(
    db: AsyncSession,
    ticket_data: TicketCreate,
    customer_id: int,
) -> Ticket:
    """
    Full end-to-end AI pipeline for a new support ticket.
    """
    logger.info("🎫 Pipeline started", subject=ticket_data.subject[:50])

    # ── Create ticket in DB ──────────────────────────────────────────
    ticket = Ticket(
        ticket_number=generate_ticket_number(),
        customer_id=customer_id,
        subject=ticket_data.subject,
        description=ticket_data.description,
    )
    db.add(ticket)
    await db.flush()  # get ticket.id

    await log_action(db, ticket.id, "system", "Ticket created", {"ticket_number": ticket.ticket_number})

    # ── Step 1: Classify ────────────────────────────────────────────
    logger.info("Step 1: Classifying ticket", ticket_id=ticket.id)
    classification = await gemini_service.classify_ticket(
        ticket_data.subject, ticket_data.description
    )
    await save_ai_response(db, ticket.id, "classify", classification)

    ticket.category = classification.get("category", "other")
    ticket.priority = classification.get("priority", "medium")
    ticket.sentiment = classification.get("sentiment", "neutral")
    ticket.ai_confidence_score = classification.get("confidence_score", 0.0)
    ticket.ai_summary = classification.get("summary", "")
    ticket.suggested_tags = classification.get("tags", [])

    await log_action(db, ticket.id, "ai", "Ticket classified", {
        "category": ticket.category,
        "priority": ticket.priority,
        "sentiment": ticket.sentiment,
        "confidence": ticket.ai_confidence_score,
    })

    # ── Step 2: Generate Response ────────────────────────────────────
    logger.info("Step 2: Generating response", ticket_id=ticket.id)
    response_data = await gemini_service.generate_response(
        subject=ticket_data.subject,
        description=ticket_data.description,
        category=str(ticket.category),
        sentiment=str(ticket.sentiment),
        priority=str(ticket.priority),
    )
    await save_ai_response(db, ticket.id, "generate_response", response_data)

    response_confidence = response_data.get("confidence_score", 0.0)
    response_text = response_data.get("response_text", "")

    ticket.first_response_at = datetime.utcnow()
    await log_action(db, ticket.id, "ai", "Response generated", {
        "confidence": response_confidence,
        "length": len(response_text),
    })

    # ── Step 3: Escalation Decision ──────────────────────────────────
    logger.info("Step 3: Escalation decision", ticket_id=ticket.id)
    decision = await gemini_service.decide_escalation(classification, response_confidence)
    await save_ai_response(db, ticket.id, "escalation_decision", decision)

    ticket.ai_processed = True

    if decision.get("auto_resolve"):
        ticket.status = TicketStatus.AI_RESOLVED
        ticket.auto_resolved = True
        ticket.resolved_at = datetime.utcnow()
        await log_action(db, ticket.id, "ai", "Auto-resolved by AI", {
            "response_text": response_text,
            "resolution_steps": response_data.get("resolution_steps", []),
        })
        logger.info("✅ Ticket auto-resolved", ticket_id=ticket.id)
    else:
        ticket.status = TicketStatus.ESCALATED
        ticket.escalation_reason = decision.get("reason", "Requires manual review")
        await log_action(db, ticket.id, "ai", "Escalated for manual review", {
            "reason": ticket.escalation_reason,
            "draft_response": response_text,
        })
        logger.info("⚠️  Ticket escalated", ticket_id=ticket.id, reason=ticket.escalation_reason)

    await db.flush()
    logger.info("🏁 Pipeline complete", ticket_id=ticket.id, status=ticket.status)
    return ticket
