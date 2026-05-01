# AI Pipeline Documentation

## Overview

Every ticket submission triggers a synchronous 3-step Gemini AI pipeline before the HTTP response is returned to the customer. The full trace is stored in the database for auditability.

---

## Step 1 — Classification

**Service**: `gemini_service.classify_ticket(subject, description)`  
**Model**: Gemini 2.5 Flash  
**Output stored in**: `tickets` table + `ai_responses` (step: `classify`)

### What it determines
| Field | Values |
|---|---|
| `category` | billing_inquiry, account_info, password_reset, order_status, technical_issue, complaint, feature_request, faq, other |
| `priority` | low, medium, high, critical |
| `sentiment` | positive, neutral, negative, frustrated, urgent |
| `confidence_score` | 0.0 – 1.0 |
| `requires_human` | true / false |
| `escalation_reason` | string or null |
| `summary` | 1–2 sentence issue summary |
| `tags` | list of keyword tags |

### Priority rules (prompt-encoded)
- **critical** — system down, data loss, security breach, legal threats  
- **high** — payments failing, account locked, major feature broken  
- **medium** — partial issues, billing questions  
- **low** — general inquiries, feature requests, feedback  

---

## Step 2 — Response Generation

**Service**: `gemini_service.generate_response(...)`  
**Output stored in**: `ai_responses` (step: `generate_response`)  
**Also stored in**: `ticket_logs` details (used by the frontend to display the AI reply)

The tone of the response adapts to detected sentiment:

| Sentiment | Tone |
|---|---|
| frustrated | very empathetic, apologetic, solution-focused |
| urgent | immediate, action-oriented, reassuring |
| negative | empathetic and professional |
| positive | warm and helpful |
| neutral | professional and informative |

### Output fields
- `response_text` — the customer-facing reply (≤200 words)
- `confidence_score` — how completely this resolves the issue
- `resolution_steps` — ordered action list
- `follow_up_required` — bool

---

## Step 3 — Escalation Decision

**Service**: `gemini_service.decide_escalation(classification, response_confidence)`  
**Output stored in**: `ai_responses` (step: `escalation_decision`)

### Auto-resolve conditions (ALL must be true)
1. `requires_human == false` from classifier
2. `category` is in `AUTO_RESOLVE_CATEGORIES` config list
3. Classification `confidence_score >= AI_CONFIDENCE_THRESHOLD` (default 0.75)
4. Response `confidence_score >= AI_CONFIDENCE_THRESHOLD` (default 0.75)

If any condition fails → ticket is **escalated** with a reason stored in `tickets.escalation_reason`.

---

## Retry Logic

All Gemini API calls use `tenacity` with exponential backoff:
- Max attempts: 3
- Wait: 2s → 4s → 8s (exponential, max 10s)

If all retries fail, the step returns a safe fallback and sets `requires_human = true`.

---

## Data Flow Diagram

```
POST /api/tickets/
        │
        ▼
 pipeline_service.process_ticket_pipeline()
        │
        ├─► Create Ticket row (status=open)
        │         │ log: "Ticket created"
        │
        ├─► Step 1: gemini_service.classify_ticket()
        │         │ saves: AIResponse(pipeline_step="classify")
        │         │ updates: ticket.category, priority, sentiment, confidence
        │         │ log: "Ticket classified"
        │
        ├─► Step 2: gemini_service.generate_response()
        │         │ saves: AIResponse(pipeline_step="generate_response")
        │         │ updates: ticket.first_response_at
        │         │ log: "Response generated"
        │
        ├─► Step 3: gemini_service.decide_escalation()
        │         │ saves: AIResponse(pipeline_step="escalation_decision")
        │         │
        │         ├─ AUTO-RESOLVE → ticket.status = "ai_resolved"
        │         │                  ticket.auto_resolved = true
        │         │                  ticket.resolved_at = now()
        │         │                  log: "Auto-resolved by AI" + response_text
        │         │
        │         └─ ESCALATE    → ticket.status = "escalated"
        │                          ticket.escalation_reason = "..."
        │                          log: "Escalated for manual review" + draft_response
        │
        └─► Return full Ticket object (with logs + ai_responses eager-loaded)
```

---

## Confidence Threshold Tuning

Edit `backend/.env`:
```
AI_CONFIDENCE_THRESHOLD=0.75       # raise to escalate more, lower to auto-resolve more
AUTO_RESOLVE_CATEGORIES=["billing_inquiry","account_info","faq","order_status","password_reset"]
```
