# API Reference

Base URL: `http://localhost:8000/api`  
Interactive docs: `http://localhost:8000/api/docs`

All protected endpoints require: `Authorization: Bearer <token>`

---

## Auth

### POST /auth/register
Create a new user account.

**Body**
```json
{ "email": "user@example.com", "full_name": "Jane Smith", "password": "secret123", "role": "customer" }
```
**Roles**: `customer` | `admin`

**Response** `201`
```json
{ "access_token": "...", "token_type": "bearer", "user": { "id": 1, "email": "...", "role": "customer", ... } }
```

---

### POST /auth/login
```json
{ "email": "user@example.com", "password": "secret123" }
```
**Response** `200` — same shape as register.

---

### GET /auth/me
Returns current authenticated user. Requires token.

---

## Tickets

### POST /tickets/
Submit a new ticket. Triggers the full AI pipeline synchronously.

**Body**
```json
{ "subject": "My invoice is wrong", "description": "I was charged twice for my March subscription..." }
```

**Response** `201` — Full `TicketOut` object including:
- Classification results (`category`, `priority`, `sentiment`, `ai_confidence_score`)
- AI pipeline trace (`ai_responses[]`)
- Audit log (`logs[]`) containing the AI-generated response text inside `details`

---

### GET /tickets/
List tickets. Customers see only their own; admins see all.

**Query params**
| Param | Values |
|---|---|
| `page` | integer (default 1) |
| `page_size` | 1–100 (default 20) |
| `status` | open, in_progress, ai_resolved, escalated, human_resolved, closed |
| `priority` | low, medium, high, critical |
| `category` | billing_inquiry, technical_issue, complaint, faq, other, ... |

**Response**
```json
{ "total": 142, "page": 1, "page_size": 20, "tickets": [ ... ] }
```

---

### GET /tickets/{id}
Full ticket detail with eager-loaded `ai_responses` and `logs`.

---

### PATCH /tickets/{id}
Admins only. Update status or priority.

**Body** (all fields optional)
```json
{ "status": "human_resolved", "priority": "high" }
```

---

## Analytics

### GET /analytics/summary
Admins only.

**Response**
```json
{
  "total_tickets": 250,
  "open_tickets": 12,
  "ai_resolved": 180,
  "human_resolved": 40,
  "escalated": 18,
  "avg_confidence": 0.84,
  "auto_resolution_rate": 72.0,
  "category_breakdown": { "billing_inquiry": 60, "technical_issue": 45, ... },
  "priority_breakdown": { "low": 80, "medium": 120, "high": 40, "critical": 10 },
  "sentiment_breakdown": { "neutral": 100, "frustrated": 50, ... },
  "daily_volume": [ { "date": "2024-11-01", "count": 35 }, ... ]
}
```

---

## Health

### GET /health
```json
{ "status": "healthy", "app": "AI Support System", "version": "1.0.0" }
```
