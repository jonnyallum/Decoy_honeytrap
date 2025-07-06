from flask import Blueprint, request, jsonify, send_file
from src.models.chat import db, ChatSession, ChatMessage, Persona, Evidence, AuditLog
from src.security import security_manager, require_auth, rate_limit
from datetime import datetime, timedelta
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import tempfile

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
@rate_limit(max_requests=5, window_minutes=15)  # Strict rate limiting for login
def admin_login():
    """Secure admin login with proper authentication"""
    try:
        data = request.get_json()
        username = security_manager.sanitize_input(data.get('username', ''))
        password = data.get('password', '')
        
        # Log login attempt
        security_manager.log_security_event(
            'login_attempt', 
            f'Username: {username}', 
            request.remote_addr
        )
        
        # Demo credentials (in production, use database with hashed passwords)
        if username == 'admin' and password == 'hampshire2024':
            # Generate secure session token
            token = security_manager.generate_session_token(
                user_id='admin_user',
                role='admin'
            )
            
            security_manager.log_security_event(
                'login_success', 
                f'Admin user logged in', 
                request.remote_addr
            )
            
            return jsonify({
                'success': True,
                'token': token,
                'message': 'Login successful'
            })
        else:
            security_manager.log_security_event(
                'login_failed', 
                f'Invalid credentials for username: {username}', 
                request.remote_addr
            )
            
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        security_manager.log_security_event(
            'login_error', 
            f'Login error: {str(e)}', 
            request.remote_addr
        )
        return jsonify({'error': 'Login failed'}), 500

