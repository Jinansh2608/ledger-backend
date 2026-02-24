-- Migration: 0005_add_storeid_and_location.sql
-- Purpose: Add store_id to client_po for aggregation and location tracking
-- Description: Adds store_id to client_po to group multiple POs from same store
--              Adds location fields to project table for geographic tracking

-- Add store_id column to client_po for grouping multiple POs from same store
ALTER TABLE "Finances"."client_po"
ADD COLUMN IF NOT EXISTS store_id VARCHAR(100);

-- Create index on store_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_client_po_store_id ON "Finances"."client_po"(store_id);

-- Create index on (client_id, store_id) for aggregation queries
CREATE INDEX IF NOT EXISTS idx_client_po_client_store ON "Finances"."client_po"(client_id, store_id);

-- Add location fields to project table
ALTER TABLE "Finances"."project"
ADD COLUMN IF NOT EXISTS location VARCHAR(255),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(100),
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS latitude NUMERIC(10, 7),
ADD COLUMN IF NOT EXISTS longitude NUMERIC(10, 7);

-- Create index on location for geographic queries
CREATE INDEX IF NOT EXISTS idx_project_location ON "Finances"."project"(city, state);
