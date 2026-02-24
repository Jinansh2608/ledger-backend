# Production Deployment Guide

## Overview
This guide provides complete instructions for deploying the Nexgen ERP Finance API to production.

## Pre-Deployment Requirements

### 1. System Requirements
- Python 3.9+
- PostgreSQL 12+
- 2GB RAM minimum (4GB recommended)
- 10GB disk space minimum
- Ubuntu 20.04+ or equivalent Linux distribution

### 2. Install Dependencies
```bash
cd /path/to/backend
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your production values
nano .env
```

**Critical .env Variables:**
```
APP_ENVIRONMENT=production
DEBUG_MODE=false
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=Nexgen_erp
DB_USER=postgres
DB_PASSWORD=strong-secure-password
SECRET_KEY=generate-with:openssl rand -hex 32
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=WARNING
```

### 4. Database Verification
```bash
# Test database connection
python -c "from app.database import init_connection_pool; init_connection_pool(); print('✓ Database connection OK')"

# Verify schema
python -c "from app.database import get_db; conn = get_db(); cur = conn.cursor(); cur.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='Finances'\"); print(f\"Tables: {cur.fetchone()[0]}\")"
```

## Deployment Options

### Option 1: Systemd Service (Recommended)

#### 1.1 Create Service File
```bash
sudo nano /etc/systemd/system/nexgen-api.service
```

Add this content:
```ini
[Unit]
Description=Nexgen ERP Finance API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/nexgen/backend
Environment="PATH=/opt/nexgen/backend/venv/bin"
ExecStart=/opt/nexgen/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/nexgen/access.log \
    --error-logfile /var/log/nexgen/error.log \
    --log-level warning \
    app.main:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 1.2 Install and Start
```bash
# Create log directory
sudo mkdir -p /var/log/nexgen
sudo chown www-data:www-data /var/log/nexgen

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable nexgen-api
sudo systemctl start nexgen-api

# Check status
sudo systemctl status nexgen-api
```

### Option 2: Docker Deployment

#### 2.1 Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

EXPOSE 8000
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
```

#### 2.2 Build and Run
```bash
# Build image
docker build -t nexgen-api:latest .

# Run container
docker run -d \
  --name nexgen-api \
  -p 8000:8000 \
  --env-file .env \
  -v /data/uploads:/app/uploads \
  -v /data/logs:/app/logs \
  nexgen-api:latest
```

### Option 3: Gunicorn with Nginx Reverse Proxy

#### 3.1 Create Virtual Environment and Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 3.2 Testing Locally
```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 app.main:app
```

#### 3.3 Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/nexgen-api
```

Add:
```nginx
upstream nexgen_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Certificate Config
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/nexgen_access.log;
    error_log /var/log/nginx/nexgen_error.log;

    # Client upload limit
    client_max_body_size 50M;

    # Proxy settings
    location / {
        proxy_pass http://nexgen_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static uploads
    location /uploads/ {
        alias /data/uploads/;
        expires 7d;
    }
}
```

#### 3.4 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/nexgen-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS Setup with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d api.yourdomain.com

# Auto-renewal (already enabled by default)
sudo systemctl enable certbot.timer
```

## Monitoring & Logging

### Check Service Status
```bash
# Systemd
sudo systemctl status nexgen-api
sudo journalctl -u nexgen-api -n 100 --follow

# Docker
docker logs -f nexgen-api

# Nginx
tail -f /var/log/nginx/nexgen_access.log
tail -f /var/log/nginx/nexgen_error.log

# Application
tail -f logs/app.log
tail -f logs/error.log
```

### Health Check
```bash
# Local
curl http://localhost:8000/api/health

# Remote
curl https://api.yourdomain.com/api/health

# Detailed health
curl https://api.yourdomain.com/api/health/detailed
```

## Performance Tuning

### PostgreSQL Connection Pool
Increase pool size if seeing "connection pool exhausted" errors:
```env
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
```

### Gunicorn Workers
For 4 CPU cores, use 9-11 workers:
```bash
gunicorn --workers 10 --worker-class uvicorn.workers.UvicornWorker app.main:app
```

### Nginx Tuning
```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
```

## Backup & Recovery

### Database Backup
```bash
# Full backup
pg_dump -h localhost -U postgres -d Nexgen_erp > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -h localhost -U postgres -d Nexgen_erp | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Scheduled backup (cron)
0 2 * * * pg_dump -h localhost -U postgres -d Nexgen_erp | gzip > /backups/Nexgen_$(date +\%Y\%m\%d).sql.gz
```

### Restore from Backup
```bash
psql -h localhost -U postgres -d Nexgen_erp < backup.sql
```

## Security Hardening

### 1. Firewall Rules
```bash
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 443/tcp # HTTPS
sudo ufw allow 80/tcp  # HTTP (redirect)
sudo ufw deny 8000/tcp # Block direct app access
```

### 2. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove
```

### 3. Disable Root Login
```bash
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 4. Set File Permissions
```bash
chmod 700 /opt/nexgen/backend
chmod 600 /opt/nexgen/backend/.env
chown www-data:www-data /opt/nexgen/backend/.env
```

## Troubleshooting

### API Not Starting
```bash
# Check logs
sudo journalctl -u nexgen-api -n 50 | grep ERROR

# Test environment
python -c "from app.config import settings; print(settings.dict())"

# Test database connection
python -c "from app.database import init_connection_pool; init_connection_pool()"
```

### Database Connection Issues
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d Nexgen_erp -c "SELECT 1"

# Check connection limit
sudo -u postgres psql -c "SHOW max_connections;"
```

### High Memory Usage
```bash
# Check process
ps aux | grep gunicorn

# Reduce workers if needed
# Update systemd service or nginx config

# Check for connection leaks
ps aux | grep python | wc -l
```

## Monitoring with Prometheus (Optional)

Install Prometheus client:
```bash
pip install prometheus-client
```

Add to main.py for metrics endpoint:
```python
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY, CollectorRegistry
from prometheus_client.asgi import make_wsgi_app

# Metrics
request_count = Counter('api_requests_total', 'Total requests', ['method', 'endpoint'])
request_latency = Histogram('api_request_duration_seconds', 'Request latency')

# Add metrics endpoint
app.add_route("/metrics", make_wsgi_app(registry=REGISTRY))
```

## Final Checklist

- [ ] Environment variables configured
- [ ] Database migrated and verified
- [ ] SSL/TLS certificate installed
- [ ] Nginx reverse proxy configured
- [ ] Systemd service running
- [ ] Backups configured and tested
- [ ] Firewall rules applied
- [ ] Monitoring setup complete
- [ ] Load testing passed
- [ ] Health check endpoints responding
- [ ] Error logging working
- [ ] Documentation updated

## Support & Escalation

For issues, check:
1. Application logs: `/app/logs/app.log`
2. Error logs: `/app/logs/error.log`
3. System logs: `journalctl -u nexgen-api`
4. Database logs: PostgreSQL error log

Contact DevOps team for database issues or infrastructure problems.
