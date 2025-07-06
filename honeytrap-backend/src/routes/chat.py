from flask import Blueprint, request, jsonify
from src.models.chat import db, ChatSession, ChatMessage, Persona, Evidence, AuditLog
from src.ai_engine import AIPersonaEngine
from datetime import datetime
import uuid
import json
import hashlib
import os

chat_bp = Blueprint('chat', __name__)
ai_engine = AIPersonaEngine()

@chat_bp.route('/chat/start', methods=['POST'])
def start_chat():
    """Initialize a new chat session with a decoy persona"""
    try:
        data = request.get_json()
        platform_type = data.get('platform_type', 'discord')
        
        # Get client information
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Select an active persona for the platform
        persona = Persona.query.filter_by(platform_type=platform_type, active=True).first()
        if not persona:
            return jsonify({'error': 'No active persona available for platform'}), 400
        
        # Create new session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            persona_id=persona.id,
            user_ip=user_ip,
            user_agent=user_agent
        )
        
        db.session.add(chat_session)
        db.session.commit()
        
        # Log the session start
        audit_log = AuditLog(
            action='chat_session_started',
            session_id=session_id,
            details=json.dumps({'platform_type': platform_type, 'persona_id': persona.id}),
            ip_address=user_ip
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'persona': persona.to_dict(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/message', methods=['POST'])
def send_message():
    """Handle incoming user messages and generate AI responses"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message_content = data.get('message')
        
        if not session_id or not message_content:
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        # Find the chat session
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            return jsonify({'error': 'Invalid session_id'}), 404
        
        # Update last activity
        chat_session.last_activity = datetime.utcnow()
        
        # Get conversation history
        conversation_history = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
        history_data = [msg.to_dict() for msg in conversation_history]
        
        # Generate AI response using the AI engine
        persona_data = chat_session.persona.to_dict()
        ai_result = ai_engine.generate_response(persona_data, message_content, history_data)
        
        ai_response = ai_result['response']
        threat_level = ai_result['threat_level']
        
        # Store user message
        user_message = ChatMessage(
            session_id=chat_session.id,
            sender_type='user',
            message_content=message_content,
            threat_level=threat_level
        )
        db.session.add(user_message)
        
        # Update escalation level if needed
        if threat_level > chat_session.escalation_level:
            chat_session.escalation_level = threat_level
            
            # Trigger evidence capture for high-risk messages
            if threat_level >= 2:
                capture_evidence(chat_session, user_message)
        
        # Store AI response
        ai_message = ChatMessage(
            session_id=chat_session.id,
            sender_type='decoy',
            message_content=ai_response
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'escalation_level': chat_session.escalation_level,
            'threat_level': threat_level,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Retrieve chat history for a session"""
    try:
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            return jsonify({'error': 'Session not found'}), 404
        
        messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
        
        return jsonify({
            'session': chat_session.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/personas', methods=['GET'])
def get_personas():
    """Get all active personas"""
    try:
        personas = Persona.query.filter_by(active=True).all()
        return jsonify([persona.to_dict() for persona in personas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/personas', methods=['POST'])
def create_persona():
    """Create a new decoy persona"""
    try:
        data = request.get_json()
        
        persona = Persona(
            name=data['name'],
            age=data['age'],
            platform_type=data['platform_type'],
            personality_traits=json.dumps(data['personality_traits']),
            language_style=json.dumps(data['language_style']),
            response_patterns=json.dumps(data['response_patterns']),
            avatar_url=data.get('avatar_url')
        )
        
        db.session.add(persona)
        db.session.commit()
        
        return jsonify(persona.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def capture_evidence(chat_session, message):
    """Capture evidence when escalation is detected"""
    try:
        # Create evidence record
        evidence_data = {
            'session_id': chat_session.session_id,
            'message_id': message.id,
            'user_ip': chat_session.user_ip,
            'user_agent': chat_session.user_agent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        content = json.dumps(evidence_data)
        hash_value = hashlib.sha256(content.encode()).hexdigest()
        
        evidence = Evidence(
            session_id=chat_session.id,
            evidence_type='threat_detection',
            content=content,
            hash_value=hash_value
        )
        
        db.session.add(evidence)
        chat_session.evidence_captured = True
        
        # Log evidence capture
        audit_log = AuditLog(
            action='evidence_captured',
            session_id=chat_session.session_id,
            details=json.dumps({'threat_level': message.threat_level}),
            ip_address=chat_session.user_ip
        )
        db.session.add(audit_log)
        
    except Exception as e:
        print(f"Error capturing evidence: {e}")

