-- =====================================================
-- NEXGEN ERP DATABASE BACKUP
-- Exported: 2026-02-22 23:09:59
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

INSERT INTO "client" ("id", "name", "created_at") VALUES
(1, 'Bajaj', '2026-02-10 16:02:15.420035'),
(2, 'Dava India', '2026-02-10 13:00:47.919725');

-- =====================================================
-- Table: client_payment (3 records)
-- =====================================================

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
    "reference_number" character varying,
);

INSERT INTO "client_payment" ("id", "client_id", "client_po_id", "amount", "payment_date", "status", "created_at", "payment_mode", "payment_stage", "notes", "is_tds_deducted", "tds_amount", "received_by_account", "transaction_type", "reference_number") VALUES
(16, 1, 133, '100000.00', '2026-02-22', 'cleared', '2026-02-22 16:41:53.873823', 'upi', 'other', 'Advance ', false, '0.00', NULL, 'credit', ''),
(17, 1, 133, '50000.00', '2026-02-22', 'cleared', '2026-02-22 16:57:32.144654', 'neft', 'other', '', false, '0.00', NULL, 'debit', ''),
(18, 1, 133, '50000.00', '2026-02-22', 'cleared', '2026-02-22 17:07:10.152248', 'neft', 'other', '', false, '0.00', NULL, 'credit', '');

-- =====================================================
-- Table: client_po (4 records)
-- =====================================================

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
    "store_id" character varying,
);

INSERT INTO "client_po" ("id", "client_id", "project_id", "po_number", "po_date", "po_value", "receivable_amount", "status", "created_at", "po_type", "parent_po_id", "agreement_date", "notes", "pi_number", "pi_date", "vendor_id", "site_id", "vendor_gstin", "bill_to_gstin", "vendor_address", "bill_to_address", "ship_to_address", "subtotal", "cgst", "sgst", "igst", "total_tax", "store_id") VALUES
(140, 2, NULL, 'PO01483', NULL, '356053.20', '356053.20', 'pending', '2026-02-22 20:52:34.088096', 'standard', NULL, NULL, NULL, '', NULL, 34, 49, '', '', '', '', '', '301740.00', '0.00', '0.00', '0.00', '0.00', 'CMHNAS1697'),
(141, 1, NULL, '4100130800', '2025-12-05', '282359.12', '282359.12', 'active', '2026-02-22 20:53:28.327292', 'standard', NULL, NULL, NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, '282359.12', NULL, NULL, NULL, '0.00', 'FY26'),
(138, 1, NULL, '4100129938', '2025-12-08', '299918.70', '299918.70', 'active', '2026-02-22 20:45:04.988277', 'standard', NULL, NULL, NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, '299918.70', NULL, NULL, NULL, '0.00', 'FY26'),
(142, 1, NULL, '4100133013', '2025-11-20', '561294.29', '561294.29', 'active', '2026-02-22 20:55:01.703300', 'standard', NULL, NULL, NULL, NULL, NULL, NULL, 50, NULL, NULL, NULL, NULL, NULL, '561294.29', NULL, NULL, NULL, '0.00', 'U27');

-- =====================================================
-- Table: client_po_line_item (156 records)
-- =====================================================

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
    "gross_amount" numeric,
);

