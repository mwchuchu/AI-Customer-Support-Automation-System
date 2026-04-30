# 🤖 AI Customer Support Automation System

An end-to-end intelligent customer support platform powered by **Gemini AI**, **FastAPI**, **PostgreSQL**, and **React**.

When a customer submits a ticket, a 3-step AI pipeline instantly classifies it, generates a professional response, and either auto-resolves it or escalates it to a human agent — all within seconds.

---

## 🏗️ Architecture

```
Customer Submits Ticket
        │
        ▼
┌──────────────────────────────────────────────────┐
│              AI PIPELINE (Gemini 1.5 Flash)       │
│                                                    │
│  Step 1: CLASSIFY                                  │
│    → Category, Priority, Sentiment, Confidence     │
│                                                    │
│  Step 2: GENERATE RESPONSE                         │
│    → Empathetic, contextual customer reply         │
│                                                    │
│  Step 3: ESCALATION DECISION                       │
│    → Auto-resolve OR route to human agent          │
└──────────────────────────────────────────────────┘
        │
        ├── Auto-resolved → Customer gets instant AI response
        └── Escalated     → Agent dashboard with full context
```

---

## 📁 Folder Structure

```
ai-support-system/
├── backend/                        # FastAPI application
│   ├── main.py                     # App entrypoint
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini                 # DB migration config
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial.py      # Initial schema migration
│   └── app/
│       ├── api/routes/
│       │   ├── auth.py             # Register, login, /me
│       │   ├── tickets.py          # Full ticket CRUD + AI pipeline trigger
│       │   ├── analytics.py        # Dashboard analytics
│       │   └── agents.py           # List agents for assignment
│       ├── core/
│       │   ├── config.py           # Pydantic settings (reads .env)
│       │   ├── logging.py          # Structlog structured logging
│       │   └── security.py         # JWT auth + bcrypt
│       ├── db/
│       │   └── database.py         # Async SQLAlchemy engine + session
│       ├── models/
│       │   └── models.py           # User, Ticket, AIResponse, TicketLog
│       ├── schemas/
│       │   └── schemas.py          # Pydantic request/response schemas
│       └── services/
│           ├── gemini_service.py   # Gemini API calls (classify, generate, decide)
│           ├── pipeline_service.py # AI pipeline orchestrator
│           └── user_service.py     # User CRUD helpers
│
├── frontend/                       # React + Vite application
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                 # Router
│       ├── store/
│       │   └── authStore.js        # Zustand auth state (persisted)
│       ├── services/
│       │   └── api.js              # Axios instance + all API calls
│       ├── components/common/
│       │   ├── Layout.jsx          # Sidebar + main shell
│       │   └── Badge.jsx           # Status/priority/category badges
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── RegisterPage.jsx
│       │   ├── DashboardPage.jsx   # Stats overview + recent tickets
│       │   ├── TicketsPage.jsx     # Paginated ticket list + filters
│       │   ├── NewTicketPage.jsx   # Submit form + AI result display
│       │   ├── TicketDetailPage.jsx# Full ticket + AI pipeline trace
│       │   └── AnalyticsPage.jsx   # Charts (category, priority, sentiment, volume)
│       └── styles/
│           └── globals.css         # Design system CSS variables
│
├── scripts/
│   ├── init_db.sql                 # PostgreSQL init (extensions)
│   ├── seed.py                     # Demo users seeder
│   └── setup.sh                    # Local dev setup script
│
├── docker-compose.yml              # Full stack (postgres + backend + frontend)
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Option A — Docker (recommended)

```bash
# 1. Clone and enter project
cd ai-support-system

# 2. Copy and configure env
cp backend/.env.example backend/.env
# Edit backend/.env — set your GEMINI_API_KEY

# 3. Start everything
docker-compose up --build

# 4. Seed demo users (in a new terminal)
docker exec ai_support_backend python ../scripts/seed.py
```

- **App**: http://localhost:5173  
- **API docs**: http://localhost:8000/api/docs

---

### Option B — Local Dev

```bash
# Run the setup script
bash scripts/setup.sh

# Start Postgres
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ai_support_db \
  postgres:16-alpine

# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 — Seed data
python scripts/seed.py

# Terminal 3 — Frontend
cd frontend && npm run dev
```

---

## 🔑 Demo Credentials (after seeding)

| Role     | Email               | Password      |
|----------|---------------------|---------------|
| Admin    | admin@demo.com      | admin123      |
| Agent    | agent@demo.com      | agent123      |
| Customer | customer@demo.com   | customer123   |

---

## 🧠 AI Pipeline Details

### Step 1 — Classification
Gemini classifies the ticket into:
- **Category**: billing_inquiry, technical_issue, complaint, faq, etc.
- **Priority**: low / medium / high / critical
- **Sentiment**: positive / neutral / negative / frustrated / urgent
- **Confidence score**: 0.0–1.0

### Step 2 — Response Generation
Gemini writes an empathetic, professional reply tuned to the detected sentiment.

### Step 3 — Escalation Decision
Auto-resolves if:
- Category is in the auto-resolvable list (billing_inquiry, faq, account_info, etc.)
- Both classification confidence AND response confidence ≥ 0.75
- No human required flag from classifier

Otherwise: escalated to the agent queue with a reason.

---

## ⚙️ Environment Variables

| Variable                  | Description                              |
|---------------------------|------------------------------------------|
| `DATABASE_URL`            | Async PostgreSQL URL (asyncpg)           |
| `DATABASE_URL_SYNC`       | Sync PostgreSQL URL (for alembic)        |
| `GEMINI_API_KEY`          | Google AI Studio API key (free tier)     |
| `SECRET_KEY`              | JWT signing secret                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL (default 1440 = 24h)      |
| `AI_CONFIDENCE_THRESHOLD` | Minimum confidence for auto-resolve (0.75)|
| `DEBUG`                   | Enable hot-reload and verbose logs       |

---

## 🛠️ Tech Stack

| Layer     | Technology                            |
|-----------|---------------------------------------|
| Frontend  | React 18, Vite, Zustand, Recharts     |
| Backend   | FastAPI, SQLAlchemy (async), Alembic  |
| Database  | PostgreSQL 16                         |
| AI        | Google Gemini 1.5 Flash (free tier)   |
| Auth      | JWT (python-jose) + bcrypt            |
| Logging   | structlog (JSON in prod, pretty in dev)|
| Container | Docker + nginx                        |

---

## 📊 API Endpoints

| Method | Endpoint                | Description                    |
|--------|-------------------------|--------------------------------|
| POST   | `/api/auth/register`    | Create account                 |
| POST   | `/api/auth/login`       | Login → JWT token              |
| GET    | `/api/auth/me`          | Current user                   |
| POST   | `/api/tickets/`         | Submit ticket (triggers AI)    |
| GET    | `/api/tickets/`         | List tickets (paginated)       |
| GET    | `/api/tickets/{id}`     | Ticket detail + AI trace       |
| PATCH  | `/api/tickets/{id}`     | Update status/assignee (agent) |
| GET    | `/api/analytics/summary`| Dashboard stats                |
| GET    | `/api/agents/`          | List agents                    |
| GET    | `/api/health`           | Health check                   |

Full interactive docs at `/api/docs` (Swagger UI).
