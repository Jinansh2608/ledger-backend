-- Migration to add Quotation tables and update Vendor Master
-- Removing GST related columns as requested

SET search_path TO "Finances";

-- 1. Create Quotation Table
CREATE TABLE IF NOT EXISTS "quotation" (
    "id" SERIAL PRIMARY KEY,
    "store_id" VARCHAR(50) NOT NULL,
    "store_location" TEXT NOT NULL,
    "full_address" TEXT NOT NULL,
    "company_name" TEXT NOT NULL,
    "total_area" VARCHAR(50) NOT NULL,
    "total_amount" NUMERIC DEFAULT 0,
    "status" VARCHAR(20) DEFAULT 'saved',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Quotation Line Items Table
CREATE TABLE IF NOT EXISTS "quotation_line_item" (
    "id" SERIAL PRIMARY KEY,
    "quotation_id" INTEGER REFERENCES "quotation"(id) ON DELETE CASCADE,
    "name" TEXT NOT NULL,
    "hsn_sac_code" VARCHAR(50),
    "type_of_boq" VARCHAR(50),
    "quantity" NUMERIC DEFAULT 1,
    "units" VARCHAR(20),
    "price" NUMERIC DEFAULT 0,
    "total" NUMERIC DEFAULT 0,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Update Vendor Table
-- Add master_type and rate_configuration (JSONB for the editable grid data)
ALTER TABLE "vendor" ADD COLUMN IF NOT EXISTS "master_type" VARCHAR(50);
ALTER TABLE "vendor" ADD COLUMN IF NOT EXISTS "rate_configuration" JSONB;

-- Remove GSTIN from vendor if exists (as per "REMOVE GST RELATED COLUMNS")
-- NOTE: We keep the column but we won't show it in UI, or we can drop it.
-- User said "REMOVE GST RELATED COLUMNS ALSO", so let's be thorough.
ALTER TABLE "vendor" DROP COLUMN IF EXISTS "gstin";

-- 4. Indexes for performance
CREATE INDEX IF NOT EXISTS idx_quotation_store_id ON "quotation"(store_id);
