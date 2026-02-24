-- Migration: 0004_add_billing_po.sql
-- Purpose: Create billing PO tables for final billing workflow
-- Description: Adds billing_po and billing_po_line_items tables
--              to track final billed values against original POs

-- Create billing_po table
CREATE TABLE IF NOT EXISTS "Finances"."billing_po" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_po_id INT NOT NULL,
    project_id INT NOT NULL,
    po_number TEXT NOT NULL,
    billed_value NUMERIC(12, 2) NOT NULL DEFAULT 0,
    billed_gst NUMERIC(12, 2) NOT NULL DEFAULT 0,
    billed_total NUMERIC(12, 2) NOT NULL DEFAULT 0,
    billing_notes TEXT,
    status TEXT NOT NULL DEFAULT 'FINAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_billing_po_client_po FOREIGN KEY (client_po_id) REFERENCES "Finances"."client_po"(id) ON DELETE RESTRICT,
    CONSTRAINT fk_billing_po_project FOREIGN KEY (project_id) REFERENCES "Finances"."project"(id) ON DELETE RESTRICT
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_billing_po_project_id ON "Finances"."billing_po"(project_id);
CREATE INDEX IF NOT EXISTS idx_billing_po_client_po_id ON "Finances"."billing_po"(client_po_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_billing_po_unique_per_project ON "Finances"."billing_po"(project_id) 
    WHERE status = 'FINAL';

-- Create billing_po_line_items table
CREATE TABLE IF NOT EXISTS "Finances"."billing_po_line_item" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    billing_po_id UUID NOT NULL,
    description TEXT NOT NULL,
    qty NUMERIC(10, 2) NOT NULL,
    rate NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_billing_line_item_billing_po FOREIGN KEY (billing_po_id) REFERENCES "Finances"."billing_po"(id) ON DELETE CASCADE
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_billing_po_line_item_billing_po_id ON "Finances"."billing_po_line_item"(billing_po_id);

-- Add columns to vendor_order table to track billing status
ALTER TABLE "Finances"."vendor_order"
ADD COLUMN IF NOT EXISTS final_po_value NUMERIC(12, 2),
ADD COLUMN IF NOT EXISTS billing_status TEXT DEFAULT 'not_initiated',
ADD COLUMN IF NOT EXISTS billing_notes TEXT;

COMMIT;
