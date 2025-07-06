# Deployment Guide - AI Honeytrap Network

This guide provides comprehensive instructions for deploying the AI Honeytrap Network system in production environments for Hampshire Police.

## 🎯 Deployment Overview

The AI Honeytrap Network can be deployed in several configurations depending on security requirements, scale, and infrastructure preferences. This guide covers both development and production deployment scenarios.

## 🏗️ Infrastructure Requirements

### Minimum System Requirements

**Development Environment:**
- CPU: 2 cores, 2.4GHz
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100Mbps connection

**Production Environment:**
- CPU: 4 cores, 3.0GHz
- RAM: 8GB
- Storage: 100GB SSD (with backup)
- Network: 1Gbps connection
- Load Balancer: Recommended for high availability

### Recommended Infrastructure

**Cloud Deployment (AWS/Azure/GCP):**
- Application Server: t3.medium or equivalent
- Database: RDS PostgreSQL or managed database service
- Load Balancer: Application Load Balancer
- CDN: CloudFront or equivalent for static assets
- Monitoring: CloudWatch or equivalent

**On-Premises Deployment:**
- Dedicated server or VM cluster
- Network isolation and firewall protection
- Backup and disaster recovery systems
- Monitoring and alerting infrastructure

## 🔧 Production Deployment Steps

### Step 1: Environment Preparation

1. **Server Setup**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv nodejs npm nginx postgresql

# Install pnpm globally
npm install -g pnpm

# Create application user
sudo useradd -m -s /bin/bash honeytrap
sudo usermod -aG sudo honeytrap
```

2. **Database Setup**
```bash
# Install and configure PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE honeytrap_db;
CREATE USER honeytrap_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE honeytrap_db TO honeytrap_user;
\q
```

### Step 2: Application Deployment

1. **Clone Repository**
```bash
sudo -u honeytrap git clone https://github.com/jonnyallum/Decoy_honeytrap.git /opt/honeytrap
cd /opt/honeytrap
sudo chown -R honeytrap:honeytrap /opt/honeytrap
```

2. **Backend Deployment**
```bash
cd /opt/honeytrap/honeytrap-backend

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure production settings
cp src/config/production.py.example src/config/production.py
# Edit production.py with your database credentials and security settings

# Initialize database
python src/manage.py db upgrade
```

3. **Frontend Build**
```bash
cd /opt/honeytrap/honeytrap-frontend

# Install dependencies
pnpm install

# Build for production
pnpm run build

# Copy build files to web server directory
sudo cp -r dist/* /var/www/honeytrap/
```

### Step 3: Web Server Configuration

1. **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/honeytrap
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Frontend static files
    location / {
        root /var/www/honeytrap;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    }
    
    # API proxy to backend
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Admin panel with additional security
    location /admin/ {
        # IP whitelist for admin access
        allow 192.168.1.0/24;  # Internal network
        allow 10.0.0.0/8;      # VPN network
        deny all;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/honeytrap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 4: Process Management

1. **Systemd Service Configuration**
```ini
# /etc/systemd/system/honeytrap-backend.service
[Unit]
Description=AI Honeytrap Network Backend
After=network.target postgresql.service

[Service]
Type=simple
User=honeytrap
Group=honeytrap
WorkingDirectory=/opt/honeytrap/honeytrap-backend
Environment=FLASK_ENV=production
Environment=DATABASE_URL=postgresql://honeytrap_user:secure_password_here@localhost/honeytrap_db
ExecStart=/opt/honeytrap/honeytrap-backend/venv/bin/python src/main.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/honeytrap/honeytrap-backend/logs

[Install]
WantedBy=multi-user.target
```

2. **Start Services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable honeytrap-backend
sudo systemctl start honeytrap-backend
sudo systemctl status honeytrap-backend
```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Obtain SSL Certificate**
```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Or use your organization's certificate authority
```

2. **Security Headers**
Ensure all security headers are properly configured in Nginx (see configuration above).

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Database Security

1. **PostgreSQL Hardening**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/13/main/postgresql.conf

# Set secure configurations
listen_addresses = 'localhost'
ssl = on
log_connections = on
log_disconnections = on
log_statement = 'all'
```

2. **Regular Backups**
```bash
# Create backup script
#!/bin/bash
# /opt/honeytrap/scripts/backup.sh
BACKUP_DIR="/opt/honeytrap/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h localhost -U honeytrap_user honeytrap_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Application backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" /opt/honeytrap

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

## 📊 Monitoring and Logging

### Application Monitoring

1. **Log Configuration**
```python
# Add to Flask app configuration
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/honeytrap.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

2. **System Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/honeytrap
```

### Health Checks

1. **Application Health Endpoint**
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

2. **Monitoring Script**
```bash
#!/bin/bash
# /opt/honeytrap/scripts/health_check.sh
HEALTH_URL="https://your-domain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$RESPONSE" != "200" ]; then
    echo "Health check failed: HTTP $RESPONSE"
    # Send alert notification
    systemctl restart honeytrap-backend
fi
```

## 🚀 Performance Optimization

### Database Optimization

1. **PostgreSQL Tuning**
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_chat_sessions_escalation ON chat_sessions(escalation_level);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX idx_evidence_session_id ON evidence(session_id);
```

2. **Connection Pooling**
```python
# Add to Flask configuration
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Application Optimization

1. **Caching Configuration**
```python
# Add Redis caching for session data
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})
```

2. **Static File Optimization**
```bash
# Enable Nginx gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## 🔄 Maintenance Procedures

### Regular Maintenance Tasks

1. **Daily Tasks**
   - Monitor system health and performance
   - Review security logs for anomalies
   - Check backup completion status
   - Verify evidence integrity

2. **Weekly Tasks**
   - Update system packages
   - Review and archive old evidence
   - Performance optimization review
   - Security audit of access logs

3. **Monthly Tasks**
   - Full system backup verification
   - Security patch assessment and application
   - Capacity planning review
   - Compliance audit preparation

### Update Procedures

1. **Application Updates**
```bash
# Create maintenance window
sudo systemctl stop honeytrap-backend

# Backup current version
cp -r /opt/honeytrap /opt/honeytrap-backup-$(date +%Y%m%d)

# Pull updates
cd /opt/honeytrap
git pull origin main

# Update dependencies
cd honeytrap-backend
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
python src/manage.py db upgrade

# Rebuild frontend
cd ../honeytrap-frontend
pnpm install
pnpm run build
sudo cp -r dist/* /var/www/honeytrap/

# Restart services
sudo systemctl start honeytrap-backend
sudo systemctl reload nginx
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U honeytrap_user -d honeytrap_db

# Review logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

2. **Application Startup Issues**
```bash
# Check service status
sudo systemctl status honeytrap-backend

# Review application logs
sudo journalctl -u honeytrap-backend -f

# Check port availability
sudo netstat -tlnp | grep :5001
```

3. **Frontend Issues**
```bash
# Check Nginx configuration
sudo nginx -t

# Review Nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify static files
ls -la /var/www/honeytrap/
```

### Emergency Procedures

1. **System Recovery**
   - Restore from latest backup
   - Verify data integrity
   - Restart all services
   - Notify stakeholders

2. **Security Incident Response**
   - Isolate affected systems
   - Preserve evidence
   - Contact security team
   - Follow incident response procedures

---

**For additional support or questions regarding deployment, contact the Hampshire Police Technical Support Team.**