@admin_bp.route('/admin/dashboard', methods=['GET'])
@require_auth
@rate_limit(max_requests=60, window_minutes=60)
def get_dashboard_stats():
    """Get dashboard statistics for admin interface"""
    try:
        # Log dashboard access
        security_manager.log_security_event(
            'dashboard_access', 
            f'User {request.current_user["user_id"]} accessed dashboard', 
            request.remote_addr
        )
        
        # Get date range for filtering (default: last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Active sessions
        active_sessions = ChatSession.query.filter(
            ChatSession.last_activity >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        # Total sessions in period
        total_sessions = ChatSession.query.filter(
            ChatSession.created_at >= start_date
        ).count()
        
        # High-risk sessions
        high_risk_sessions = ChatSession.query.filter(
            ChatSession.escalation_level >= 2,
            ChatSession.created_at >= start_date
        ).count()
        
        # Evidence captured
        evidence_count = Evidence.query.join(ChatSession).filter(
            ChatSession.created_at >= start_date
        ).count()
        
        # Recent high-risk sessions
        recent_high_risk = ChatSession.query.filter(
            ChatSession.escalation_level >= 2
        ).order_by(ChatSession.last_activity.desc()).limit(10).all()
        
        return jsonify({
            'stats': {
                'active_sessions': active_sessions,
                'total_sessions': total_sessions,
                'high_risk_sessions': high_risk_sessions,
                'evidence_count': evidence_count
            },
            'recent_high_risk': [session.to_dict() for session in recent_high_risk]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions with filtering options"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        escalation_level = request.args.get('escalation_level', type=int)
        
        query = ChatSession.query
        
        if escalation_level is not None:
            query = query.filter(ChatSession.escalation_level >= escalation_level)
        
        sessions = query.order_by(ChatSession.last_activity.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions.items],
            'pagination': {
                'page': page,
                'pages': sessions.pages,
                'per_page': per_page,
                'total': sessions.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/sessions/<int:session_id>/evidence', methods=['GET'])
def get_session_evidence(session_id):
    """Get all evidence for a specific session"""
    try:
        evidence_list = Evidence.query.filter_by(session_id=session_id).all()
        return jsonify([evidence.to_dict() for evidence in evidence_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/sessions/<int:session_id>/report', methods=['GET'])
def generate_evidence_report(session_id):
    """Generate a comprehensive evidence report for law enforcement"""
    try:
        chat_session = ChatSession.query.get(session_id)
        if not chat_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get all messages and evidence
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        evidence_list = Evidence.query.filter_by(session_id=session_id).all()
        
        # Generate PDF report
        report_path = generate_pdf_report(chat_session, messages, evidence_list)
        
        return send_file(report_path, as_attachment=True, 
                        download_name=f'evidence_report_{chat_session.session_id}.pdf')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action = request.args.get('action')
        
        query = AuditLog.query
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        logs = query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'pages': logs.pages,
                'per_page': per_page,
                'total': logs.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/personas/<int:persona_id>/toggle', methods=['POST'])
def toggle_persona(persona_id):
    """Toggle persona active status"""
    try:
        persona = Persona.query.get(persona_id)
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        persona.active = not persona.active
        db.session.commit()
        
        # Log the action
        audit_log = AuditLog(
            action='persona_toggled',
            details=json.dumps({'persona_id': persona_id, 'active': persona.active}),
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify(persona.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_pdf_report(chat_session, messages, evidence_list):
    """Generate a PDF evidence report for law enforcement"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("DIGITAL EVIDENCE REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Case Information
    story.append(Paragraph("CASE INFORMATION", styles['Heading2']))
    case_data = [
        ['Session ID:', chat_session.session_id],
        ['Date Created:', chat_session.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')],
        ['Last Activity:', chat_session.last_activity.strftime('%Y-%m-%d %H:%M:%S UTC')],
        ['Escalation Level:', f"Level {chat_session.escalation_level}"],
        ['Evidence Captured:', 'Yes' if chat_session.evidence_captured else 'No'],
        ['User IP Address:', chat_session.user_ip],
        ['User Agent:', chat_session.user_agent or 'Not available']
    ]
    
    case_table = Table(case_data, colWidths=[2*72, 4*72])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(case_table)
    story.append(Spacer(1, 20))
    
    # Persona Information
    story.append(Paragraph("DECOY PERSONA INFORMATION", styles['Heading2']))
    persona = chat_session.persona
    persona_data = [
        ['Persona Name:', persona.name],
        ['Age:', str(persona.age)],
        ['Platform:', persona.platform_type.title()],
        ['Personality Traits:', json.dumps(json.loads(persona.personality_traits), indent=2)]
    ]
    
    persona_table = Table(persona_data, colWidths=[2*72, 4*72])
    persona_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(persona_table)
    story.append(Spacer(1, 20))
    
    # Chat Messages
    story.append(Paragraph("CHAT TRANSCRIPT", styles['Heading2']))
    for message in messages:
        sender = "SUSPECT" if message.sender_type == 'user' else f"DECOY ({persona.name})"
        timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Message header
        header_text = f"<b>{sender}</b> - {timestamp}"
        if message.threat_level > 0:
            header_text += f" <b>[THREAT LEVEL: {message.threat_level}]</b>"
        
        story.append(Paragraph(header_text, styles['Normal']))
        
        # Message content
        content_style = ParagraphStyle(
            'MessageContent',
            parent=styles['Normal'],
            leftIndent=20,
            spaceAfter=10,
            borderColor=colors.red if message.threat_level >= 2 else colors.orange if message.threat_level >= 1 else colors.grey,
            borderWidth=1 if message.threat_level > 0 else 0,
            borderPadding=5
        )
        story.append(Paragraph(message.message_content, content_style))
        story.append(Spacer(1, 10))
    
    # Evidence Summary
    if evidence_list:
        story.append(Paragraph("EVIDENCE SUMMARY", styles['Heading2']))
        for evidence in evidence_list:
            story.append(Paragraph(f"<b>Evidence Type:</b> {evidence.evidence_type}", styles['Normal']))
            story.append(Paragraph(f"<b>Created:</b> {evidence.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
            story.append(Paragraph(f"<b>Hash:</b> {evidence.hash_value}", styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    
    return temp_path

