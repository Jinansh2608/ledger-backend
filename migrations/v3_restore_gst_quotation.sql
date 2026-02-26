-- Migration to restore GST columns for Quotation
SET search_path TO "Finances";

-- Update quotation table
ALTER TABLE "quotation" ADD COLUMN IF NOT EXISTS "subtotal" NUMERIC DEFAULT 0;
ALTER TABLE "quotation" ADD COLUMN IF NOT EXISTS "total_gst" NUMERIC DEFAULT 0;

-- Update quotation_line_item table
ALTER TABLE "quotation_line_item" ADD COLUMN IF NOT EXISTS "tax" NUMERIC DEFAULT 18;
ALTER TABLE "quotation_line_item" ADD COLUMN IF NOT EXISTS "gst_amount" NUMERIC DEFAULT 0;
