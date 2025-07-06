import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from src.models.user import db
from src.models.chat import ChatSession, ChatMessage, Persona, Evidence, AuditLog
from src.routes.user import user_bp
from src.routes.chat import chat_bp
from src.routes.admin import admin_bp
from src.ai_engine import AIPersonaEngine
import json
import uuid
from datetime import datetime

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'honeytrap-secure-key-2024-hampshire-police'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Initialize AI Engine
ai_engine = AIPersonaEngine()

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Store active WebSocket sessions
active_sessions = {}

# Initialize database and create default personas
with app.app_context():
    db.create_all()
    
    # Create default personas if they don't exist
    if Persona.query.count() == 0:
        default_personas = [
            {
                'name': 'Emma',
                'age': 13,
                'platform_type': 'discord',
                'personality_traits': {
                    'interests': ['gaming', 'anime', 'art'],
                    'personality': 'shy but friendly, loves to chat about hobbies',
                    'communication_style': 'uses lots of emojis, casual language'
                },
                'language_style': {
                    'common_phrases': ['omg', 'lol', 'that\'s so cool', 'i love that'],
                    'emoji_usage': 'frequent',
                    'slang': ['sus', 'bet', 'no cap', 'fr']
                },
                'response_patterns': {
                    'greeting': ['hey!', 'hi there!', 'what\'s up?'],
                    'interest': ['that sounds awesome!', 'tell me more!', 'i love that too!'],
                    'casual': ['lol yeah', 'omg really?', 'that\'s so cool']
                }
            },
            {
                'name': 'Jake',
                'age': 15,
                'platform_type': 'snapchat',
                'personality_traits': {
                    'interests': ['sports', 'music', 'friends'],
                    'personality': 'outgoing, sporty, social',
                    'communication_style': 'casual, uses abbreviations'
                },
                'language_style': {
                    'common_phrases': ['yo', 'what\'s good', 'that\'s sick', 'for real'],
                    'emoji_usage': 'moderate',
                    'slang': ['lit', 'fire', 'bet', 'facts']
                },
                'response_patterns': {
                    'greeting': ['yo what\'s up', 'hey man', 'what\'s good'],
                    'interest': ['that\'s sick!', 'no way!', 'for real?'],
                    'casual': ['bet', 'facts', 'that\'s fire']
                }
            },
            {
                'name': 'Zoe',
                'age': 14,
                'platform_type': 'tiktok',
                'personality_traits': {
                    'interests': ['dance', 'fashion', 'social media'],
                    'personality': 'trendy, social, loves attention',
                    'communication_style': 'uses trending phrases, lots of emojis'
                },
                'language_style': {
                    'common_phrases': ['periodt', 'slay', 'it\'s giving', 'main character'],
                    'emoji_usage': 'very frequent',
                    'slang': ['bestie', 'periodt', 'slay', 'iconic']
                },
                'response_patterns': {
                    'greeting': ['hey bestie!', 'hiiii', 'what\'s the tea?'],
                    'interest': ['slay!', 'that\'s iconic!', 'periodt!'],
                    'casual': ['bestie yes', 'it\'s giving', 'main character energy']
                }
            }
        ]
        
        for persona_data in default_personas:
            persona = Persona(
                name=persona_data['name'],
                age=persona_data['age'],
                platform_type=persona_data['platform_type'],
                personality_traits=json.dumps(persona_data['personality_traits']),
                language_style=json.dumps(persona_data['language_style']),
                response_patterns=json.dumps(persona_data['response_patterns'])
            )
            db.session.add(persona)
        
        db.session.commit()
        print("Default personas created successfully!")

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'status': 'Connected to AI Honeytrap Network'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Clean up any session data
    for session_id, data in list(active_sessions.items()):
        if data.get('socket_id') == request.sid:
            active_sessions[session_id]['connected'] = False
            print(f'Marked session {session_id} as disconnected')
            break

