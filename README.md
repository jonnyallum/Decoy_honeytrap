# AI Honeytrap Network

**Online Safety Solution**

A sophisticated AI-powered honeytrap system designed to detect and capture evidence of online predatory behavior through realistic decoy chat interfaces, intelligent AI responses, and comprehensive evidence collection.

## 🚨 Important Notice

This system is designed exclusively for the purpose of detecting and preventing online predatory behavior. Unauthorized use is strictly prohibited.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Legal Compliance](#legal-compliance)
- [Support](#support)

## 🎯 Overview

The AI Honeytrap Network is a cutting-edge law enforcement tool that creates realistic social media chat environments to identify potential online predators. The system uses advanced AI personas that mimic age-appropriate communication patterns while automatically detecting and escalating suspicious behavior.

### Key Components

- **Decoy Chat Interfaces**: Authentic-looking social media platforms (Discord, Snapchat, TikTok)
- **AI Persona Engine**: Sophisticated AI that generates age-appropriate responses
- **Threat Detection**: Real-time analysis of incoming messages for predatory behavior
- **Evidence Collection**: Automated capture and documentation of suspicious interactions
- **Admin Dashboard**: Comprehensive monitoring and reporting interface

## ✨ Features

### 🤖 AI-Powered Personas
- Multiple pre-configured personas with different ages and platform preferences
- Age-appropriate language patterns and slang usage
- Realistic response timing and conversation flow
- Adaptive behavior based on conversation context

### 🔍 Threat Detection
- Real-time message analysis for grooming patterns
- Escalation level tracking (Normal → Suspicious → High Risk)
- Automatic evidence capture when threats are detected
- Comprehensive logging of all interactions

### 📊 Admin Dashboard
- Real-time monitoring of active sessions
- Statistical overview of system activity
- High-risk session alerts and management
- Evidence report generation for legal proceedings

### 🔒 Security & Compliance
- End-to-end encryption for all data
- Comprehensive audit logging
- Secure evidence storage with integrity verification
- GDPR and law enforcement compliance features

## 🏗️ Architecture

The system follows a modern microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ • Chat UIs      │    │ • AI Engine     │    │ • Sessions      │
│ • Admin Panel   │    │ • Threat Det.   │    │ • Messages      │
│ • Auth          │    │ • Evidence      │    │ • Evidence      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Frontend:**
- React 18 with modern hooks
- Tailwind CSS for styling
- React Router for navigation
- Responsive design for all devices

**Backend:**
- Flask web framework
- SQLAlchemy ORM
- CORS enabled for frontend communication
- RESTful API design

**AI Engine:**
- Custom persona-based response generation
- Threat detection algorithms
- Conversation context analysis
- Escalation management

**Database:**
- SQLite for development (easily upgradeable to PostgreSQL)
- Comprehensive data models
- Audit logging
- Evidence integrity verification

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm package manager

### Backend Setup

1. Navigate to the backend directory:
```bash
cd honeytrap-backend
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python src/main.py
```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd honeytrap-frontend
```

2. Install dependencies:
```bash
pnpm install
```

3. Start the development server:
```bash
pnpm run dev --host
```

The frontend will be available at `http://localhost:5173`

## 📖 Usage

### For Law Enforcement Officers

#### Accessing the Admin Dashboard

1. Navigate to `http://localhost:5173/admin`
2. Login with credentials:
   - Username: `admin`
   - Password: `hampshire2024`
3. Monitor active sessions and review alerts

#### Generating Evidence Reports

1. Access the admin dashboard
2. Navigate to "Recent High-Risk Sessions"
3. Click "Report" on any session with captured evidence
4. Download the generated PDF report for legal proceedings

### For Testing (Authorized Personnel Only)

#### Testing Chat Interfaces

1. Navigate to `http://localhost:5173`
2. Select a platform (Discord, Snapchat, or TikTok)
3. Engage in conversation with the AI persona
4. Observe threat detection and escalation in the admin dashboard

## 📚 API Documentation

### Authentication Endpoints

#### Start Chat Session
```http
POST /api/chat/start
Content-Type: application/json

{
  "platform_type": "discord"
}
```

#### Send Message
```http
POST /api/chat/message
Content-Type: application/json

{
  "session_id": "uuid-string",
  "message": "user message content"
}
```

### Admin Endpoints

#### Dashboard Statistics
```http
GET /api/admin/dashboard
```

#### Session Management
```http
GET /api/admin/sessions?page=1&per_page=20
```

#### Evidence Report Generation
```http
GET /api/admin/sessions/{session_id}/report
```

For complete API documentation, see [API_REFERENCE.md](docs/API_REFERENCE.md)

## 🔐 Security

### Data Protection
- All sensitive data encrypted at rest using AES-256
- TLS encryption for data in transit
- Secure session management
- Regular security audits and updates

### Access Control
- Role-based access control for admin functions
- Secure authentication mechanisms
- Audit logging of all administrative actions
- IP-based access restrictions (configurable)

### Evidence Integrity
- SHA-256 hashing for all evidence files
- Tamper-evident storage mechanisms
- Chain of custody documentation
- Automated backup procedures

## ⚖️ Legal Compliance

This system has been designed with legal compliance in mind:

### Data Protection
- GDPR compliant data handling
- Configurable data retention policies
- Right to erasure implementation
- Privacy by design principles

### Law Enforcement Standards
- Evidence collection meets legal standards
- Comprehensive audit trails
- Secure evidence storage and transfer
- Court-admissible report generation

### Ethical Considerations
- Clear operational guidelines included
- Regular review and oversight procedures
- Transparent logging and accountability
- Minimal data collection principles

## 🆘 Support

### Technical Support
For technical issues or questions:
- Email: tech-support@kliqtmedia.co.uk
- Phone: +44 (0) 7723959178


### Training and Documentation
- Comprehensive user training materials available
- Regular training sessions for authorized personnel
- Updated documentation and best practices
- 24/7 emergency support for critical issues

### System Maintenance
- Regular security updates and patches
- Performance monitoring and optimization
- Backup and disaster recovery procedures
- Compliance audits and reporting

---

**© 2025 KLIQT Media. All rights reserved.**

*This system is for authorized use only. Unauthorized access or use is strictly prohibited and may result in criminal prosecution.*

