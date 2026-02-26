-- Migration: 0009_add_client_po_id_to_vendor_order.sql
-- Purpose: Link vendor orders to specific client purchase orders
-- Description: Adds client_po_id column to vendor_order table

SET search_path TO "Finances";

-- Add client_po_id to vendor_order table
ALTER TABLE "vendor_order" 
ADD COLUMN IF NOT EXISTS client_po_id INTEGER;

-- Add foreign key constraint
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_vendor_order_client_po') THEN
        ALTER TABLE "vendor_order" 
        ADD CONSTRAINT fk_vendor_order_client_po 
        FOREIGN KEY (client_po_id) REFERENCES "client_po"(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_vendor_order_client_po_id ON "vendor_order"(client_po_id);

COMMIT;
