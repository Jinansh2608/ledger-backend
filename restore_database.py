#!/usr/bin/env python3
"""
Restore Nexgen ERP Database from Backup

This script simplifies the restoration process by handling:
1. Database creation if needed
2. Schema creation
3. Full data restoration
4. Verification of record counts

Usage:
    python restore_database.py [backup_file] [--host] [--port] [--user] [--password]

Example:
    python restore_database.py Nexgen_erp_backup_20260222_230959.sql
    python restore_database.py Nexgen_erp_backup_20260222_230959.sql --host localhost --user postgres
"""

import argparse
import glob
import sys
import os
import subprocess
from pathlib import Path

def find_backup_file(filename=None):
    """Find the backup file to restore."""
    if filename and os.path.exists(filename):
        return filename
    
    # Search for backup files
    backups = sorted(glob.glob("Nexgen_erp_backup_*.sql"), reverse=True)
    if backups:
        print(f"Found backup files: {backups}")
        return backups[0]
    
    raise FileNotFoundError("No backup file found. Specify filename or place in current directory.")

def restore_database(backup_file, host="localhost", port=5432, user="postgres", password=None, db_name="Nexgen_erp"):
    """Restore the database from backup."""
    
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")
    
    print(f"\n{'='*60}")
    print(f"Database Restoration Tool")
    print(f"{'='*60}")
    print(f"\nBackup File: {backup_file}")
    print(f"Host: {host}:{port}")
    print(f"User: {user}")
    print(f"Database: {db_name}")
    print(f"{'='*60}\n")
    
    # Set environment
    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password
    
    try:
        # Step 1: Create database if needed
        print("[1/3] Creating database...")
        subprocess.run(
            ["createdb", "-h", host, "-p", str(port), "-U", user, db_name],
            capture_output=True,
            env=env,
            check=False  # Don't fail if database exists
        )
        print("     Database ready")
        
        # Step 2: Create schema
        print("[2/3] Creating schema...")
        subprocess.run(
            ["psql", "-h", host, "-p", str(port), "-U", user, "-d", db_name, "-c", 'CREATE SCHEMA IF NOT EXISTS "Finances";'],
            env=env,
            check=True
        )
        print("     Schema ready")
        
        # Step 3: Restore data
        print("[3/3] Restoring data from backup...")
        with open(backup_file, 'r') as f:
            subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", user, "-d", db_name],
                stdin=f,
                env=env,
                check=True
            )
        print("     Data restored")
        
        print(f"\n{'='*60}")
        print("✅ Restoration Complete!")
        print(f"{'='*60}\n")
        
        # Step 4: Verify
        verify_restoration(host, port, user, password, db_name)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Restoration failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def verify_restoration(host, port, user, password, db_name):
    """Verify the restoration was successful."""
    
    print("[Verification] Checking record counts...")
    
    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password
    
    # Query to count records in each table
    queries = [
        ("client", "SELECT COUNT(*) FROM \"Finances\".client"),
        ("vendor", "SELECT COUNT(*) FROM \"Finances\".vendor"),
        ("user", "SELECT COUNT(*) FROM \"Finances\".\"user\""),
        ("client_po", "SELECT COUNT(*) FROM \"Finances\".client_po"),
        ("client_po_line_item", "SELECT COUNT(*) FROM \"Finances\".client_po_line_item"),
        ("site", "SELECT COUNT(*) FROM \"Finances\".site"),
        ("upload_file", "SELECT COUNT(*) FROM \"Finances\".upload_file"),
        ("upload_session", "SELECT COUNT(*) FROM \"Finances\".upload_session"),
    ]
    
    total_records = 0
    
    for table_name, query in queries:
        try:
            result = subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", user, "-d", db_name, 
                 "-t", "-c", query],
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            count = int(result.stdout.strip())
            total_records += count
            status = "✓" if count > 0 else "-"
            print(f"  {status} {table_name}: {count} records")
        except Exception as e:
            print(f"  ✗ {table_name}: Error - {e}")
    
    print(f"\nTotal: {total_records} records across all tables")
    print("\n✅ Verification complete!")

def main():
    parser = argparse.ArgumentParser(
        description="Restore Nexgen ERP Database from Backup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python restore_database.py
  python restore_database.py Nexgen_erp_backup_20260222_230959.sql
  python restore_database.py backup.sql --host db.example.com --user admin --password secret
        """
    )
    
    parser.add_argument(
        "backup_file",
        nargs="?",
        help="Backup file to restore (auto-detects if not provided)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Database host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5432,
        help="Database port (default: 5432)"
    )
    parser.add_argument(
        "--user",
        default="postgres",
        help="Database user (default: postgres)"
    )
    parser.add_argument(
        "--password",
        help="Database password (prompted if not provided)"
    )
    parser.add_argument(
        "--dbname",
        default="Nexgen_erp",
        help="Database name (default: Nexgen_erp)"
    )
    
    args = parser.parse_args()
    
    # Find backup file
    try:
        backup_file = find_backup_file(args.backup_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Restore database
    restore_database(
        backup_file,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        db_name=args.dbname
    )

if __name__ == "__main__":
    main()
