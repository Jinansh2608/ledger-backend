# Hosting Deployment Checklist

## Pre-Deployment (Local Development)
- [x] API running successfully on `http://localhost:8000`
- [x] All endpoints tested and working
- [x] Database backup created: `Nexgen_erp_backup_YYYYMMDD_HHMMSS.sql`
- [x] Backup verified: 19 tables, 196 records, ~64 KB
- [x] All authentication working with bcrypt password hashing
- [x] Line items endpoints complete with validation
- [x] Client-specific PO bundling logic implemented
- [x] Database connection pooling configured

---

## Database Deployment
- [ ] **Environment Setup**
  - [ ] PostgreSQL 12+ installed on hosting server
  - [ ] PostgreSQL service running and accessible
  - [ ] Database user created with proper permissions
  - [ ] Network access configured (firewall rules, security groups)

- [ ] **Database Restoration**
  - [ ] Copy backup file to hosting server: `Nexgen_erp_backup_*.sql`
  - [ ] Run: `psql -U postgres -d Nexgen_erp -f Nexgen_erp_backup_*.sql`
  - [ ] Or use restoration script: `python restore_database.py backup.sql --host <host> --user <user>`
  - [ ] Verify restoration successful (check output for errors)

- [ ] **Verification**
  - [ ] Connect to database: `psql -U postgres -d Nexgen_erp`
  - [ ] Set schema: `SET search_path TO "Finances";`
  - [ ] List tables: `\dt`
  - [ ] Check record counts:
    ```sql
    SELECT COUNT(*) FROM client;  -- Should be 2
    SELECT COUNT(*) FROM vendor;  -- Should be 13
    SELECT COUNT(*) FROM client_po;  -- Should be 4
    SELECT COUNT(*) FROM client_po_line_item;  -- Should be 156
    ```

---

## Application Deployment

### Environment Configuration
- [ ] **Create `.env` file with hosting credentials**
  ```
  # Database Configuration
  DB_HOST=your-hosting-db-server.com
  DB_PORT=5432
  DB_NAME=Nexgen_erp
  DB_USER=postgres
  DB_PASSWORD=your-secure-password
  
  # API Configuration
  API_HOST=your-api-domain.com
  API_PORT=8000
  DEBUG=False
  ENVIRONMENT=production
  
  # Security
  SECRET_KEY=your-secret-key-here
  JWT_EXPIRY=3600
  ```

- [ ] **Update configuration files**
  - [ ] `app/config.py` - Database connection string
  - [ ] Environment variables in hosting platform
  - [ ] SSL/TLS certificates if applicable

### Backend Deployment
- [ ] **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Test API locally with production database**
  ```bash
  python run.py
  ```

- [ ] **Deploy to hosting platform**
  - [ ] Push code to repository
  - [ ] Configure CI/CD pipeline
  - [ ] Deploy via hosting platform (Heroku, AWS, Azure, etc.)

- [ ] **Start API service**
  ```bash
  # Using Uvicorn directly
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  
  # Or with Gunicorn (production)
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
  ```

---

## API Testing

### Health Check
- [ ] **Endpoint**: `GET http://your-api-domain.com/health` (or `/docs`)
- [ ] **Expected**: API response without errors
- [ ] **Command**:
  ```bash
  curl http://your-api-domain.com/health
  ```

### Authentication Testing
- [ ] **Test user login**
  ```bash
  curl -X POST http://your-api-domain.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "user", "password": "password"}'
  ```

- [ ] **Verify JWT token returned**
- [ ] **Test protected endpoint with token**
  ```bash
  curl -H "Authorization: Bearer YOUR_TOKEN" \
    http://your-api-domain.com/api/protected-endpoint
  ```

### Critical Endpoints
- [ ] **GET** `/po/list` - List all POs
- [ ] **GET** `/po/aggregated/by-store` - Aggregated POs by store
- [ ] **GET** `/po/{po_id}/line-items` - Get line items
- [ ] **POST** `/po/{po_id}/line-items` - Add line item
- [ ] **GET** `/client` - List clients
- [ ] **GET** `/vendor` - List vendors

---

## Monitoring & Maintenance

### Logging
- [ ] **Configure log rotation**
  - [ ] Max log file size: 100 MB
  - [ ] Retention: 30 days
  - [ ] Location: `/var/log/nexgen-api/`

- [ ] **Enable error tracking**
  - [ ] Sentry or similar error monitoring
  - [ ] CloudWatch or similar log aggregation

### Performance Monitoring
- [ ] **Set up performance monitoring**
  - [ ] Response time tracking
  - [ ] Database query performance
  - [ ] CPU/memory usage alerts

- [ ] **Database monitoring**
  - [ ] Connection pool status
  - [ ] Query logs
  - [ ] Backup verification

