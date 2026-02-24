-- =====================================================
-- NEXGEN ERP DATABASE BACKUP
-- Exported: 2026-02-22 23:09:02
-- Database: Nexgen_erp
-- Schema: Finances
-- Complete replica with schema and data
-- =====================================================

-- Set search path
SET search_path TO "Finances";

-- =====================================================
-- Table: billing_po (0 records)
-- =====================================================

DROP TABLE IF EXISTS "billing_po" CASCADE;

CREATE TABLE "billing_po" (
    "id" bigint DEFAULT nextval('billing_po_id_seq'::regclass) NOT NULL,
    "client_id" bigint NOT NULL,
    "po_number" character varying NOT NULL,
    "amount" numeric,
    "status" character varying DEFAULT 'PENDING'::character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "project_id" bigint,
    "client_po_id" bigint,
    "billed_value" numeric,
    "billed_gst" numeric,
    "billed_total" numeric,
    "billing_notes" text,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: billing_po_line_item (0 records)
-- =====================================================

DROP TABLE IF EXISTS "billing_po_line_item" CASCADE;

CREATE TABLE "billing_po_line_item" (
    "id" bigint DEFAULT nextval('billing_po_line_item_id_seq'::regclass) NOT NULL,
    "billing_po_id" bigint NOT NULL,
    "item_description" character varying,
    "quantity" numeric,
    "unit_price" numeric,
    "amount" numeric,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "description" text,
    "qty" numeric,
    "rate" numeric,
    "total" numeric,
);

-- =====================================================
-- Table: client (2 records)
-- =====================================================

DROP TABLE IF EXISTS "client" CASCADE;

CREATE TABLE "client" (
    "id" bigint DEFAULT nextval('client_id_seq'::regclass) NOT NULL,
    "name" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

