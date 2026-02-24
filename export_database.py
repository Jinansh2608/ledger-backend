#!/usr/bin/env python3
"""
Export Nexgen_erp database to SQL file for hosting
Creates a complete replica with schema and data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'Nexgen_erp',
    'user': 'postgres',
    'password': 'toor'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def export_database():
    """Export entire database to SQL file"""
    print("\n" + "="*80)
    print("  📦 DATABASE EXPORT - Nexgen_erp")
    print("="*80 + "\n")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Set search path
    cur.execute('SET search_path TO "Finances";')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Nexgen_erp_backup_{timestamp}.sql"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("-- =====================================================\n")
            f.write("-- NEXGEN ERP DATABASE BACKUP\n")
            f.write(f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- Database: Nexgen_erp\n")
            f.write("-- Schema: Finances\n")
            f.write("-- Complete replica with schema and data\n")
            f.write("-- =====================================================\n\n")
            
            f.write("-- Set search path\n")
            f.write('SET search_path TO "Finances";\n\n')
            
            # Get all tables
            cur.execute('''
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'Finances'
                ORDER BY table_name
            ''')
            
            tables = [row['table_name'] for row in cur.fetchall()]
            print(f"✅ Found {len(tables)} tables to export\n")
            
            # Export each table
            total_records = 0
            
            for table in tables:
                print(f"  📋 Exporting {table}...", end=" ")
                
                # Get table structure
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'Finances' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cur.fetchall()
                column_names = [col['column_name'] for col in columns]
                
                # Get table data
                cur.execute(f'SELECT * FROM "Finances"."{table}"')
                rows = cur.fetchall()
                record_count = len(rows)
                total_records += record_count
                
                # Write table comment
                f.write(f"-- =====================================================\n")
                f.write(f"-- Table: {table} ({record_count} records)\n")
                f.write(f"-- =====================================================\n\n")
                
                # Write drop and create statements
                f.write(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;\n\n")
                
                f.write(f"CREATE TABLE \"{table}\" (\n")
                for col in columns:
                    col_def = f'    \"{col["column_name"]}\" {col["data_type"]}'
                    
                    if col['column_default']:
                        col_def += f" DEFAULT {col['column_default']}"
                    
                    if col['is_nullable'] == 'NO':
                        col_def += " NOT NULL"
                    
                    col_def += ",\n"
                    f.write(col_def)
                
                # Remove last comma and close
                f.seek(f.tell() - 2)
                f.write("\n);\n\n")
                
                # Write data
                if rows:
                    # Write INSERT statements
                    f.write(f"INSERT INTO \"{table}\" ({', '.join([f'\"{col}\"' for col in column_names])}) VALUES\n")
                    
                    for idx, row in enumerate(rows):
                        values = []
                        for col_name in column_names:
                            val = row[col_name]
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped = val.replace("'", "''")
                                values.append(f"'{escaped}'")
                            elif isinstance(val, bool):
                                values.append("true" if val else "false")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                # For dates and other types
                                values.append(f"'{str(val)}'")
                        
                        line = f"({', '.join(values)})"
                        if idx < len(rows) - 1:
                            line += ","
                        else:
                            line += ";"
                        
                        f.write(line + "\n")
                    
                    f.write("\n")
                
                print(f"✅ ({record_count} records)")
            
            # Write indexes
            f.write("\n-- =====================================================\n")
            f.write("-- INDEXES\n")
            f.write("-- =====================================================\n\n")
            
            try:
                cur.execute("""
                    SELECT indexname, indexdef FROM pg_indexes
                    WHERE schemaname = 'Finances'
                    AND tablename NOT LIKE 'pg_%'
                """)
                
                indexes = cur.fetchall()
                for idx in indexes:
                    f.write(f"{idx['indexdef']};\n")
            except:
                pass
            
            # Add footer
            f.write("\n-- =====================================================\n")
            f.write("-- EXPORT COMPLETE\n")
            f.write(f"-- Total tables: {len(tables)}\n")
            f.write(f"-- Total records: {total_records}\n")
            f.write("-- =====================================================\n")
        
        # File size
        file_size = os.path.getsize(filename)
        size_mb = file_size / (1024 * 1024)
        
        print("\n" + "="*80)
        print(f"  ✅ EXPORT SUCCESSFUL")
        print("="*80)
        print(f"\n  📄 File: {filename}")
        print(f"  📊 Size: {size_mb:.2f} MB ({file_size:,} bytes)")
        print(f"  📋 Tables: {len(tables)}")
        print(f"  📝 Records: {total_records}")
        print(f"  ⏰ Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("  ✨ Ready for hosting!\n")
        
        return filename
        
    except Exception as e:
        print(f"\n❌ Export failed: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    try:
        export_database()
    except KeyboardInterrupt:
        print("\n\n⏹️  Export cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
