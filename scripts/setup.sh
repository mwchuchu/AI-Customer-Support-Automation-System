#!/bin/bash
# setup.sh — local dev setup (no Docker)
set -e

echo "🚀 AI Support System — Local Setup"
echo "──────────────────────────────────"

# ── Backend ────────────────────────────────────
echo ""
echo "📦 Setting up Python backend..."
cd backend

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Created .env from .env.example — add your GEMINI_API_KEY!"
fi

python3 -m venv venv
source venv/bin/activate
pip install --quiet -r requirements.txt
echo "✅ Backend dependencies installed"

# ── Frontend ───────────────────────────────────
echo ""
echo "📦 Setting up React frontend..."
cd ../frontend
npm install --silent
echo "✅ Frontend dependencies installed"

# ── Instructions ───────────────────────────────
echo ""
echo "──────────────────────────────────"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env — add your GEMINI_API_KEY"
echo "  2. Start PostgreSQL:  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=ai_support_db postgres:16-alpine"
echo "  3. Start backend:     cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  4. Seed demo data:    cd backend && python ../scripts/seed.py"
echo "  5. Start frontend:    cd frontend && npm run dev"
echo ""
echo "  API docs: http://localhost:8000/api/docs"
echo "  App:      http://localhost:5173"