@socketio.on('join_chat')
def handle_join_chat(data):
    """Handle client joining a chat session"""
    try:
        platform_type = data.get('platform_type', 'discord')
        
        # Create new chat session
        session_id = str(uuid.uuid4())
        persona = ai_engine.get_random_persona(platform_type)
        
        # Create database session
        chat_session = ChatSession(
            session_id=session_id,
            persona_id=persona['id'],
            user_ip=request.environ.get('REMOTE_ADDR', 'unknown'),
            escalation_level=0
        )
        db.session.add(chat_session)
        db.session.commit()
        
        # Store session info
        active_sessions[session_id] = {
            'socket_id': request.sid,
            'persona': persona,
            'platform_type': platform_type,
            'connected': True,
            'escalation_level': 0
        }
        
        # Join the session room
        join_room(session_id)
        
        # Send initial greeting
        greeting = ai_engine.get_greeting(persona)
        
        # Save greeting message
        greeting_msg = ChatMessage(
            session_id=session_id,
            sender_type='decoy',
            message_content=greeting,
            timestamp=datetime.utcnow()
        )
        db.session.add(greeting_msg)
        db.session.commit()
        
        emit('chat_joined', {
            'session_id': session_id,
            'persona': persona,
            'greeting': greeting
        })
        
        print(f'Client {request.sid} joined chat session {session_id}')
        
    except Exception as e:
        print(f'Error in join_chat: {str(e)}')
        emit('error', {'message': 'Failed to join chat session'})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming chat messages"""
    try:
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not session_id or not message:
            emit('error', {'message': 'Invalid message data'})
            return
        
        if session_id not in active_sessions:
            emit('error', {'message': 'Session not found'})
            return
        
        session_data = active_sessions[session_id]
        persona = session_data['persona']
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            sender_type='user',
            message_content=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(user_msg)
        
        # Emit user message to room
        emit('message_received', {
            'id': str(uuid.uuid4()),
            'sender_type': 'user',
            'message_content': message,
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id)
        
        # Show typing indicator
        emit('typing_start', {'persona': persona['name']}, room=session_id)
        
        # Generate AI response with realistic delay
        socketio.sleep(1 + (len(message) * 0.02))  # Realistic reading time
        
        response_data = ai_engine.generate_response(message, persona, session_id)
        ai_response = response_data['response']
        threat_level = response_data['threat_level']
        
        # Update escalation level if needed
        if threat_level > session_data['escalation_level']:
            session_data['escalation_level'] = threat_level
            
            # Update database
            chat_session = ChatSession.query.filter_by(session_id=session_id).first()
            if chat_session:
                chat_session.escalation_level = threat_level
                db.session.commit()
        
        # Save AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            sender_type='decoy',
            message_content=ai_response,
            timestamp=datetime.utcnow(),
            threat_level=threat_level
        )
        db.session.add(ai_msg)
        db.session.commit()
        
        # Simulate typing time based on response length
        typing_time = 0.5 + (len(ai_response) * 0.05)  # Realistic typing speed
        socketio.sleep(typing_time)
        
        emit('typing_stop', room=session_id)
        
        # Send AI response
        emit('message_received', {
            'id': str(uuid.uuid4()),
            'sender_type': 'decoy',
            'message_content': ai_response,
            'timestamp': datetime.utcnow().isoformat(),
            'threat_level': threat_level,
            'persona': persona
        }, room=session_id)
        
        # Handle evidence capture for high-risk messages
        if threat_level >= 2:
            capture_evidence_websocket(session_id, message, ai_response, threat_level)
            
            # Notify admin dashboard
            emit('high_risk_alert', {
                'session_id': session_id,
                'threat_level': threat_level,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'persona': persona
            }, room='admin_room')
        
        print(f'Message processed for session {session_id}, threat level: {threat_level}')
        
    except Exception as e:
        print(f'Error in send_message: {str(e)}')
        emit('error', {'message': 'Failed to process message'})

@socketio.on('join_admin')
def handle_join_admin():
    """Handle admin joining for real-time monitoring"""
    join_room('admin_room')
    emit('admin_joined', {'status': 'Connected to admin monitoring'})
    
    # Send current active sessions
    active_count = len([s for s in active_sessions.values() if s.get('connected', False)])
    emit('session_stats', {
        'active_sessions': active_count,
        'total_sessions': len(active_sessions)
    })
    
    print(f'Admin client {request.sid} joined monitoring room')

def capture_evidence_websocket(session_id, user_message, ai_response, threat_level):
    """Capture evidence for high-risk interactions"""
    try:
        # Get the database session ID
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            print(f'Chat session not found for evidence capture: {session_id}')
            return
        
        # Create evidence content
        evidence_content = json.dumps({
            'user_message': user_message,
            'ai_response': ai_response,
            'threat_level': threat_level,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        })
        
        # Create evidence metadata
        evidence_metadata_content = json.dumps({
            'escalation_trigger': 'threat_level_' + str(threat_level),
            'analysis_confidence': 0.85,
            'capture_method': 'websocket_realtime',
            'keywords_detected': get_detected_keywords(user_message),
            'risk_assessment': get_risk_assessment(threat_level)
        })
        
        # Generate hash for integrity
        import hashlib
        hash_value = hashlib.sha256(evidence_content.encode()).hexdigest()
        
        evidence = Evidence(
            session_id=chat_session.id,  # Use the database ID, not the session_id string
            evidence_type='high_risk_conversation',
            content=evidence_content,
            evidence_metadata=evidence_metadata_content,
            hash_value=hash_value
        )
        db.session.add(evidence)
        db.session.commit()
        print(f'Evidence captured for session {session_id} (DB ID: {chat_session.id})')
    except Exception as e:
        print(f'Error capturing evidence: {str(e)}')

def get_detected_keywords(message):
    """Extract detected threat keywords from message"""
    threat_keywords = [
        'meet', 'meet up', 'come over', 'my place', 'your place',
        'secret', 'don\'t tell', 'between us', 'our secret',
        'send photo', 'send pic', 'picture', 'selfie', 'video call',
        'address', 'where do you live', 'location'
    ]
    
    detected = []
    message_lower = message.lower()
    for keyword in threat_keywords:
        if keyword in message_lower:
            detected.append(keyword)
    
    return detected

def get_risk_assessment(threat_level):
    """Get risk assessment description based on threat level"""
    if threat_level >= 2:
        return 'HIGH_RISK - Immediate attention required'
    elif threat_level == 1:
        return 'SUSPICIOUS - Monitor closely'
    else:
        return 'NORMAL - No immediate concern'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)

