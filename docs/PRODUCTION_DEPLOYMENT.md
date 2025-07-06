# Production Deployment Guide - AI Honeytrap Network

**Hampshire Police - AI Honeytrap Network**  
**Version 1.0 - Production Ready**

## Overview

This guide provides comprehensive instructions for deploying the AI Honeytrap Network system to production environments using modern cloud infrastructure. The system has been designed with security, scalability, and law enforcement requirements in mind.

## Architecture Overview

The AI Honeytrap Network consists of several key components:

- **Frontend Application**: React-based user interface with authentic social media platform replicas
- **Backend API**: Flask-based REST API with WebSocket support for real-time communication
- **AI Engine**: Advanced persona-based chatbot with threat detection capabilities
- **Database**: SQLite for development, PostgreSQL recommended for production
- **Security Layer**: JWT authentication, encryption, and comprehensive audit logging

## Production Infrastructure Requirements

### Server Specifications

**Minimum Requirements:**
- CPU: 2 vCPUs
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100 Mbps

**Recommended for High Traffic:**
- CPU: 4 vCPUs
- RAM: 8GB
- Storage: 50GB SSD
- Network: 1 Gbps

### Cloud Provider Options

#### Option 1: Hetzner Cloud (Recommended)
Using the provided Hetzner API key, you can deploy to Hetzner's reliable European infrastructure:

```bash
# Using Hetzner API
export HETZNER_API_KEY="SYF3UCvB3R3Lla3eiHxtVdpiEkEDDZS42DPCsbDW5dcH7tsrFy2v8J32Iw2RCIT9"

# Create server instance
hcloud server create --type cx21 --image ubuntu-22.04 --name honeytrap-prod --ssh-key "ssh-rsa AAAAB3...== jonny@kliqtmedia.co.uk"
```

#### Option 2: DigitalOcean
Using the provided DigitalOcean API key:

```bash
export DIGITAL_OCEAN_API_KEY="dop_v1_571d32ce2e5ac8a7e01531b14fe30336a0804cea876b9b1fa2c60bb3be6a744c"
```

## Deployment Methods

### Method 1: CapRover Deployment (Recommended)

CapRover provides an easy-to-use platform for deploying applications with built-in SSL, monitoring, and scaling capabilities.

#### Step 1: CapRover Setup
```bash
# Install CapRover CLI
npm install -g caprover

# Connect to your CapRover instance
caprover serversetup
```

#### Step 2: Application Configuration
Create `captain-definition` file in project root:

```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile"
}
```

#### Step 3: Deploy Backend
```bash
# Navigate to backend directory
cd honeytrap-backend

# Deploy to CapRover
caprover deploy
```

#### Step 4: Deploy Frontend
```bash
# Navigate to frontend directory
cd honeytrap-frontend

# Build for production
pnpm run build

# Deploy to CapRover
caprover deploy
```

### Method 2: Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY . .

EXPOSE 5000

CMD ["python", "src/main_websocket.py"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./honeytrap-backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/honeytrap
    depends_on:
      - db

  frontend:
    build: ./honeytrap-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=honeytrap
      - POSTGRES_USER=honeytrap_user
      - POSTGRES_PASSWORD=secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Database Configuration

### PostgreSQL Setup for Production

```sql
-- Create database and user
CREATE DATABASE honeytrap_production;
CREATE USER honeytrap_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE honeytrap_production TO honeytrap_user;

-- Connect to the database
\c honeytrap_production;

-- Create tables (run the Flask migration)
```

### Environment Variables

Create a `.env` file for production:

```bash
# Database
DATABASE_URL=postgresql://honeytrap_user:password@localhost:5432/honeytrap_production

# Security
SECRET_KEY=your_very_secure_secret_key_here
JWT_SECRET_KEY=another_secure_key_for_jwt

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=hampshire_secure_2024

# API Configuration
FLASK_ENV=production
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/honeytrap/app.log
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Security Hardening

### Firewall Configuration
```bash
# UFW firewall setup
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### System Security
```bash
# Update system
apt update && apt upgrade -y

# Install fail2ban
apt install fail2ban -y

# Configure automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure unattended-upgrades
```

## Monitoring and Logging

### Application Monitoring
```python
# Add to Flask app
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/honeytrap.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### System Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'honeytrap'
    static_configs:
      - targets: ['localhost:5000']
```

## Backup Strategy

### Database Backups
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump honeytrap_production > /backups/honeytrap_$DATE.sql
find /backups -name "honeytrap_*.sql" -mtime +7 -delete
```

### Application Backups
```bash
#!/bin/bash
# backup_app.sh
tar -czf /backups/honeytrap_app_$(date +%Y%m%d).tar.gz /opt/honeytrap
```

## Performance Optimization

### Redis Caching
```python
# Add Redis for session management
import redis
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

### Load Balancing with Nginx
```nginx
upstream honeytrap_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location /api/ {
        proxy_pass http://honeytrap_backend;
    }
}
```

## Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup systems tested
- [ ] Monitoring systems configured

### Post-Deployment
- [ ] Application health checks passing
- [ ] SSL certificate validation
- [ ] Database connectivity verified
- [ ] WebSocket functionality tested
- [ ] Admin dashboard accessible
- [ ] Evidence capture system tested
- [ ] Threat detection algorithms verified

## Troubleshooting

### Common Issues

**WebSocket Connection Failures:**
```bash
# Check if WebSocket port is open
netstat -tulpn | grep :5000

# Verify nginx WebSocket configuration
nginx -t
```

**Database Connection Issues:**
```bash
# Test PostgreSQL connection
psql -h localhost -U honeytrap_user -d honeytrap_production

# Check database logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

**High Memory Usage:**
```bash
# Monitor application memory
ps aux | grep python
htop

# Check for memory leaks
valgrind --tool=memcheck python src/main_websocket.py
```

## Maintenance Procedures

### Regular Maintenance Tasks

**Weekly:**
- Review application logs for errors
- Check disk space usage
- Verify backup integrity
- Update security patches

**Monthly:**
- Review evidence capture statistics
- Analyze threat detection accuracy
- Update AI persona responses
- Performance optimization review

**Quarterly:**
- Security audit and penetration testing
- Database optimization and cleanup
- Infrastructure capacity planning
- Disaster recovery testing

## Support and Contact Information

**Technical Support:**
- Primary Contact: Hampshire Police IT Department
- Emergency Contact: 24/7 SOC Team
- Documentation: Internal Wiki System

**Vendor Support:**
- AI Engine: Manus AI Support Team
- Infrastructure: Cloud Provider Support
- Security: Cybersecurity Consultant

---

**Document Version:** 1.0  
**Last Updated:** $(date)  
**Author:** Manus AI  
**Classification:** RESTRICTED - Law Enforcement Use Only

