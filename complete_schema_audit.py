#!/usr/bin/env python3
"""
Complete schema audit showing all table columns and data types
"""
from app.database import get_db
from collections import defaultdict

conn = get_db()
try:
    with conn.cursor() as cur:
        # Get list of all tables
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY tablename
        """)
        tables = [row['tablename'] for row in cur.fetchall()]
        
        print(f"{'='*100}")
        print(f"COMPLETE DATABASE SCHEMA AUDIT - {len(tables)} Tables")
        print(f"{'='*100}\n")
        
        schema_report = {}
        
        for table in tables:
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            
            columns = cur.fetchall()
            schema_report[table] = columns
            
            print(f"TABLE: {table.upper()}")
            print(f"Columns: {len(columns)}")
            for col in columns:
                col_info = f"  • {col['column_name']}: {col['data_type']}"
                if col['column_default']:
                    col_info += f" (default: {col['column_default']})"
                if col['is_nullable'] == 'NO':
                    col_info += " [NOT NULL]"
                print(col_info)
            print()
        
        # Create a summary
        print(f"\n{'='*100}")
        print("SUMMARY")
        print(f"{'='*100}")
        
        # Tables with line items
        print("\n📦 LINE ITEM TABLES:")
        for table in ['client_po_line_item', 'billing_po_line_item', 'vendor_order_line_item']:
            if table in schema_report:
                cols = [c['column_name'] for c in schema_report[table]]
                print(f"  {table}: {', '.join(cols)}")
        
        # Key junction tables
        print("\n🔗 KEY JUNCTION/MAPPING TABLES:")
        for table in ['po_project_mapping', 'payment_vendor_link', 'user_role']:
            if table in schema_report:
                cols = [c['column_name'] for c in schema_report[table]]
                print(f"  {table}: {', '.join(cols)}")
        
        # Core entity tables
        print("\n📋 CORE ENTITY TABLES:")
        for table in ['project', 'client_po', 'billing_po', 'vendor_order', 'client', 'vendor']:
            if table in schema_report:
                cols = [c['column_name'] for c in schema_report[table]]
                print(f"  {table}: {', '.join(cols)}")
        
        print(f"\n{'='*100}\n")
        
finally:
    conn.close()
