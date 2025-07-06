import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.chat import ChatSession, ChatMessage, Persona, Evidence, AuditLog
from src.routes.user import user_bp
from src.routes.chat import chat_bp
from src.routes.admin import admin_bp
import json

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'honeytrap-secure-key-2024-hampshire-police'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
    app.run(host='0.0.0.0', port=5001, debug=True)
