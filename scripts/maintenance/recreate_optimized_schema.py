#!/usr/bin/env python3
"""
Create Optimized Schema - Minimal Design
Recreates removed tables with only essential columns
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "Finances";')
    return conn

def create_optimized_schema():
    """Create optimized tables with minimal necessary columns"""
    print("\n" + "="*70)
    print("CREATING OPTIMIZED SCHEMA")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. BILLING_PO - Minimal design
    print("📋 Creating: billing_po")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS billing_po (
            id BIGSERIAL PRIMARY KEY,
            client_id BIGINT NOT NULL REFERENCES client(id),
            po_number VARCHAR(100) NOT NULL UNIQUE,
            amount NUMERIC(15, 2),
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, client_id, po_number, amount, status, created_at")
    
    # 2. VENDOR_ORDER - Minimal design
    print("📋 Creating: vendor_order")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendor_order (
            id BIGSERIAL PRIMARY KEY,
            vendor_id BIGINT NOT NULL REFERENCES vendor(id),
            po_number VARCHAR(100) NOT NULL,
            amount NUMERIC(15, 2),
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, vendor_id, po_number, amount, status, created_at")
    
    # 3. VENDOR_PAYMENT - Minimal design
    print("📋 Creating: vendor_payment")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendor_payment (
            id BIGSERIAL PRIMARY KEY,
            vendor_id BIGINT NOT NULL REFERENCES vendor(id),
            vendor_order_id BIGINT REFERENCES vendor_order(id),
            amount NUMERIC(15, 2),
            payment_date DATE,
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, vendor_id, vendor_order_id, amount, payment_date, status, created_at")
    
    # 4. CLIENT_PAYMENT - Minimal design
    print("📋 Creating: client_payment")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_payment (
            id BIGSERIAL PRIMARY KEY,
            client_id BIGINT NOT NULL REFERENCES client(id),
            client_po_id BIGINT REFERENCES client_po(id),
            amount NUMERIC(15, 2),
            payment_date DATE,
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, client_id, client_po_id, amount, payment_date, status, created_at")
    
    # 5. PAYMENT_VENDOR_LINK - Minimal design (junction table)
    print("📋 Creating: payment_vendor_link")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_vendor_link (
            id BIGSERIAL PRIMARY KEY,
            vendor_payment_id BIGINT NOT NULL REFERENCES vendor_payment(id) ON DELETE CASCADE,
            vendor_order_id BIGINT NOT NULL REFERENCES vendor_order(id) ON DELETE CASCADE,
            amount_allocated NUMERIC(15, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vendor_payment_id, vendor_order_id)
        );
    """)
    print("   ✅ Created with columns: id, vendor_payment_id, vendor_order_id, amount_allocated, created_at")
    
    # 6. PO_PROJECT_MAPPING - Minimal design (already has project_id in client_po, but keep for reference)
    print("📋 Creating: po_project_mapping")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS po_project_mapping (
            id BIGSERIAL PRIMARY KEY,
            client_po_id BIGINT NOT NULL REFERENCES client_po(id) ON DELETE CASCADE,
            project_id BIGINT NOT NULL REFERENCES project(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(client_po_id, project_id)
        );
    """)
    print("   ✅ Created with columns: id, client_po_id, project_id, created_at")
    
    # 7. PROJECT_DOCUMENT - Minimal design
    print("📋 Creating: project_document")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_document (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
            document_name VARCHAR(255),
            document_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, project_id, document_name, document_path, created_at")
    
    # 8. UPLOAD_STATS - Minimal design (computed stats)
    print("📋 Creating: upload_stats")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS upload_stats (
            id BIGSERIAL PRIMARY KEY,
            total_files BIGINT DEFAULT 0,
            total_sessions BIGINT DEFAULT 0,
            total_size_bytes BIGINT DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, total_files, total_sessions, total_size_bytes, last_updated")
    
    # 9. BILLING_PO_LINE_ITEM - Minimal design
    print("📋 Creating: billing_po_line_item")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS billing_po_line_item (
            id BIGSERIAL PRIMARY KEY,
            billing_po_id BIGINT NOT NULL REFERENCES billing_po(id) ON DELETE CASCADE,
            item_description VARCHAR(500),
            quantity NUMERIC(10, 2),
            unit_price NUMERIC(15, 2),
            amount NUMERIC(15, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, billing_po_id, item_description, quantity, unit_price, amount, created_at")
    
    # 10. VENDOR_ORDER_LINE_ITEM - Minimal design
    print("📋 Creating: vendor_order_line_item")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendor_order_line_item (
            id BIGSERIAL PRIMARY KEY,
            vendor_order_id BIGINT NOT NULL REFERENCES vendor_order(id) ON DELETE CASCADE,
            item_description VARCHAR(500),
            quantity NUMERIC(10, 2),
            unit_price NUMERIC(15, 2),
            amount NUMERIC(15, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ Created with columns: id, vendor_order_id, item_description, quantity, unit_price, amount, created_at")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("✨ OPTIMIZED SCHEMA CREATED SUCCESSFULLY")
    print("="*70)

def show_schema_summary():
    """Show the new optimized schema"""
    print("\n" + "="*70)
    print("OPTIMIZED SCHEMA SUMMARY")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    tables_info = {
        "billing_po": "Billing Purchase Orders",
        "billing_po_line_item": "Line items for billing POs",
        "vendor_order": "Vendor purchase orders",
        "vendor_order_line_item": "Line items for vendor orders",
        "vendor_payment": "Vendor payment tracking",
        "client_payment": "Client payment tracking",
        "payment_vendor_link": "Link vendor payments to orders",
        "po_project_mapping": "Map POs to projects",
        "project_document": "Project documents",
        "upload_stats": "Upload statistics"
    }
    
    for table, description in tables_info.items():
        try:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            cnt = cur.fetchone()['cnt']
            
            # Get columns
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position;
            """)
            columns = [f"{row['column_name']}" for row in cur.fetchall()]
            
            print(f"📊 {table}")
            print(f"   Description: {description}")
            print(f"   Rows: {cnt}")
            print(f"   Columns: {', '.join(columns)}")
            print()
        except Exception as e:
            print(f"   ⚠️  Error: {e}\n")
    
    conn.close()

def main():
    try:
        create_optimized_schema()
        show_schema_summary()
        
        print("\n✅ SCHEMA OPTIMIZATION COMPLETE")
        print("\n📌 KEY FEATURES:")
        print("   • Minimal necessary columns only")
        print("   • Proper referential integrity (FK constraints)")
        print("   • CASCADE deletes for data consistency")
        print("   • Ready for business logic")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
