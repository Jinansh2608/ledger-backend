# Nexgen ERP Database Backup

## Overview
This is a complete SQL dump of the Nexgen_erp database for hosting purposes. It includes:
- **19 tables** - Complete schema with all tables
- **196 records** - Current data state
- **Schema + Data** - Ready for production deployment

## File Information
- **Filename**: `Nexgen_erp_backup_YYYYMMDD_HHMMSS.sql`
- **Size**: ~64 KB
- **Format**: PostgreSQL SQL dump
- **Schema**: Finances

## Restore Instructions

### Prerequisites
- PostgreSQL 12+ installed
- `psql` command available
- Access to a database server
- User with CREATE DATABASE permissions

### Option 1: Full Database Restore (Recommended)

```bash
# Create the database (if it doesn't exist)
createdb -U postgres Nexgen_erp

# Create the schema
psql -U postgres -d Nexgen_erp -c 'CREATE SCHEMA "Finances";'

# Restore the backup
psql -U postgres -d Nexgen_erp -f Nexgen_erp_backup_YYYYMMDD_HHMMSS.sql
```

### Option 2: Restore to Existing Database

```bash
# If you already have the database and schema
psql -U postgres -d Nexgen_erp -f Nexgen_erp_backup_YYYYMMDD_HHMMSS.sql
```

### Option 3: Remote Server Restore

```bash
# Via SSH to remote server
ssh user@remote_host "psql -U postgres -d Nexgen_erp -f /path/to/backup.sql"

# Or via direct connection
psql -h remote_host -U postgres -d Nexgen_erp -f Nexgen_erp_backup_YYYYMMDD_HHMMSS.sql
```

## Verify Restoration

After restoration, verify the data:

```sql
-- Connect to the database
psql -U postgres -d Nexgen_erp

-- Set search path
SET search_path TO "Finances";

-- Check tables
\dt

-- Count records
SELECT 'client' as table_name, COUNT(*) FROM client
UNION ALL
SELECT 'vendor', COUNT(*) FROM vendor
UNION ALL
SELECT 'client_po', COUNT(*) FROM client_po
UNION ALL
SELECT 'client_po_line_item', COUNT(*) FROM client_po_line_item
UNION ALL
SELECT 'upload_file', COUNT(*) FROM upload_file
...
```

## Database Structure

### Core Tables
- **client** - Client information (2 records)
- **vendor** - Vendor details (13 records)
- **user** - User accounts (5 records)

### Project Management
- **project** - Projects (0 records - cleared)
- **site** - Sites (3 records)
- **po_project_mapping** - PO to project mapping (0 records)

### Purchase Orders
- **client_po** - Client POs (4 records)
- **client_po_line_item** - Line items (156 records)
- **billing_po** - Billing POs (0 records)
- **billing_po_line_item** - Billing line items (0 records)

### Orders & Payments
- **vendor_order** - Vendor orders (0 records)
- **vendor_order_line_item** - Vendor order items (0 records)
- **client_payment** - Client payments (3 records)
- **vendor_payment** - Vendor payments (0 records)
- **payment_vendor_link** - Payment links (0 records)

### Documents & Files
- **upload_file** - Uploaded files (5 records)
- **upload_session** - Upload sessions (5 records)
- **upload_stats** - Upload statistics (0 records)
- **project_document** - Project documents (0 records)

## Configuration

Update your `.env` or database configuration after restoration:

```python
# app/config.py or environment variables
DB_HOST = "your-hosting-server.com"
DB_PORT = 5432
DB_NAME = "Nexgen_erp"
DB_USER = "postgres"
DB_PASSWORD = "your-secure-password"
```

## Backup Schedule

For production, create regular backups:

```bash
# Daily backup
0 2 * * * /usr/bin/python3 /path/to/export_database.py

# Or using pg_dump directly
0 2 * * * pg_dump -U postgres -h localhost Nexgen_erp > /backups/Nexgen_erp_$(date +\%Y\%m\%d).sql
```

## Recovery Plan

In case of data loss:

1. **Stop the application** - Prevent further changes
2. **Backup current state** - Create emergency backup of corrupted database
3. **Restore from this file** - Use instructions above
4. **Verify data integrity** - Check critical tables and records
5. **Restart application** - Redeploy and test

## Important Notes

- ⚠️ This backup was created on **2026-02-22 23:09:59**
- ⚠️ All project data has been cleared (as per cleanup script)
- ⚠️ Contains 2 clients and 13 vendors
- ✅ Contains 4 active POs with 156 line items
- ✅ Contains 3 client payments
- ✅ Contains 5 uploaded files
- ✅ Contains 5 user accounts

## Support

For issues during restoration:

1. Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql.log`
2. Verify database permissions: `psql -l`
3. Check schema: `\dn` in psql
4. Contact: DevOps team

## Next Steps

After successful restoration:

1. Update API configuration to connect to new database
2. Run migrations if any: `python manage.py migrate`
3. Test API endpoints against restored data
4. Monitor logs for any connection issues
5. Perform smoke tests on critical features

---

**Backup Tool**: `export_database.py`  
**Generator**: Nexgen Finance Backend  
**Version**: 1.0  
