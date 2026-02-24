#!/usr/bin/env python3
"""
Complete Database Schema Audit & Sync Check
Compares actual schema with code expectations
"""

from app.database import get_db
import json


def get_all_tables():
    """Get all tables in database"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            return tables
    finally:
        conn.close()


def get_table_schema(table_name):
    """Get columns for a table"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cur.fetchall()
            return columns
    finally:
        conn.close()


def get_table_fks(table_name):
    """Get foreign keys for a table"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    constraint_name,
                    column_name,
                    referenced_table_name,
                    referenced_column_name
                FROM information_schema.referential_constraints rc
                JOIN information_schema.key_column_usage kcu 
                    ON rc.constraint_name = kcu.constraint_name
                WHERE kcu.table_name = %s
            """, (table_name,))
            
            fks = cur.fetchall()
            return fks
    finally:
        conn.close()


def main():
    print("\n" + "="*100)
    print("🔍 COMPLETE DATABASE SCHEMA AUDIT")
    print("="*100)
    
    tables = get_all_tables()
    print(f"\n📊 Found {len(tables)} tables:\n")
    
    schema_report = {}
    
    for table in tables:
        print(f"\n{'─'*100}")
        print(f"📋 TABLE: {table.upper()}")
        print(f"{'─'*100}")
        
        columns = get_table_schema(table)
        
        if not columns:
            print(f"  ⚠️  No columns found!")
            continue
        
        schema_report[table] = []
        
        print(f"\n  Columns ({len(columns)}):")
        for col in columns:
            col_name = col['column_name']
            col_type = col['data_type']
            nullable = "✅ NULL" if col['is_nullable'] == 'YES' else "❌ NOT NULL"
            default = f"(default: {col['column_default']})" if col['column_default'] else ""
            
            print(f"    • {col_name:30} {col_type:20} {nullable:15} {default}")
            schema_report[table].append({
                'name': col_name,
                'type': col_type,
                'nullable': col['is_nullable'],
                'default': col['column_default']
            })
    
    # Save schema report
    with open('SCHEMA_AUDIT_REPORT.json', 'w') as f:
        json.dump(schema_report, f, indent=2)
    
    print("\n" + "="*100)
    print("✅ SCHEMA AUDIT COMPLETE")
    print("="*100)
    print(f"\n📁 Saved schema report to: SCHEMA_AUDIT_REPORT.json")
    
    return schema_report


if __name__ == "__main__":
    main()