INSERT INTO "client_po_line_item" ("id", "client_po_id", "item_name", "quantity", "unit_price", "total_price", "hsn_code", "unit", "rate", "gst_amount", "gross_amount") VALUES
(636, 133, 'PARTITION : Single Skin Aluminium', '125.00', NULL, '41300.00', NULL, NULL, NULL, NULL, NULL),
(637, 133, 'INTERIOR WORK : As Per Annexure', '1.00', NULL, '49047.88', NULL, NULL, NULL, NULL, NULL),
(638, 133, 'ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '68427.02', NULL, NULL, NULL, NULL, NULL),
(639, 133, 'Table : Discussion Table 5 x3 (1500 x 900 mm)', '1.00', NULL, '9440.00', NULL, NULL, NULL, NULL, NULL),
(640, 133, 'Manager Table : Providing B.M. table', '2.00', NULL, '16992.00', NULL, NULL, NULL, NULL, NULL),
(641, 133, 'WHITE BOARD OF SIZE 5''X 4''', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(642, 133, 'SOFT BOARD : 4''X 3'' Soft board with Aluminium border (fabric colour Blue)', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(643, 133, 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC', '1.00', NULL, '4130.00', NULL, NULL, NULL, NULL, NULL),
(644, 133, 'FAN : EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(645, 133, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(646, 133, 'Employee Chairs', '2.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(647, 133, 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC', '26.00', NULL, '21476.00', NULL, NULL, NULL, NULL, NULL),
(648, 133, 'Dustbin : 10L : LOCAL : PLASTIC', '3.00', NULL, '1239.00', NULL, NULL, NULL, NULL, NULL),
(649, 133, 'Water Dispenser ( Bubble top)', '1.00', NULL, '826.00', NULL, NULL, NULL, NULL, NULL),
(650, 133, 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex', '2.00', NULL, '4248.00', NULL, NULL, NULL, NULL, NULL),
(651, 133, 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT', '1.00', NULL, '7670.00', NULL, NULL, NULL, NULL, NULL),
(652, 133, 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves', '1.00', NULL, '15930.00', NULL, NULL, NULL, NULL, NULL),
(653, 133, 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size', '1.00', NULL, '2242.00', NULL, NULL, NULL, NULL, NULL),
(654, 133, 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH', '6.00', NULL, '8496.00', NULL, NULL, NULL, NULL, NULL),
(655, 133, 'PILLOWS : 2.0 X 1.5 FT', '6.00', NULL, '3780.00', NULL, NULL, NULL, NULL, NULL),
(656, 133, 'BEDSHEET : SINGLE', '6.00', NULL, '3540.00', NULL, NULL, NULL, NULL, NULL),
(657, 133, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL),
(658, 133, 'Pedestal Drawer Storages', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(659, 134, 'PARTITION : Single Skin Aluminium', '107.00', NULL, '35352.80', NULL, NULL, NULL, NULL, NULL),
(660, 134, 'INTERIOR WORK : As Per Annexure', '1.00', NULL, '32301.32', NULL, NULL, NULL, NULL, NULL),
(661, 134, 'ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '73561.20', NULL, NULL, NULL, NULL, NULL),
(662, 134, 'Table : Discussion Table 5 x3 (1500 x 900 mm)', '1.00', NULL, '9440.00', NULL, NULL, NULL, NULL, NULL),
(663, 134, 'Manager Table : Providing B.M. table', '2.00', NULL, '16992.00', NULL, NULL, NULL, NULL, NULL),
(664, 134, 'WHITE BOARD OF SIZE 5''X 4''', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(665, 134, 'SOFT BOARD : 4''X 3'' Soft board with Aluminium border (fabric colour Blue)', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(666, 134, 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC', '1.00', NULL, '4130.00', NULL, NULL, NULL, NULL, NULL),
(667, 134, 'FAN : EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(668, 134, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(669, 134, 'Employee Chairs', '2.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(670, 134, 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC', '26.00', NULL, '21476.00', NULL, NULL, NULL, NULL, NULL),
(671, 134, 'Dustbin : 10L : LOCAL : PLASTIC', '3.00', NULL, '1239.00', NULL, NULL, NULL, NULL, NULL),
(672, 134, 'Water Dispenser ( Bubble top)', '1.00', NULL, '826.00', NULL, NULL, NULL, NULL, NULL),
(673, 134, 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex', '2.00', NULL, '4248.00', NULL, NULL, NULL, NULL, NULL),
(674, 134, 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT', '1.00', NULL, '7670.00', NULL, NULL, NULL, NULL, NULL),
(675, 134, 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves', '1.00', NULL, '15930.00', NULL, NULL, NULL, NULL, NULL),
(676, 134, 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size', '1.00', NULL, '2242.00', NULL, NULL, NULL, NULL, NULL),
(677, 134, 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH', '6.00', NULL, '8496.00', NULL, NULL, NULL, NULL, NULL),
(678, 134, 'PILLOWS : 2.0 X 1.5 FT', '6.00', NULL, '3780.00', NULL, NULL, NULL, NULL, NULL),
(679, 134, 'BEDSHEET : SINGLE', '6.00', NULL, '3540.00', NULL, NULL, NULL, NULL, NULL),
(680, 134, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL),
(681, 134, 'Pedestal Drawer Storages', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(682, 136, 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)', '1.00', NULL, '11800.00', NULL, NULL, NULL, NULL, NULL),
(683, 136, 'PEDESTAL : MODULAR PEDESTAL', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(684, 136, 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)', '4.00', NULL, '24544.00', NULL, NULL, NULL, NULL, NULL),
(685, 136, 'STORAGES : MODULAR LOW HEIGHT STORAGES : 1200 X 450 X 1200 MM', '1.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(686, 136, 'TABLE : HALF ROUND : 1200 X 1050 X 750 MM : 25MM THICK ISI MARK PLPB TOP IN SLATE GREY COLOUR. 25 MM MS POWDER COATED ROUND LEG AT HALF ROUND SIDE END OF THE TOP.', '1.00', NULL, '10620.00', NULL, NULL, NULL, NULL, NULL),
(687, 136, 'TABLE : PRINTER : 600 X 600 MM : WITH PARTICAL BOARD TOP', '1.00', NULL, '5015.00', NULL, NULL, NULL, NULL, NULL),
(688, 136, 'BOARD : SOFT BOARD : 3'' x 3''', '1.00', NULL, '2596.00', NULL, NULL, NULL, NULL, NULL),
(689, 136, 'BOARD : WHITE BOARD : 4'' x 3''', '1.00', NULL, '2596.00', NULL, NULL, NULL, NULL, NULL),
(690, 136, 'PARTITION : PARTITION SCREEN : 900 x 300 MM : WITH 12MM THK PLPB BOARD FIXED ON INNOFITT BRACKETS FOR LINEAR W/S OF SIZE 800 X 600 (BLUE 01 NOS & GREY 01 QTY TOTAL- 02 NOS)', '2.00', NULL, '3304.00', NULL, NULL, NULL, NULL, NULL),
(691, 136, 'BOX : SUGGESTION BOX : ACRYLIC', '1.00', NULL, '1416.00', NULL, NULL, NULL, NULL, NULL),
(692, 136, 'DOOR : SINGLE SKIN ALUMINUM : 900 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THK PLPB BOARD', '2.00', NULL, '27140.00', NULL, NULL, NULL, NULL, NULL),
(693, 136, 'PARTITION : SINGLE SKIN ALUMINIUM PARTITION : FROM FRONT & BOTH SIDE PARTITION UP TO 7FT HEIGHT- WITH 5MM THICK GLASS & 12MM THK PLPB BOARD COMBINATION ALL AS PER DETAIL DRAWING', '299.23', NULL, '97806.32', NULL, NULL, NULL, NULL, NULL),
(694, 136, 'DOOR : SINGLE SKIN ALUMINUM : 750 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THICK PLPB BOARD', '1.00', NULL, '12685.00', NULL, NULL, NULL, NULL, NULL),
(695, 136, 'ROLLER BLINDS : ROLLING BLINDS : PARYTEX : AS APPROVED - WHITE SHADE', '59.50', NULL, '7723.10', NULL, NULL, NULL, NULL, NULL),
(696, 136, 'FILM : FROSTED FILM', '83.46', NULL, '8863.45', NULL, NULL, NULL, NULL, NULL),
(697, 136, 'CHARGES : TRANSPORTATION CHARGES', '1.00', NULL, '6490.00', NULL, NULL, NULL, NULL, NULL),
(698, 136, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(699, 136, 'FAN : INDUSTRIAL TYPE EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(700, 136, 'FRAME : ACRYLIC ALUMINIUM FRAME : A2 : SANDWICH', '2.00', NULL, '4484.00', NULL, NULL, NULL, NULL, NULL),
(701, 136, 'DUSTBIN : 10 LTR 8" X 12"', '4.00', NULL, '944.00', NULL, NULL, NULL, NULL, NULL),
(702, 136, 'FIRE EXTINGUISHER : ABC : 2 KG', '1.00', NULL, '2065.00', NULL, NULL, NULL, NULL, NULL),
(703, 136, 'FIRE EXTINGUISHER : CO2 : 2 KG', '1.00', NULL, '5074.00', NULL, NULL, NULL, NULL, NULL),
(704, 136, 'DRAWER : CASH DRAWER', '1.00', NULL, '4956.00', NULL, NULL, NULL, NULL, NULL),
(705, 136, 'INTERIOR : OTHER INTERIOR WORK : AS PER ANNEXURE', '1.00', NULL, '109692.82', NULL, NULL, NULL, NULL, NULL),
(706, 136, 'ELECTRICAL : ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '175064.80', NULL, NULL, NULL, NULL, NULL),
(707, 136, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL),
(708, 138, 'PARTITION : Single Skin Aluminium', '125.00', NULL, '41300.00', NULL, NULL, NULL, NULL, NULL),
(709, 138, 'INTERIOR WORK : As Per Annexure', '1.00', NULL, '49047.88', NULL, NULL, NULL, NULL, NULL),
(710, 138, 'ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '68427.02', NULL, NULL, NULL, NULL, NULL),
(711, 138, 'Table : Discussion Table 5 x3 (1500 x 900 mm)', '1.00', NULL, '9440.00', NULL, NULL, NULL, NULL, NULL),
(712, 138, 'Manager Table : Providing B.M. table', '2.00', NULL, '16992.00', NULL, NULL, NULL, NULL, NULL),
(713, 138, 'WHITE BOARD OF SIZE 5''X 4''', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(714, 138, 'SOFT BOARD : 4''X 3'' Soft board with Aluminium border (fabric colour Blue)', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(715, 138, 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC', '1.00', NULL, '4130.00', NULL, NULL, NULL, NULL, NULL),
(716, 138, 'FAN : EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(717, 138, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(718, 138, 'Employee Chairs', '2.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(719, 138, 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC', '26.00', NULL, '21476.00', NULL, NULL, NULL, NULL, NULL),
(720, 138, 'Dustbin : 10L : LOCAL : PLASTIC', '3.00', NULL, '1239.00', NULL, NULL, NULL, NULL, NULL),
(721, 138, 'Water Dispenser ( Bubble top)', '1.00', NULL, '826.00', NULL, NULL, NULL, NULL, NULL),
(722, 138, 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex', '2.00', NULL, '4248.00', NULL, NULL, NULL, NULL, NULL),
(723, 138, 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT', '1.00', NULL, '7670.00', NULL, NULL, NULL, NULL, NULL),
(724, 138, 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves', '1.00', NULL, '15930.00', NULL, NULL, NULL, NULL, NULL),
(725, 138, 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size', '1.00', NULL, '2242.00', NULL, NULL, NULL, NULL, NULL),
(726, 138, 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH', '6.00', NULL, '8496.00', NULL, NULL, NULL, NULL, NULL),
(727, 138, 'PILLOWS : 2.0 X 1.5 FT', '6.00', NULL, '3780.00', NULL, NULL, NULL, NULL, NULL),
(728, 138, 'BEDSHEET : SINGLE', '6.00', NULL, '3540.00', NULL, NULL, NULL, NULL, NULL),
(729, 138, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL),
(730, 138, 'Pedestal Drawer Storages', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(754, 140, 'GYPSUM FALSE CEILING', '272.00', '3916.80', '21760.00', '68091100', 'SQFT', '3916.80', '0.00', '25676.80'),
(755, 140, 'PVC FLOORING 36 X 6, 1.5 mm', '272.00', '4161.60', '23120.00', '39252000', 'SQFT', '4161.60', '0.00', '27281.60'),
(756, 140, 'ELECTRICAL WIRING', '299.00', '6458.40', '35880.00', '74130000', 'SQFT', '6458.40', '0.00', '42338.40'),
(757, 140, 'ACP OUTDOOR PLANNING', '152.00', '6156.00', '34200.00', '76109090', 'SQFT', '6156.00', '0.00', '40356.00'),
(758, 140, 'TUFF GLASS DOOR WITH ALL FITTING LUMSUM', '1.00', '3960.00', '22000.00', '70071900', 'Nos', '3960.00', '0.00', '25960.00'),
(759, 140, 'TUFF GLASS WITH ALL FITTING', '58.00', '3915.00', '21750.00', '70071900', 'SQFT', '3915.00', '0.00', '25665.00'),
(760, 140, 'BRANDING VINYL PRINTING', '231.00', '3742.20', '20790.00', '39199010', 'SQFT', '3742.20', '0.00', '24532.20'),
(761, 140, 'MAIN SIGAGE WITH MS BOX AND PRINTING LG VINAYAL Main Signage: 2"x1" MS Frame with 3mm 0.25 mm Thick ACP Refresh Orange Colour cladding and Branding on 3M IJ 40 with 8520 Lamination and UV Print Vinyl plotter cut letters pasting on the ACP with 3 years warranty', '64.00', '6048.00', '33600.00', '49111020', 'SQFT', '6048.00', '0.00', '39648.00'),
(762, 140, 'Wall Painting', '1088.00', '5875.20', '32640.00', '32141000', 'SQFT', '5875.20', '0.00', '38515.20'),
(763, 140, 'Shutter Boxing', '90.00', '8100.00', '45000.00', '73089090', 'SQFT', '8100.00', '0.00', '53100.00'),
(764, 140, 'Debris Removal', '1.00', '720.00', '4000.00', '999441', 'Nos', '720.00', '0.00', '4720.00'),
(765, 140, 'Scaffolding Rent', '1.00', '1260.00', '7000.00', '995457', 'Nos', '1260.00', '0.00', '8260.00'),
(766, 141, 'PARTITION : Single Skin Aluminium', '107.00', NULL, '35352.80', NULL, NULL, NULL, NULL, NULL),
(767, 141, 'INTERIOR WORK : As Per Annexure', '1.00', NULL, '32301.32', NULL, NULL, NULL, NULL, NULL),
(768, 141, 'ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '73561.20', NULL, NULL, NULL, NULL, NULL),
(769, 141, 'Table : Discussion Table 5 x3 (1500 x 900 mm)', '1.00', NULL, '9440.00', NULL, NULL, NULL, NULL, NULL),
(770, 141, 'Manager Table : Providing B.M. table', '2.00', NULL, '16992.00', NULL, NULL, NULL, NULL, NULL),
(771, 141, 'WHITE BOARD OF SIZE 5''X 4''', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(772, 141, 'SOFT BOARD : 4''X 3'' Soft board with Aluminium border (fabric colour Blue)', '1.00', NULL, '2360.00', NULL, NULL, NULL, NULL, NULL),
(773, 141, 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC', '1.00', NULL, '4130.00', NULL, NULL, NULL, NULL, NULL),
(774, 141, 'FAN : EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(775, 141, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(776, 141, 'Employee Chairs', '2.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(777, 141, 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC', '26.00', NULL, '21476.00', NULL, NULL, NULL, NULL, NULL),
(778, 141, 'Dustbin : 10L : LOCAL : PLASTIC', '3.00', NULL, '1239.00', NULL, NULL, NULL, NULL, NULL),
(779, 141, 'Water Dispenser ( Bubble top)', '1.00', NULL, '826.00', NULL, NULL, NULL, NULL, NULL),
(780, 141, 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex', '2.00', NULL, '4248.00', NULL, NULL, NULL, NULL, NULL),
(781, 141, 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT', '1.00', NULL, '7670.00', NULL, NULL, NULL, NULL, NULL),
(782, 141, 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves', '1.00', NULL, '15930.00', NULL, NULL, NULL, NULL, NULL),
(783, 141, 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size', '1.00', NULL, '2242.00', NULL, NULL, NULL, NULL, NULL),
(784, 141, 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH', '6.00', NULL, '8496.00', NULL, NULL, NULL, NULL, NULL),
(785, 141, 'PILLOWS : 2.0 X 1.5 FT', '6.00', NULL, '3780.00', NULL, NULL, NULL, NULL, NULL),
(786, 141, 'BEDSHEET : SINGLE', '6.00', NULL, '3540.00', NULL, NULL, NULL, NULL, NULL),
(787, 141, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL),
(788, 141, 'Pedestal Drawer Storages', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(789, 142, 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)', '1.00', NULL, '11800.00', NULL, NULL, NULL, NULL, NULL),
(790, 142, 'PEDESTAL : MODULAR PEDESTAL', '1.00', NULL, '5900.00', NULL, NULL, NULL, NULL, NULL),
(791, 142, 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)', '4.00', NULL, '24544.00', NULL, NULL, NULL, NULL, NULL),
(792, 142, 'STORAGES : MODULAR LOW HEIGHT STORAGES : 1200 X 450 X 1200 MM', '1.00', NULL, '14160.00', NULL, NULL, NULL, NULL, NULL),
(793, 142, 'TABLE : HALF ROUND : 1200 X 1050 X 750 MM : 25MM THICK ISI MARK PLPB TOP IN SLATE GREY COLOUR. 25 MM MS POWDER COATED ROUND LEG AT HALF ROUND SIDE END OF THE TOP.', '1.00', NULL, '10620.00', NULL, NULL, NULL, NULL, NULL),
(794, 142, 'TABLE : PRINTER : 600 X 600 MM : WITH PARTICAL BOARD TOP', '1.00', NULL, '5015.00', NULL, NULL, NULL, NULL, NULL),
(795, 142, 'BOARD : SOFT BOARD : 3'' x 3''', '1.00', NULL, '2596.00', NULL, NULL, NULL, NULL, NULL),
(796, 142, 'BOARD : WHITE BOARD : 4'' x 3''', '1.00', NULL, '2596.00', NULL, NULL, NULL, NULL, NULL),
(797, 142, 'PARTITION : PARTITION SCREEN : 900 x 300 MM : WITH 12MM THK PLPB BOARD FIXED ON INNOFITT BRACKETS FOR LINEAR W/S OF SIZE 800 X 600 (BLUE 01 NOS & GREY 01 QTY TOTAL- 02 NOS)', '2.00', NULL, '3304.00', NULL, NULL, NULL, NULL, NULL),
(798, 142, 'BOX : SUGGESTION BOX : ACRYLIC', '1.00', NULL, '1416.00', NULL, NULL, NULL, NULL, NULL),
(799, 142, 'DOOR : SINGLE SKIN ALUMINUM : 900 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THK PLPB BOARD', '2.00', NULL, '27140.00', NULL, NULL, NULL, NULL, NULL),
(800, 142, 'PARTITION : SINGLE SKIN ALUMINIUM PARTITION : FROM FRONT & BOTH SIDE PARTITION UP TO 7FT HEIGHT- WITH 5MM THICK GLASS & 12MM THK PLPB BOARD COMBINATION ALL AS PER DETAIL DRAWING', '299.23', NULL, '97806.32', NULL, NULL, NULL, NULL, NULL),
(801, 142, 'DOOR : SINGLE SKIN ALUMINUM : 750 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THICK PLPB BOARD', '1.00', NULL, '12685.00', NULL, NULL, NULL, NULL, NULL),
(802, 142, 'ROLLER BLINDS : ROLLING BLINDS : PARYTEX : AS APPROVED - WHITE SHADE', '59.50', NULL, '7723.10', NULL, NULL, NULL, NULL, NULL),
(803, 142, 'FILM : FROSTED FILM', '83.46', NULL, '8863.45', NULL, NULL, NULL, NULL, NULL),
(804, 142, 'CHARGES : TRANSPORTATION CHARGES', '1.00', NULL, '6490.00', NULL, NULL, NULL, NULL, NULL),
(805, 142, 'FAN : CEILING : 48" DIA', '5.00', NULL, '12980.00', NULL, NULL, NULL, NULL, NULL),
(806, 142, 'FAN : INDUSTRIAL TYPE EXHAUST : 9" DIA', '1.00', NULL, '1947.00', NULL, NULL, NULL, NULL, NULL),
(807, 142, 'FRAME : ACRYLIC ALUMINIUM FRAME : A2 : SANDWICH', '2.00', NULL, '4484.00', NULL, NULL, NULL, NULL, NULL),
(808, 142, 'DUSTBIN : 10 LTR 8" X 12"', '4.00', NULL, '944.00', NULL, NULL, NULL, NULL, NULL),
(809, 142, 'FIRE EXTINGUISHER : ABC : 2 KG', '1.00', NULL, '2065.00', NULL, NULL, NULL, NULL, NULL),
(810, 142, 'FIRE EXTINGUISHER : CO2 : 2 KG', '1.00', NULL, '5074.00', NULL, NULL, NULL, NULL, NULL),
(811, 142, 'DRAWER : CASH DRAWER', '1.00', NULL, '4956.00', NULL, NULL, NULL, NULL, NULL),
(812, 142, 'INTERIOR : OTHER INTERIOR WORK : AS PER ANNEXURE', '1.00', NULL, '109692.82', NULL, NULL, NULL, NULL, NULL),
(813, 142, 'ELECTRICAL : ELECTRICAL WORK : AS PER ANNEXURE', '1.00', NULL, '175064.80', NULL, NULL, NULL, NULL, NULL),
(814, 142, 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER', '1.00', NULL, '1427.80', NULL, NULL, NULL, NULL, NULL);

-- =====================================================
-- Table: payment_vendor_link (0 records)
-- =====================================================

DROP TABLE IF EXISTS "payment_vendor_link" CASCADE;

CREATE TABLE "payment_vendor_link" (
    "id" bigint DEFAULT nextval('payment_vendor_link_id_seq'::regclass) NOT NULL,
    "vendor_payment_id" bigint NOT NULL,
    "vendor_order_id" bigint NOT NULL,
    "amount_allocated" numeric,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: po_project_mapping (0 records)
-- =====================================================

DROP TABLE IF EXISTS "po_project_mapping" CASCADE;

CREATE TABLE "po_project_mapping" (
    "id" bigint DEFAULT nextval('po_project_mapping_id_seq'::regclass) NOT NULL,
    "client_po_id" bigint NOT NULL,
    "project_id" bigint NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: project (0 records)
-- =====================================================

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
    "longitude" numeric,
);

-- =====================================================
-- Table: project_document (0 records)
-- =====================================================

DROP TABLE IF EXISTS "project_document" CASCADE;

CREATE TABLE "project_document" (
    "id" bigint DEFAULT nextval('project_document_id_seq'::regclass) NOT NULL,
    "project_id" bigint NOT NULL,
    "document_name" character varying,
    "document_path" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: site (3 records)
-- =====================================================

DROP TABLE IF EXISTS "site" CASCADE;

CREATE TABLE "site" (
    "id" bigint DEFAULT nextval('site_id_seq'::regclass) NOT NULL,
    "store_id" character varying,
    "site_name" character varying NOT NULL,
    "address" text,
    "city" character varying,
    "state" character varying,
    "postal_code" character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO "site" ("id", "store_id", "site_name", "address", "city", "state", "postal_code", "created_at") VALUES
(48, 'FY26', 'FY26', NULL, NULL, NULL, NULL, '2026-02-22 20:45:04.988277'),
(49, 'CMHNAS1697', 'CMHNAS1697', NULL, NULL, NULL, NULL, '2026-02-22 20:52:34.088096'),
(50, 'U27', 'U27', NULL, NULL, NULL, NULL, '2026-02-22 20:55:01.703300');

-- =====================================================
-- Table: upload_file (5 records)
-- =====================================================

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
    "status" character varying DEFAULT 'active'::character varying,
);

INSERT INTO "upload_file" ("id", "session_id", "po_number", "original_filename", "storage_filename", "storage_path", "file_size", "compressed_size", "is_compressed", "mime_type", "original_mime_type", "file_hash", "compressed_hash", "upload_timestamp", "uploaded_by", "metadata", "status") VALUES
('e358a8ae-0dd7-41ff-93cf-1f782e05a467', 'sess_client1_20260222_151922_bacd', NULL, 'BAJAJ2.xlsx', '20260222_151922_c4f52806a61ddd651eee09477ff4c81e.xlsx', 'sess_client1_20260222_151922_bacd', 17116, 14303, true, 'application/gzip', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '21e7a597a196887dee5c150a57491bc3b708f21829ea4f37addcf2d8c07a0768', '17d0244ab57b9d98c5d1a10938f4360e91329f01de5bd4e660270f78e4e7a861', '2026-02-22 20:49:22.671206', NULL, '{'parsed': True, 'line_items': [{'amount': 35352.8, 'quantity': 107.0, 'row_index': 3, 'description': 'PARTITION : Single Skin Aluminium'}, {'amount': 32301.32, 'quantity': 1.0, 'row_index': 4, 'description': 'INTERIOR WORK : As Per Annexure'}, {'amount': 73561.2, 'quantity': 1.0, 'row_index': 5, 'description': 'ELECTRICAL WORK : AS PER ANNEXURE'}, {'amount': 9440.0, 'quantity': 1.0, 'row_index': 6, 'description': 'Table : Discussion Table 5 x3 (1500 x 900 mm)'}, {'amount': 16992.0, 'quantity': 2.0, 'row_index': 7, 'description': 'Manager Table : Providing B.M. table'}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 8, 'description': "WHITE BOARD OF SIZE 5'X 4'"}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 9, 'description': "SOFT BOARD : 4'X 3' Soft board with Aluminium border (fabric colour Blue)"}, {'amount': 4130.0, 'quantity': 1.0, 'row_index': 10, 'description': 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC'}, {'amount': 1947.0, 'quantity': 1.0, 'row_index': 11, 'description': 'FAN : EXHAUST : 9" DIA'}, {'amount': 12980.0, 'quantity': 5.0, 'row_index': 12, 'description': 'FAN : CEILING : 48" DIA'}, {'amount': 14160.0, 'quantity': 2.0, 'row_index': 13, 'description': 'Employee Chairs'}, {'amount': 21476.0, 'quantity': 26.0, 'row_index': 14, 'description': 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC'}, {'amount': 1239.0, 'quantity': 3.0, 'row_index': 15, 'description': 'Dustbin : 10L : LOCAL : PLASTIC'}, {'amount': 826.0, 'quantity': 1.0, 'row_index': 16, 'description': 'Water Dispenser ( Bubble top)'}, {'amount': 4248.0, 'quantity': 2.0, 'row_index': 17, 'description': 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex'}, {'amount': 7670.0, 'quantity': 1.0, 'row_index': 18, 'description': 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT'}, {'amount': 15930.0, 'quantity': 1.0, 'row_index': 19, 'description': 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves'}, {'amount': 2242.0, 'quantity': 1.0, 'row_index': 20, 'description': 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size'}, {'amount': 8496.0, 'quantity': 6.0, 'row_index': 21, 'description': 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH'}, {'amount': 3780.0, 'quantity': 6.0, 'row_index': 22, 'description': 'PILLOWS : 2.0 X 1.5 FT'}, {'amount': 3540.0, 'quantity': 6.0, 'row_index': 23, 'description': 'BEDSHEET : SINGLE'}, {'amount': 1427.8, 'quantity': 1.0, 'row_index': 24, 'description': 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER'}, {'amount': 5900.0, 'quantity': 1.0, 'row_index': 25, 'description': 'Pedestal Drawer Storages'}], 'po_details': {'po_date': '2025-12-05', 'store_id': 'FY26', 'po_number': '4100130800', 'site_address': 'Tisri MFI 01 FY26� : Jharkhand : Bajaj Finance Limited : Tisri MFI, Giridih, Jharkhand-815317'}, 'client_name': 'Bajaj', 'parser_type': 'po', 'line_item_count': 23}', 'active'),
('6588175b-333d-43a9-8902-5ae5f75f6a86', 'sess_client2_20260222_152233_175e', NULL, 'Davaindia Lokhande Mala, Jail Road, Nashik Maharastra Proforma Invoice No. 1.xlsx', '20260222_152233_4bf324caf5fc30a0285454c5be16aee7.xlsx', 'sess_client2_20260222_152233_175e', 137532, 137532, false, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'a1f773004b7bed6f16c219d873b9bfcac749d811d5a9783120297cecc0581a17', 'a1f773004b7bed6f16c219d873b9bfcac749d811d5a9783120297cecc0581a17', '2026-02-22 20:52:33.833113', NULL, '{'parsed': True, 'line_items': [{'sr': 1, 'rate': 3916.7999999999997, 'unit': 'SQFT', 'boq_name': 'GYPSUM FALSE CEILING', 'hsn_code': '68091100', 'quantity': 272.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 25676.8, 'taxable_amount': 21760.0, 'total_with_gst': 25676.8}, {'sr': 2, 'rate': 4161.599999999999, 'unit': 'SQFT', 'boq_name': 'PVC FLOORING 36 X 6, 1.5 mm', 'hsn_code': '39252000', 'quantity': 272.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 27281.6, 'taxable_amount': 23120.0, 'total_with_gst': 27281.6}, {'sr': 3, 'rate': 6458.4, 'unit': 'SQFT', 'boq_name': 'ELECTRICAL WIRING', 'hsn_code': '74130000', 'quantity': 299.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 42338.4, 'taxable_amount': 35880.0, 'total_with_gst': 42338.4}, {'sr': 4, 'rate': 6156.0, 'unit': 'SQFT', 'boq_name': 'ACP OUTDOOR PLANNING', 'hsn_code': '76109090', 'quantity': 152.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 40356.0, 'taxable_amount': 34200.0, 'total_with_gst': 40356.0}, {'sr': 5, 'rate': 3960.0, 'unit': 'Nos', 'boq_name': 'TUFF GLASS DOOR WITH ALL FITTING LUMSUM', 'hsn_code': '70071900', 'quantity': 1.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 25960.0, 'taxable_amount': 22000.0, 'total_with_gst': 25960.0}, {'sr': 6, 'rate': 3915.0, 'unit': 'SQFT', 'boq_name': 'TUFF GLASS WITH ALL FITTING', 'hsn_code': '70071900', 'quantity': 58.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 25665.0, 'taxable_amount': 21750.0, 'total_with_gst': 25665.0}, {'sr': 7, 'rate': 3742.2, 'unit': 'SQFT', 'boq_name': 'BRANDING VINYL PRINTING', 'hsn_code': '39199010', 'quantity': 231.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 24532.2, 'taxable_amount': 20790.0, 'total_with_gst': 24532.2}, {'sr': 8, 'rate': 6048.0, 'unit': 'SQFT', 'boq_name': 'MAIN SIGAGE WITH MS BOX AND PRINTING LG VINAYAL Main Signage: 2"x1" MS Frame with 3mm 0.25 mm Thick ACP Refresh Orange Colour cladding and Branding on 3M IJ 40 with 8520 Lamination and UV Print Vinyl plotter cut letters pasting on the ACP with 3 years warranty', 'hsn_code': '49111020', 'quantity': 64.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 39648.0, 'taxable_amount': 33600.0, 'total_with_gst': 39648.0}, {'sr': 9, 'rate': 5875.2, 'unit': 'SQFT', 'boq_name': 'Wall Painting', 'hsn_code': '32141000', 'quantity': 1088.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 38515.2, 'taxable_amount': 32640.0, 'total_with_gst': 38515.2}, {'sr': 10, 'rate': 8100.0, 'unit': 'SQFT', 'boq_name': 'Shutter Boxing', 'hsn_code': '73089090', 'quantity': 90.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 53100.0, 'taxable_amount': 45000.0, 'total_with_gst': 53100.0}, {'sr': 11, 'rate': 720.0, 'unit': 'Nos', 'boq_name': 'Debris Removal', 'hsn_code': '999441', 'quantity': 1.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 4720.0, 'taxable_amount': 4000.0, 'total_with_gst': 4720.0}, {'sr': 12, 'rate': 1260.0, 'unit': 'Nos', 'boq_name': 'Scaffolding Rent', 'hsn_code': '995457', 'quantity': 1.0, 'tax_rate': '', 'gst_amount': 0.0, 'tax_amount': 0.0, 'gross_amount': 8260.0, 'taxable_amount': 7000.0, 'total_with_gst': 8260.0}], 'po_details': {'cgst': 0.0, 'igst': 0.0, 'sgst': 0.0, 'pi_date': None, 'po_date': None, 'store_id': 'CMHNAS1697', 'subtotal': 0.0, 'pi_number': '', 'po_number': 'PO01483', 'site_name': '', 'client_name': '708, 7TH FLOOR, PALM SPRING CENTRE PREMISES CO-OP SOC. LTD.,LINK ROAD, MALAD WEST, MUMBAI. 400-064.', 'vendor_name': '708, 7TH FLOOR, PALM SPRING CENTRE PREMISES CO-OP SOC. LTD.,LINK ROAD, MALAD WEST, MUMBAI. 400-064.', 'total_amount': 356053.19999999995, 'vendor_gstin': '', 'bill_to_gstin': '', 'vendor_address': '', 'bill_to_address': '', 'ship_to_address': '', 'client_po_number': 'PO01483'}, 'client_name': 'Dava India', 'parser_type': 'proforma_invoice', 'line_item_count': 12}', 'active'),
('4a415c32-743a-42a9-a1cb-49c352cf1c55', 'sess_client1_20260222_152328_8fad', NULL, 'BAJAJ2.xlsx', '20260222_152328_c9cb82ab98b8c079e4587cbc9f587fd8.xlsx', 'sess_client1_20260222_152328_8fad', 17116, 14303, true, 'application/gzip', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '21e7a597a196887dee5c150a57491bc3b708f21829ea4f37addcf2d8c07a0768', '42f7a7741643bbbfaf221ea8e50d7954a4f898e5a5ca2c8233b3dac3079f6af4', '2026-02-22 20:53:28.291965', NULL, '{'parsed': True, 'line_items': [{'amount': 35352.8, 'quantity': 107.0, 'row_index': 3, 'description': 'PARTITION : Single Skin Aluminium'}, {'amount': 32301.32, 'quantity': 1.0, 'row_index': 4, 'description': 'INTERIOR WORK : As Per Annexure'}, {'amount': 73561.2, 'quantity': 1.0, 'row_index': 5, 'description': 'ELECTRICAL WORK : AS PER ANNEXURE'}, {'amount': 9440.0, 'quantity': 1.0, 'row_index': 6, 'description': 'Table : Discussion Table 5 x3 (1500 x 900 mm)'}, {'amount': 16992.0, 'quantity': 2.0, 'row_index': 7, 'description': 'Manager Table : Providing B.M. table'}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 8, 'description': "WHITE BOARD OF SIZE 5'X 4'"}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 9, 'description': "SOFT BOARD : 4'X 3' Soft board with Aluminium border (fabric colour Blue)"}, {'amount': 4130.0, 'quantity': 1.0, 'row_index': 10, 'description': 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC'}, {'amount': 1947.0, 'quantity': 1.0, 'row_index': 11, 'description': 'FAN : EXHAUST : 9" DIA'}, {'amount': 12980.0, 'quantity': 5.0, 'row_index': 12, 'description': 'FAN : CEILING : 48" DIA'}, {'amount': 14160.0, 'quantity': 2.0, 'row_index': 13, 'description': 'Employee Chairs'}, {'amount': 21476.0, 'quantity': 26.0, 'row_index': 14, 'description': 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC'}, {'amount': 1239.0, 'quantity': 3.0, 'row_index': 15, 'description': 'Dustbin : 10L : LOCAL : PLASTIC'}, {'amount': 826.0, 'quantity': 1.0, 'row_index': 16, 'description': 'Water Dispenser ( Bubble top)'}, {'amount': 4248.0, 'quantity': 2.0, 'row_index': 17, 'description': 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex'}, {'amount': 7670.0, 'quantity': 1.0, 'row_index': 18, 'description': 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT'}, {'amount': 15930.0, 'quantity': 1.0, 'row_index': 19, 'description': 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves'}, {'amount': 2242.0, 'quantity': 1.0, 'row_index': 20, 'description': 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size'}, {'amount': 8496.0, 'quantity': 6.0, 'row_index': 21, 'description': 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH'}, {'amount': 3780.0, 'quantity': 6.0, 'row_index': 22, 'description': 'PILLOWS : 2.0 X 1.5 FT'}, {'amount': 3540.0, 'quantity': 6.0, 'row_index': 23, 'description': 'BEDSHEET : SINGLE'}, {'amount': 1427.8, 'quantity': 1.0, 'row_index': 24, 'description': 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER'}, {'amount': 5900.0, 'quantity': 1.0, 'row_index': 25, 'description': 'Pedestal Drawer Storages'}], 'po_details': {'po_date': '2025-12-05', 'store_id': 'FY26', 'po_number': '4100130800', 'site_address': 'Tisri MFI 01 FY26� : Jharkhand : Bajaj Finance Limited : Tisri MFI, Giridih, Jharkhand-815317'}, 'client_name': 'Bajaj', 'parser_type': 'po', 'line_item_count': 23}', 'active'),
('3233059b-81c0-4bcb-947f-c9d2aca60f2d', 'sess_client1_20260222_152501_597c', NULL, 'BAJAJ3.xlsx', '20260222_152501_dc703b924602a98664ae5e89ddfb33cd.xlsx', 'sess_client1_20260222_152501_597c', 17959, 15100, true, 'application/gzip', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '5a358634d4f10393d4879bca7463d2ac59973922e3773fcb7c3a0241de468643', '536ecae750460e80378f912a69681ea5ec78e4aec0dc9d58dc03be1d6d91dc91', '2026-02-22 20:55:01.660021', NULL, '{'parsed': True, 'line_items': [{'amount': 11800.0, 'quantity': 1.0, 'row_index': 3, 'description': 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)'}, {'amount': 5900.0, 'quantity': 1.0, 'row_index': 4, 'description': 'PEDESTAL : MODULAR PEDESTAL'}, {'amount': 24544.0, 'quantity': 4.0, 'row_index': 5, 'description': 'CABIN : CASHIER : 25MM THICK PLPB TOP (SIZE-1500X600) 18MM THICK PLPB LEG (SIZE 600X725MM), 18MM THICK PLPB MODESTY (SIZE-1500X600MM), 25MM THICK PLPB SERVICE TOP (SIZE-1500X450MM)'}, {'amount': 14160.0, 'quantity': 1.0, 'row_index': 6, 'description': 'STORAGES : MODULAR LOW HEIGHT STORAGES : 1200 X 450 X 1200 MM'}, {'amount': 10620.0, 'quantity': 1.0, 'row_index': 7, 'description': 'TABLE : HALF ROUND : 1200 X 1050 X 750 MM : 25MM THICK ISI MARK PLPB TOP IN SLATE GREY COLOUR. 25 MM MS POWDER COATED ROUND LEG AT HALF ROUND SIDE END OF THE TOP.'}, {'amount': 5015.0, 'quantity': 1.0, 'row_index': 8, 'description': 'TABLE : PRINTER : 600 X 600 MM : WITH PARTICAL BOARD TOP'}, {'amount': 2596.0, 'quantity': 1.0, 'row_index': 9, 'description': "BOARD : SOFT BOARD : 3' x 3'"}, {'amount': 2596.0, 'quantity': 1.0, 'row_index': 10, 'description': "BOARD : WHITE BOARD : 4' x 3'"}, {'amount': 3304.0, 'quantity': 2.0, 'row_index': 11, 'description': 'PARTITION : PARTITION SCREEN : 900 x 300 MM : WITH 12MM THK PLPB BOARD FIXED ON INNOFITT BRACKETS FOR LINEAR W/S OF SIZE 800 X 600 (BLUE 01 NOS & GREY 01 QTY TOTAL- 02 NOS)'}, {'amount': 1416.0, 'quantity': 1.0, 'row_index': 12, 'description': 'BOX : SUGGESTION BOX : ACRYLIC'}, {'amount': 27140.0, 'quantity': 2.0, 'row_index': 13, 'description': 'DOOR : SINGLE SKIN ALUMINUM : 900 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THK PLPB BOARD'}, {'amount': 97806.32, 'quantity': 299.23, 'row_index': 14, 'description': 'PARTITION : SINGLE SKIN ALUMINIUM PARTITION : FROM FRONT & BOTH SIDE PARTITION UP TO 7FT HEIGHT- WITH 5MM THICK GLASS & 12MM THK PLPB BOARD COMBINATION ALL AS PER DETAIL DRAWING'}, {'amount': 12685.0, 'quantity': 1.0, 'row_index': 15, 'description': 'DOOR : SINGLE SKIN ALUMINUM : 750 x 2100 MM : WITH DOOR CLOSER & FITTING COMBINATION OF 5MM THICK GLASS & 12MM THICK PLPB BOARD'}, {'amount': 7723.1, 'quantity': 59.5, 'row_index': 16, 'description': 'ROLLER BLINDS : ROLLING BLINDS : PARYTEX : AS APPROVED - WHITE SHADE'}, {'amount': 8863.45, 'quantity': 83.46, 'row_index': 17, 'description': 'FILM : FROSTED FILM'}, {'amount': 6490.0, 'quantity': 1.0, 'row_index': 18, 'description': 'CHARGES : TRANSPORTATION CHARGES'}, {'amount': 12980.0, 'quantity': 5.0, 'row_index': 19, 'description': 'FAN : CEILING : 48" DIA'}, {'amount': 1947.0, 'quantity': 1.0, 'row_index': 20, 'description': 'FAN : INDUSTRIAL TYPE EXHAUST : 9" DIA'}, {'amount': 4484.0, 'quantity': 2.0, 'row_index': 21, 'description': 'FRAME : ACRYLIC ALUMINIUM FRAME : A2 : SANDWICH'}, {'amount': 944.0, 'quantity': 4.0, 'row_index': 22, 'description': 'DUSTBIN : 10 LTR 8" X 12"'}, {'amount': 2065.0, 'quantity': 1.0, 'row_index': 23, 'description': 'FIRE EXTINGUISHER : ABC : 2 KG'}, {'amount': 5074.0, 'quantity': 1.0, 'row_index': 24, 'description': 'FIRE EXTINGUISHER : CO2 : 2 KG'}, {'amount': 4956.0, 'quantity': 1.0, 'row_index': 25, 'description': 'DRAWER : CASH DRAWER'}, {'amount': 109692.82, 'quantity': 1.0, 'row_index': 26, 'description': 'INTERIOR : OTHER INTERIOR WORK : AS PER ANNEXURE'}, {'amount': 175064.8, 'quantity': 1.0, 'row_index': 27, 'description': 'ELECTRICAL : ELECTRICAL WORK : AS PER ANNEXURE'}, {'amount': 1427.8, 'quantity': 1.0, 'row_index': 28, 'description': 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER'}], 'po_details': {'po_date': '2025-11-20', 'store_id': 'U27', 'po_number': '4100133013', 'site_address': 'Temathani U27 :1st Floor ,Opposite Of Temathani Bus Stand, Above Medplus Pharmacy, Lutunia,Temathani, Medinipur West, 721166, West Bengal'}, 'client_name': 'Bajaj', 'parser_type': 'po', 'line_item_count': 26}', 'active'),
('e0bf1359-5700-4899-aad8-884a3fd25f83', 'sess_client1_20260222_151504_8dd2', NULL, 'BAJAJ PO.xlsx', '20260222_151504_db50bd5c294cb876ae9bab44a145a22b.xlsx', 'sess_client1_20260222_151504_8dd2', 17089, 14249, true, 'application/gzip', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'bde527853e95a29b7a9103ef0412387c9c068de50240e8a23dac5a3a1c0723b1', '99d39629ba5551ef593c655363a2d27376c412108dc41045c2d88acd35da52f2', '2026-02-22 20:45:04.944638', NULL, '{'parsed': True, 'line_items': [{'amount': 41300.0, 'quantity': 125.0, 'row_index': 3, 'description': 'PARTITION : Single Skin Aluminium'}, {'amount': 49047.88, 'quantity': 1.0, 'row_index': 4, 'description': 'INTERIOR WORK : As Per Annexure'}, {'amount': 68427.02, 'quantity': 1.0, 'row_index': 5, 'description': 'ELECTRICAL WORK : AS PER ANNEXURE'}, {'amount': 9440.0, 'quantity': 1.0, 'row_index': 6, 'description': 'Table : Discussion Table 5 x3 (1500 x 900 mm)'}, {'amount': 16992.0, 'quantity': 2.0, 'row_index': 7, 'description': 'Manager Table : Providing B.M. table'}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 8, 'description': "WHITE BOARD OF SIZE 5'X 4'"}, {'amount': 2360.0, 'quantity': 1.0, 'row_index': 9, 'description': "SOFT BOARD : 4'X 3' Soft board with Aluminium border (fabric colour Blue)"}, {'amount': 4130.0, 'quantity': 1.0, 'row_index': 10, 'description': 'TABLE : DISCUSSION : 1200 MM DIA : PLASTIC'}, {'amount': 1947.0, 'quantity': 1.0, 'row_index': 11, 'description': 'FAN : EXHAUST : 9" DIA'}, {'amount': 12980.0, 'quantity': 5.0, 'row_index': 12, 'description': 'FAN : CEILING : 48" DIA'}, {'amount': 14160.0, 'quantity': 2.0, 'row_index': 13, 'description': 'Employee Chairs'}, {'amount': 21476.0, 'quantity': 26.0, 'row_index': 14, 'description': 'CHAIR : CUSTOMER : NILKAMAL/CELLO : PLASTIC'}, {'amount': 1239.0, 'quantity': 3.0, 'row_index': 15, 'description': 'Dustbin : 10L : LOCAL : PLASTIC'}, {'amount': 826.0, 'quantity': 1.0, 'row_index': 16, 'description': 'Water Dispenser ( Bubble top)'}, {'amount': 4248.0, 'quantity': 2.0, 'row_index': 17, 'description': 'ABC Fire Extinguisher 1 Kg : Safex / Aimex/ Kanex'}, {'amount': 7670.0, 'quantity': 1.0, 'row_index': 18, 'description': 'NON LIT FLEX WITH MS FRAME : 10 X 3 FT : 3M or LG FLEX PRINT'}, {'amount': 15930.0, 'quantity': 1.0, 'row_index': 19, 'description': 'Storage Almirah (7X3) : Full Height Steel - Gauge with 05 Shelves'}, {'amount': 2242.0, 'quantity': 1.0, 'row_index': 20, 'description': 'Acrylic Aluminium Frame Frame Aluminium Sandwich A2 Size'}, {'amount': 8496.0, 'quantity': 6.0, 'row_index': 21, 'description': 'MATTRESS : 6.0 X 4.0 FT : COTTON AND THICKNESS SHOULD BE 4 INCH'}, {'amount': 3780.0, 'quantity': 6.0, 'row_index': 22, 'description': 'PILLOWS : 2.0 X 1.5 FT'}, {'amount': 3540.0, 'quantity': 6.0, 'row_index': 23, 'description': 'BEDSHEET : SINGLE'}, {'amount': 1427.8, 'quantity': 1.0, 'row_index': 24, 'description': 'WALL MOUNTED COMPLIANCE STANDEE WITH A4 SIZE FOLDER'}, {'amount': 5900.0, 'quantity': 1.0, 'row_index': 25, 'description': 'Pedestal Drawer Storages'}], 'po_details': {'po_date': '2025-12-08', 'store_id': 'FY26', 'po_number': '4100129938', 'site_address': 'Balumath MFI 01 FY26� : Jharkhand : Bajaj Finance Limited : Balumath MFI, Latehar, Jharkhand-829202'}, 'client_name': 'Bajaj', 'parser_type': 'po', 'line_item_count': 23}', 'active');

-- =====================================================
-- Table: upload_session (5 records)
-- =====================================================

DROP TABLE IF EXISTS "upload_session" CASCADE;

CREATE TABLE "upload_session" (
    "id" character varying NOT NULL,
    "session_id" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "expires_at" timestamp without time zone NOT NULL,
    "metadata" jsonb DEFAULT '{}'::jsonb,
    "status" character varying DEFAULT 'active'::character varying,
    "last_activity" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO "upload_session" ("id", "session_id", "created_at", "expires_at", "metadata", "status", "last_activity") VALUES
('ec764d01-a7bb-43ff-ac96-b77af7068fa2', 'sess_client1_20260222_151922_bacd', '2026-02-22 20:49:22.626267', '2026-02-23 15:19:22.625429', '{'client_id': 1, 'project_id': None, 'client_name': 'Bajaj', 'parser_type': 'po', 'upload_type': 'po'}', 'active', '2026-02-22 20:49:22.626267'),
('4ac4f1c8-da43-47bf-8896-5c752b7eea5d', 'sess_client1_20260222_152501_597c', '2026-02-22 20:55:01.637873', '2026-02-23 15:25:01.147898', '{'client_id': 1, 'project_id': None, 'client_name': 'Bajaj', 'parser_type': 'po', 'upload_type': 'po'}', 'active', '2026-02-22 20:55:01.637873'),
('46384674-5b62-467a-80bf-1dc43c693a3f', 'sess_client2_20260222_152233_175e', '2026-02-22 20:52:33.774934', '2026-02-23 15:22:33.773915', '{'client_id': 2, 'project_id': None, 'client_name': 'Dava India', 'parser_type': 'proforma_invoice', 'upload_type': 'po'}', 'active', '2026-02-22 20:52:33.774934'),
('0b31cafa-ba13-4c58-a8c1-80e184029457', 'sess_client1_20260222_152328_8fad', '2026-02-22 20:53:28.279333', '2026-02-23 15:23:28.278426', '{'client_id': 1, 'project_id': None, 'client_name': 'Bajaj', 'parser_type': 'po', 'upload_type': 'po'}', 'active', '2026-02-22 20:53:28.279333'),
('01370bdf-5abc-4069-a0d0-355bbe97dfff', 'sess_client1_20260222_151504_8dd2', '2026-02-22 20:45:04.920857', '2026-02-23 15:15:04.469063', '{'client_id': 1, 'project_id': None, 'client_name': 'Bajaj', 'parser_type': 'po', 'upload_type': 'po'}', 'active', '2026-02-22 20:45:04.920857');

-- =====================================================
-- Table: upload_stats (0 records)
-- =====================================================

DROP TABLE IF EXISTS "upload_stats" CASCADE;

CREATE TABLE "upload_stats" (
    "id" character varying NOT NULL,
    "session_id" character varying NOT NULL,
    "total_uploads" integer DEFAULT 0,
    "total_downloads" integer DEFAULT 0,
    "total_size_bytes" bigint DEFAULT 0,
    "last_activity" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: user (5 records)
-- =====================================================

DROP TABLE IF EXISTS "user" CASCADE;

CREATE TABLE "user" (
    "id" integer DEFAULT nextval('user_id_seq'::regclass) NOT NULL,
    "username" character varying NOT NULL,
    "email" character varying NOT NULL,
    "password_hash" character varying NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO "user" ("id", "username", "email", "password_hash", "created_at", "updated_at") VALUES
(1, 'test5', 'test5@example.com', '$2b$12$tkotEcKNDHoceEWmhGAVFONVPT47s6uwETFrfGxIjoTeIYsySnD6W', '2026-02-22 08:42:20.773962', '2026-02-22 14:12:20.774042'),
(2, 'subagent1', 'subagent1@example.com', '$2b$12$dfhdcRMeBBoCZfw4e6Jzh.jy2lMPjAo6WuKpTiMD5t3si8FBttsve', '2026-02-22 08:44:17.371533', '2026-02-22 14:14:17.371719'),
(3, 'subagentX', 'subagentX@example.com', '$2b$12$gth40GC3mNi.P3G2bezi.uP6J/lmhaI2ZcYoCp3CsDbzsiDfyGraK', '2026-02-22 08:46:12.626894', '2026-02-22 14:16:12.626973'),
(4, 'test7', 'test7@example.com', '$2b$12$jY0.2evELtEfJADfDV9OBe3/5cORuSDpN.372heD.PNw3YuWOohLO', '2026-02-22 09:27:58.307823', '2026-02-22 14:57:58.307927'),
(5, 'shahjinansh09@gmail.com', 'shahjinansh09@gmail.com', '$2b$12$80wC37RyEe1uXp6WvdjRP.5u6D3Zm4tvK1KNnwCSprYfbEC.4iiUG', '2026-02-22 09:32:59.488567', '2026-02-22 15:02:59.488698');

-- =====================================================
-- Table: vendor (13 records)
-- =====================================================

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
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO "vendor" ("id", "name", "address", "gstin", "created_at", "contact_person", "email", "phone", "payment_terms", "status", "updated_at") VALUES
(32, 'A', NULL, NULL, '2026-02-18 01:37:23.563132', NULL, NULL, NULL, NULL, 'active', '2026-02-18 01:37:23.563132'),
(33, 'A', NULL, NULL, '2026-02-18 01:39:58.019107', NULL, NULL, NULL, NULL, 'active', '2026-02-18 01:39:58.019107'),
(34, '708, 7TH FLOOR, PALM SPRING CENTRE PREMISES CO-OP SOC. LTD.,LINK ROAD, MALAD WEST, MUMBAI. 400-064.', '', '', '2026-02-18 16:59:50.330748', NULL, NULL, NULL, NULL, 'active', '2026-02-18 16:59:50.330748'),
(35, 'AAAAAA', NULL, NULL, '2026-02-18 17:47:50.288496', NULL, NULL, NULL, NULL, 'active', '2026-02-18 17:47:50.288496'),
(36, 'ZZZZZ', NULL, NULL, '2026-02-19 15:11:58.445881', NULL, NULL, NULL, NULL, 'active', '2026-02-19 15:11:58.445881'),
(37, '2', NULL, NULL, '2026-02-19 15:12:35.517695', NULL, NULL, NULL, NULL, 'active', '2026-02-19 15:12:35.517695'),
(38, '2', NULL, NULL, '2026-02-19 15:12:39.499244', NULL, NULL, NULL, NULL, 'active', '2026-02-19 15:12:39.499244'),
(39, '2', NULL, NULL, '2026-02-19 15:14:30.032343', NULL, NULL, NULL, NULL, 'active', '2026-02-19 15:14:30.032343'),
(40, 'A', NULL, NULL, '2026-02-19 15:14:48.117324', NULL, NULL, NULL, NULL, 'active', '2026-02-19 15:14:48.117324'),
(41, 'A', NULL, NULL, '2026-02-20 18:39:29.463085', NULL, NULL, NULL, NULL, 'active', '2026-02-20 18:39:29.463085'),
(42, 'a', NULL, NULL, '2026-02-20 18:39:41.576494', NULL, NULL, NULL, NULL, 'active', '2026-02-20 18:39:41.576494'),
(43, 'A', NULL, NULL, '2026-02-22 15:06:37.526478', NULL, NULL, NULL, NULL, 'active', '2026-02-22 15:06:37.526478'),
(44, 'A', NULL, NULL, '2026-02-22 15:06:45.167189', NULL, NULL, NULL, NULL, 'active', '2026-02-22 15:06:45.167189');

-- =====================================================
-- Table: vendor_order (0 records)
-- =====================================================

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
);

-- =====================================================
-- Table: vendor_order_line_item (0 records)
-- =====================================================

DROP TABLE IF EXISTS "vendor_order_line_item" CASCADE;

CREATE TABLE "vendor_order_line_item" (
    "id" bigint DEFAULT nextval('vendor_order_line_item_id_seq'::regclass) NOT NULL,
    "vendor_order_id" bigint NOT NULL,
    "item_description" character varying,
    "quantity" numeric,
    "unit_price" numeric,
    "amount" numeric,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);

-- =====================================================
-- Table: vendor_payment (0 records)
-- =====================================================

DROP TABLE IF EXISTS "vendor_payment" CASCADE;

CREATE TABLE "vendor_payment" (
    "id" bigint DEFAULT nextval('vendor_payment_id_seq'::regclass) NOT NULL,
    "vendor_id" bigint NOT NULL,
    "vendor_order_id" bigint,
    "amount" numeric,
    "payment_date" date,
    "status" character varying DEFAULT 'PENDING'::character varying,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
);


-- =====================================================
-- INDEXES
-- =====================================================

CREATE UNIQUE INDEX upload_session_pkey ON "Finances".upload_session USING btree (id);
CREATE UNIQUE INDEX upload_session_session_id_key ON "Finances".upload_session USING btree (session_id);
CREATE INDEX idx_upload_session_expires_at ON "Finances".upload_session USING btree (expires_at);
CREATE INDEX idx_upload_session_status ON "Finances".upload_session USING btree (status);
CREATE INDEX idx_upload_session_session_id ON "Finances".upload_session USING btree (session_id);
CREATE UNIQUE INDEX upload_file_pkey ON "Finances".upload_file USING btree (id);
CREATE INDEX idx_upload_file_session_id ON "Finances".upload_file USING btree (session_id);
CREATE INDEX idx_upload_file_po_number ON "Finances".upload_file USING btree (po_number);
CREATE INDEX idx_upload_file_upload_timestamp ON "Finances".upload_file USING btree (upload_timestamp);
CREATE INDEX idx_upload_file_status ON "Finances".upload_file USING btree (status);
CREATE UNIQUE INDEX upload_stats_pkey ON "Finances".upload_stats USING btree (id);
CREATE UNIQUE INDEX upload_stats_session_id_key ON "Finances".upload_stats USING btree (session_id);
CREATE INDEX idx_upload_stats_session_id ON "Finances".upload_stats USING btree (session_id);
CREATE UNIQUE INDEX project_pkey ON "Finances".project USING btree (id);
CREATE INDEX idx_project_location ON "Finances".project USING btree (city, state);
CREATE UNIQUE INDEX vendor_payment_pkey ON "Finances".vendor_payment USING btree (id);
CREATE UNIQUE INDEX payment_vendor_link_pkey ON "Finances".payment_vendor_link USING btree (id);
CREATE UNIQUE INDEX payment_vendor_link_vendor_payment_id_vendor_order_id_key ON "Finances".payment_vendor_link USING btree (vendor_payment_id, vendor_order_id);
CREATE UNIQUE INDEX po_project_mapping_pkey ON "Finances".po_project_mapping USING btree (id);
CREATE UNIQUE INDEX po_project_mapping_client_po_id_project_id_key ON "Finances".po_project_mapping USING btree (client_po_id, project_id);
CREATE UNIQUE INDEX project_document_pkey ON "Finances".project_document USING btree (id);
CREATE UNIQUE INDEX vendor_order_pkey ON "Finances".vendor_order USING btree (id);
CREATE UNIQUE INDEX billing_po_pkey ON "Finances".billing_po USING btree (id);
CREATE UNIQUE INDEX billing_po_po_number_key ON "Finances".billing_po USING btree (po_number);
CREATE UNIQUE INDEX client_payment_pkey ON "Finances".client_payment USING btree (id);
CREATE UNIQUE INDEX vendor_order_line_item_pkey ON "Finances".vendor_order_line_item USING btree (id);
CREATE UNIQUE INDEX billing_po_line_item_pkey ON "Finances".billing_po_line_item USING btree (id);
CREATE UNIQUE INDEX user_pkey ON "Finances"."user" USING btree (id);
CREATE UNIQUE INDEX user_username_key ON "Finances"."user" USING btree (username);
CREATE UNIQUE INDEX user_email_key ON "Finances"."user" USING btree (email);
CREATE INDEX idx_user_username ON "Finances"."user" USING btree (username);
CREATE INDEX idx_user_email ON "Finances"."user" USING btree (email);
CREATE UNIQUE INDEX client_po_pkey ON "Finances".client_po USING btree (id);
CREATE UNIQUE INDEX client_po_po_number_key ON "Finances".client_po USING btree (po_number);
CREATE INDEX idx_client_po_project_id ON "Finances".client_po USING btree (project_id);
CREATE INDEX idx_client_po_parent_id ON "Finances".client_po USING btree (parent_po_id);
CREATE INDEX idx_client_po_type ON "Finances".client_po USING btree (po_type);
CREATE INDEX idx_client_po_vendor_id ON "Finances".client_po USING btree (vendor_id);
CREATE INDEX idx_client_po_site_id ON "Finances".client_po USING btree (site_id);
CREATE INDEX idx_client_po_store_id ON "Finances".client_po USING btree (store_id);
CREATE INDEX idx_client_po_client_store ON "Finances".client_po USING btree (client_id, store_id);
CREATE UNIQUE INDEX client_po_line_item_pkey ON "Finances".client_po_line_item USING btree (id);
CREATE INDEX idx_po_line_item_client_po_id ON "Finances".client_po_line_item USING btree (client_po_id);
CREATE INDEX idx_client_po_line_item_hsn ON "Finances".client_po_line_item USING btree (hsn_code);
CREATE UNIQUE INDEX vendor_pkey ON "Finances".vendor USING btree (id);
CREATE INDEX idx_vendor_gstin ON "Finances".vendor USING btree (gstin);
CREATE UNIQUE INDEX site_pkey ON "Finances".site USING btree (id);
CREATE UNIQUE INDEX site_store_id_key ON "Finances".site USING btree (store_id);
CREATE INDEX idx_site_store_id ON "Finances".site USING btree (store_id);
CREATE UNIQUE INDEX client_pkey ON "Finances".client USING btree (id);

-- =====================================================
-- EXPORT COMPLETE
-- Total tables: 19
-- Total records: 196
-- =====================================================
