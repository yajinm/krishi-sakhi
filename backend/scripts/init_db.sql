-- Initialize PostgreSQL database with required extensions
-- This script is run when the database container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('farmer', 'staff', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE activity_kind AS ENUM (
        'sowing', 'irrigation', 'fertilizer', 'pesticide', 
        'harvest', 'plowing', 'weeding', 'pruning', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE advisory_severity AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'failed', 'delivered');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE consent_kind AS ENUM (
        'data_processing', 'marketing', 'analytics', 'location', 
        'notifications', 'voice_recording', 'data_sharing'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
-- These will be created after tables are created by Alembic

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE krishi_sakhi TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

-- Set timezone
SET timezone = 'Asia/Kolkata';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully with extensions: uuid-ossp, pg_trgm, postgis, vector';
END $$;