### Alerts
- [ ] **Configure alerts for:**
  - [ ] API service down (HTTP 500+ errors)
  - [ ] Database connection failure
  - [ ] High response times (> 5 seconds)
  - [ ] Disk space running low
  - [ ] Backup failures

---

## Backup & Disaster Recovery

### Automated Backups
- [ ] **Set up daily database backups**
  ```bash
  # Cron job (runs at 2 AM daily)
  0 2 * * * /usr/bin/python3 /path/to/export_database.py
  ```

- [ ] **Configure backup retention**
  - [ ] Daily backups: Keep 7 days
  - [ ] Weekly backups: Keep 4 weeks
  - [ ] Monthly backups: Keep 1 year

### Disaster Recovery Plan
- [ ] **Document recovery procedures**
- [ ] **Test recovery process** - Restore backup to test environment
- [ ] **Estimate RTO/RPO**
  - [ ] Recovery Time Objective (RTO)
  - [ ] Recovery Point Objective (RPO)

---

## Security Hardening

### Database Security
- [ ] **Database user permissions**
  - [ ] Limit to necessary tables only
  - [ ] No superuser privileges
  - [ ] Read-only users for analytics/reports

- [ ] **Network security**
  - [ ] Restrict database access to API server only
  - [ ] Use SSL/TLS for database connections
  - [ ] Enable VPC/security groups

### API Security
- [ ] **HTTPS/TLS enabled**
- [ ] **CORS configured properly**
- [ ] **Rate limiting enabled**
  - [ ] API rate limits
  - [ ] Database query limits

- [ ] **Input validation**
  - [ ] All endpoints validate input (done in code)
  - [ ] SQL injection prevention (using parameterized queries - done)
  - [ ] XSS prevention headers

- [ ] **Authentication & Authorization**
  - [ ] JWT token validation working
  - [ ] Token expiration enforced
  - [ ] Password requirements met (72-byte limit enforced)

### SSL/TLS Certificates
- [ ] **Obtain SSL certificate** (Let's Encrypt, AWS Certificate Manager, etc.)
- [ ] **Configure certificate on hosting platform**
- [ ] **Set certificate auto-renewal**
- [ ] **Test HTTPS**: `https://your-api-domain.com/health`

---

## Post-Deployment Verification

### Functional Testing
- [ ] **Login works** - Credentials authenticate properly
- [ ] **PO operations work** - Can list, create, update POs
- [ ] **Line items work** - Can add, update, delete line items
- [ ] **Database operations work** - Data persists correctly
- [ ] **Aggregation works** - `/po/aggregated/by-store` returns bundled POs

### Data Integrity
- [ ] **Record counts match backup**
  ```sql
  SELECT COUNT(*) FROM "Finances".client;  -- 2
  SELECT COUNT(*) FROM "Finances".vendor;  -- 13
  SELECT COUNT(*) FROM "Finances".client_po;  -- 4
  SELECT COUNT(*) FROM "Finances".client_po_line_item;  -- 156
  ```

- [ ] **Foreign key relationships intact**
- [ ] **Timestamps preserved**
- [ ] **All records accessible**

### Documentation
- [ ] **API documentation accessible** - `/docs` endpoint
- [ ] **Postman collection updated** with new API URL
- [ ] **Team documentation updated**

---

## Post-Deployment Checklist

### Immediate Actions (Day 1)
- [ ] Monitor API logs for errors
- [ ] Test critical business flows
- [ ] Monitor performance metrics
- [ ] Verify automated backups run

### Follow-up Actions (Day 2-7)
- [ ] Load testing (optional but recommended)
- [ ] Security scanning
- [ ] Database performance tuning
- [ ] Review logs for issues

### Final Handoff
- [ ] All systems operational
- [ ] Team trained on monitoring/maintenance
- [ ] Documentation complete and accessible
- [ ] Support procedures documented

---

## Rollback Plan (If Issues Found)

### Quick Rollback Steps
1. **Stop the API service**: Stop the application server
2. **Check logs**: `tail -f /var/log/nexgen-api/error.log`
3. **Identify issue**: API or database?
4. **Restore database** (if needed):
   ```bash
   python restore_database.py latest_backup.sql
   ```
5. **Redeploy previous version**: Roll back code changes
6. **Restart API**: Start service with previous version
7. **Verify**: Test all endpoints again

### Contact Information
- **Database Support**: [Team contact]
- **Infrastructure Support**: [Team contact]
- **API Developer**: [Team contact]

---

## Sign-Off

- [ ] Database Deployment: __________ Date: __________
- [ ] Application Deployment: __________ Date: __________
- [ ] Testing Complete: __________ Date: __________
- [ ] Production Ready: __________ Date: __________

---

**Last Updated**: February 22, 2026
**Backup File**: `Nexgen_erp_backup_20260222_230959.sql`
**Database Schema**: Finances
**Total Records**: 196 across 19 tables
