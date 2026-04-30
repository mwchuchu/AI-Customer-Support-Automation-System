-- AI Support System — Database Initialization
-- Runs automatically on first postgres container start

-- Ensure DB exists (postgres container creates it via env var, this is a safety net)
SELECT 'CREATE DATABASE ai_support_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_support_db');

-- Connect to the target DB
\c ai_support_db;

-- Enable UUID extension (optional but useful for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fast text search (optional)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- SQLAlchemy will create all tables on startup via Base.metadata.create_all
-- This script just ensures the DB and extensions are ready.

COMMENT ON DATABASE ai_support_db IS 'AI Customer Support Automation System';
