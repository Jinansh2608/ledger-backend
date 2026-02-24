-- =====================================================
-- NEXGEN ERP CLIENTS-ONLY BACKUP
-- Exported: 2026-02-24 11:33:19
-- Database: Nexgen_erp
-- Schema: Finances
-- Only 'client' table data included
-- =====================================================

-- Set search path
SET search_path TO "Finances";

-- Table: billing_po
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
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: billing_po_line_item
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
    "total" numeric
);

-- Table: client
DROP TABLE IF EXISTS "client" CASCADE;
CREATE TABLE "client" (
    "id" bigint DEFAULT nextval('client_id_seq'::regclass) NOT NULL,
    "name" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "client" ("id", "name", "created_at") VALUES (1, 'Bajaj', '2026-02-10 16:02:15.420035');
INSERT INTO "client" ("id", "name", "created_at") VALUES (2, 'Dava India', '2026-02-10 13:00:47.919725');

-- Table: client_payment
DROP TABLE IF EXISTS "client_payment" CASCADE;
CREATE TABLE "client_payment" (
    "id" bigint DEFAULT nextval('client_payment_id_seq'::regclass) NOT NULL,
    "client_id" bigint NOT NULL,
    "client_po_id" bigint,
    "amount" numeric,
    "payment_date" date,
    "status" character varying DEFAULT 'PENDING'::character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "payment_mode" character varying DEFAULT 'neft'::character varying,
    "payment_stage" character varying DEFAULT 'other'::character varying,
    "notes" text,
    "is_tds_deducted" boolean DEFAULT false,
    "tds_amount" numeric DEFAULT 0,
    "received_by_account" character varying,
    "transaction_type" character varying DEFAULT 'credit'::character varying,
    "reference_number" character varying
);

-- Table: client_po
DROP TABLE IF EXISTS "client_po" CASCADE;
CREATE TABLE "client_po" (
    "id" bigint DEFAULT nextval('client_po_id_seq'::regclass) NOT NULL,
    "client_id" bigint,
    "project_id" bigint,
    "po_number" character varying,
    "po_date" date,
    "po_value" numeric,
    "receivable_amount" numeric,
    "status" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "po_type" character varying DEFAULT 'standard'::character varying,
    "parent_po_id" bigint,
    "agreement_date" date,
    "notes" text,
    "pi_number" character varying,
    "pi_date" date,
    "vendor_id" bigint,
    "site_id" bigint,
    "vendor_gstin" character varying,
    "bill_to_gstin" character varying,
    "vendor_address" text,
    "bill_to_address" text,
    "ship_to_address" text,
    "subtotal" numeric,
    "cgst" numeric,
    "sgst" numeric,
    "igst" numeric,
    "total_tax" numeric,
    "store_id" character varying
);

-- Table: client_po_line_item
DROP TABLE IF EXISTS "client_po_line_item" CASCADE;
CREATE TABLE "client_po_line_item" (
    "id" bigint DEFAULT nextval('client_po_line_item_id_seq'::regclass) NOT NULL,
    "client_po_id" bigint,
    "item_name" text NOT NULL,
    "quantity" numeric,
    "unit_price" numeric,
    "total_price" numeric,
    "hsn_code" character varying,
    "unit" character varying,
    "rate" numeric,
    "gst_amount" numeric,
    "gross_amount" numeric
);

-- Table: payment_vendor_link
DROP TABLE IF EXISTS "payment_vendor_link" CASCADE;
CREATE TABLE "payment_vendor_link" (
    "id" bigint DEFAULT nextval('payment_vendor_link_id_seq'::regclass) NOT NULL,
    "vendor_payment_id" bigint NOT NULL,
    "vendor_order_id" bigint NOT NULL,
    "amount_allocated" numeric,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: po_project_mapping
DROP TABLE IF EXISTS "po_project_mapping" CASCADE;
CREATE TABLE "po_project_mapping" (
    "id" bigint DEFAULT nextval('po_project_mapping_id_seq'::regclass) NOT NULL,
    "client_po_id" bigint NOT NULL,
    "project_id" bigint NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: project
DROP TABLE IF EXISTS "project" CASCADE;
CREATE TABLE "project" (
    "id" bigint DEFAULT nextval('project_id_seq'::regclass) NOT NULL,
    "client_id" bigint,
    "name" character varying NOT NULL,
    "status" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "location" character varying,
    "city" character varying,
    "state" character varying,
    "country" character varying,
    "latitude" numeric,
    "longitude" numeric
);

-- Table: project_document
DROP TABLE IF EXISTS "project_document" CASCADE;
CREATE TABLE "project_document" (
    "id" bigint DEFAULT nextval('project_document_id_seq'::regclass) NOT NULL,
    "project_id" bigint NOT NULL,
    "document_name" character varying,
    "document_path" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: site
DROP TABLE IF EXISTS "site" CASCADE;
CREATE TABLE "site" (
    "id" bigint DEFAULT nextval('site_id_seq'::regclass) NOT NULL,
    "store_id" character varying,
    "site_name" character varying NOT NULL,
    "address" text,
    "city" character varying,
    "state" character varying,
    "postal_code" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: upload_file
DROP TABLE IF EXISTS "upload_file" CASCADE;
CREATE TABLE "upload_file" (
    "id" character varying NOT NULL,
    "session_id" character varying NOT NULL,
    "po_number" character varying,
    "original_filename" character varying NOT NULL,
    "storage_filename" character varying NOT NULL,
    "storage_path" text NOT NULL,
    "file_size" bigint NOT NULL,
    "compressed_size" bigint,
    "is_compressed" boolean DEFAULT true,
    "mime_type" character varying,
    "original_mime_type" character varying,
    "file_hash" character varying,
    "compressed_hash" character varying,
    "upload_timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "uploaded_by" character varying,
    "metadata" jsonb DEFAULT '{}'::jsonb,
    "status" character varying DEFAULT 'active'::character varying
);

-- Table: upload_session
DROP TABLE IF EXISTS "upload_session" CASCADE;
CREATE TABLE "upload_session" (
    "id" character varying NOT NULL,
    "session_id" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "expires_at" timestamp without time zone NOT NULL,
    "metadata" jsonb DEFAULT '{}'::jsonb,
    "status" character varying DEFAULT 'active'::character varying,
    "last_activity" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: upload_stats
DROP TABLE IF EXISTS "upload_stats" CASCADE;
CREATE TABLE "upload_stats" (
    "id" character varying NOT NULL,
    "session_id" character varying NOT NULL,
    "total_uploads" integer DEFAULT 0,
    "total_downloads" integer DEFAULT 0,
    "total_size_bytes" bigint DEFAULT 0,
    "last_activity" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: user
DROP TABLE IF EXISTS "user" CASCADE;
CREATE TABLE "user" (
    "id" integer DEFAULT nextval('user_id_seq'::regclass) NOT NULL,
    "username" character varying NOT NULL,
    "email" character varying NOT NULL,
    "password_hash" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: vendor
DROP TABLE IF EXISTS "vendor" CASCADE;
CREATE TABLE "vendor" (
    "id" bigint DEFAULT nextval('vendor_id_seq'::regclass) NOT NULL,
    "name" character varying NOT NULL,
    "address" text,
    "gstin" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "contact_person" character varying,
    "email" character varying,
    "phone" character varying,
    "payment_terms" character varying,
    "status" character varying DEFAULT 'active'::character varying,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: vendor_order
DROP TABLE IF EXISTS "vendor_order" CASCADE;
CREATE TABLE "vendor_order" (
    "id" bigint DEFAULT nextval('vendor_order_id_seq'::regclass) NOT NULL,
    "vendor_id" bigint NOT NULL,
    "po_number" character varying NOT NULL,
    "po_value" numeric,
    "status" character varying DEFAULT 'PENDING'::character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "project_id" bigint,
    "po_date" date,
    "due_date" date,
    "description" text,
    "work_status" character varying DEFAULT 'pending'::character varying,
    "payment_status" character varying DEFAULT 'pending'::character varying,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: vendor_order_line_item
DROP TABLE IF EXISTS "vendor_order_line_item" CASCADE;
CREATE TABLE "vendor_order_line_item" (
    "id" bigint DEFAULT nextval('vendor_order_line_item_id_seq'::regclass) NOT NULL,
    "vendor_order_id" bigint NOT NULL,
    "item_description" character varying,
    "quantity" numeric,
    "unit_price" numeric,
    "amount" numeric,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table: vendor_payment
DROP TABLE IF EXISTS "vendor_payment" CASCADE;
CREATE TABLE "vendor_payment" (
    "id" bigint DEFAULT nextval('vendor_payment_id_seq'::regclass) NOT NULL,
    "vendor_id" bigint NOT NULL,
    "vendor_order_id" bigint,
    "amount" numeric,
    "payment_date" date,
    "status" character varying DEFAULT 'PENDING'::character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

