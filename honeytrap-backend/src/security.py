import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify, current_app

class SecurityManager:
    """Handles encryption, decryption, and security operations for the honeytrap system"""
    
    def __init__(self, master_key=None):
        """Initialize security manager with encryption key"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Generate a secure master key for development
            self.master_key = os.environ.get('HONEYTRAP_MASTER_KEY', 'hampshire_police_secure_key_2024').encode()
        
        # Derive encryption key from master key
        self.salt = b'hampshire_police_salt_2024'  # In production, use random salt per installation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.cipher_suite = Fernet(key)
    
    def encrypt_data(self, data):
        """Encrypt sensitive data using AES-256"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            elif not isinstance(data, str):
                data = str(data)
            
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None
    
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
    
    def generate_session_token(self, user_id, role='admin'):
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=8)  # 8 hour expiry
        }
        
        secret_key = os.environ.get('JWT_SECRET_KEY', 'hampshire_police_jwt_secret_2024')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def verify_session_token(self, token):
        """Verify JWT session token"""
        try:
            secret_key = os.environ.get('JWT_SECRET_KEY', 'hampshire_police_jwt_secret_2024')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_evidence_hash(self, evidence_data):
        """Generate SHA-256 hash for evidence integrity"""
        if isinstance(evidence_data, dict):
            evidence_data = json.dumps(evidence_data, sort_keys=True)
        return hashlib.sha256(evidence_data.encode()).hexdigest()
    
    def verify_evidence_integrity(self, evidence_data, stored_hash):
        """Verify evidence hasn't been tampered with"""
        current_hash = self.generate_evidence_hash(evidence_data)
        return current_hash == stored_hash
    
    def sanitize_input(self, input_data):
        """Sanitize user input to prevent injection attacks"""
        if isinstance(input_data, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
            for char in dangerous_chars:
                input_data = input_data.replace(char, '')
            return input_data.strip()
        return input_data
    
    def log_security_event(self, event_type, details, ip_address=None):
        """Log security-related events for audit trail"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'ip_address': ip_address or 'unknown',
            'hash': self.generate_evidence_hash(f"{event_type}:{details}:{datetime.utcnow().isoformat()}")
        }
        
        # In production, this would write to a secure log file or database
        print(f"SECURITY LOG: {json.dumps(log_entry)}")
        return log_entry

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication for admin endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        security_manager = SecurityManager()
        payload = security_manager.verify_session_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

# Rate limiting decorator
def rate_limit(max_requests=100, window_minutes=60):
    """Simple rate limiting decorator"""
    request_counts = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = datetime.utcnow()
            
            # Clean old entries
            cutoff_time = current_time - timedelta(minutes=window_minutes)
            request_counts[client_ip] = [
                req_time for req_time in request_counts.get(client_ip, [])
                if req_time > cutoff_time
            ]
            
            # Check rate limit
            if len(request_counts.get(client_ip, [])) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Initialize global security manager
security_manager = SecurityManager()

