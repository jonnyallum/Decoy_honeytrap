"""
Session Management API Routes
Provides endpoints for managing social media sessions and account switching
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging

from services.session_manager import session_manager
from security import require_auth, require_admin


# Create blueprint
session_management_bp = Blueprint('session_management', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@session_management_bp.route('/sessions', methods=['POST'])
@require_auth
def create_session():
    """Create a new social media session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['account_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get user ID from session (would be from authentication)
        user_id = session.get('user_id', 'default_user')
        
        # Create session
        session_id = session_manager.create_session(
            user_id=user_id,
            account_id=data['account_id'],
            session_type=data.get('session_type', 'api')
        )
        
        # Get session info
        session_info = session_manager.get_session_info(session_id)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return jsonify({
            "session_id": session_id,
            "session_info": session_info
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({"error": "Failed to create session"}), 500


@session_management_bp.route('/sessions/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """Get session information"""
    try:
        session_info = session_manager.get_session_info(session_id)
        
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        # Verify user has access to this session
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify(session_info), 200
        
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        return jsonify({"error": "Failed to retrieve session"}), 500


@session_management_bp.route('/sessions', methods=['GET'])
@require_auth
def get_user_sessions():
    """Get all sessions for the current user"""
    try:
        user_id = session.get('user_id', 'default_user')
        sessions = session_manager.get_user_sessions(user_id)
        
        return jsonify({
            "sessions": sessions,
            "total": len(sessions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        return jsonify({"error": "Failed to retrieve sessions"}), 500


@session_management_bp.route('/sessions/<session_id>/switch', methods=['POST'])
@require_auth
def switch_session(session_id):
    """Switch to a different session"""
    try:
        user_id = session.get('user_id', 'default_user')
        
        result = session_manager.switch_session(user_id, session_id)
        
        # Update current session in Flask session
        session['current_social_session'] = session_id
        
        logger.info(f"User {user_id} switched to session {session_id}")
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error switching to session {session_id}: {e}")
        return jsonify({"error": "Failed to switch session"}), 500


@session_management_bp.route('/sessions/<session_id>/extend', methods=['POST'])
@require_auth
def extend_session(session_id):
    """Extend session timeout"""
    try:
        data = request.get_json() or {}
        extension_seconds = data.get('extension_seconds', 3600)
        
        # Verify user has access to this session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        success = session_manager.extend_session(session_id, extension_seconds)
        
        if success:
            updated_info = session_manager.get_session_info(session_id)
            return jsonify({
                "message": "Session extended successfully",
                "new_expires_at": updated_info['expires_at']
            }), 200
        else:
            return jsonify({"error": "Failed to extend session"}), 400
        
    except Exception as e:
        logger.error(f"Error extending session {session_id}: {e}")
        return jsonify({"error": "Failed to extend session"}), 500


@session_management_bp.route('/sessions/<session_id>/action', methods=['POST'])
@require_auth
def perform_action(session_id):
    """Perform an action using a session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'action' not in data:
            return jsonify({"error": "Missing required field: action"}), 400
        
        # Verify user has access to this session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        # Perform action
        result = session_manager.perform_action(
            session_id=session_id,
            action=data['action'],
            parameters=data.get('parameters', {})
        )
        
        logger.info(f"Performed action {data['action']} on session {session_id}")
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error performing action on session {session_id}: {e}")
        return jsonify({"error": "Failed to perform action"}), 500


@session_management_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
def close_session(session_id):
    """Close a session"""
    try:
        # Verify user has access to this session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        success = session_manager.close_session(session_id)
        
        if success:
            # Clear from Flask session if it was the current session
            if session.get('current_social_session') == session_id:
                session.pop('current_social_session', None)
            
            logger.info(f"Closed session {session_id}")
            return jsonify({"message": "Session closed successfully"}), 200
        else:
            return jsonify({"error": "Failed to close session"}), 400
        
    except Exception as e:
        logger.error(f"Error closing session {session_id}: {e}")
        return jsonify({"error": "Failed to close session"}), 500


@session_management_bp.route('/sessions/stats', methods=['GET'])
@require_auth
def get_session_stats():
    """Get session statistics"""
    try:
        stats = session_manager.get_session_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        return jsonify({"error": "Failed to get statistics"}), 500


@session_management_bp.route('/sessions/cleanup', methods=['POST'])
@require_admin
def cleanup_sessions():
    """Clean up expired sessions"""
    try:
        session_manager.cleanup_expired_sessions()
        
        logger.info("Session cleanup completed")
        
        return jsonify({"message": "Session cleanup completed"}), 200
        
    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        return jsonify({"error": "Session cleanup failed"}), 500


@session_management_bp.route('/sessions/current', methods=['GET'])
@require_auth
def get_current_session():
    """Get current active session for user"""
    try:
        current_session_id = session.get('current_social_session')
        
        if not current_session_id:
            return jsonify({"current_session": None}), 200
        
        session_info = session_manager.get_session_info(current_session_id)
        
        if not session_info or not session_manager.is_session_active(current_session_id):
            # Clear invalid session
            session.pop('current_social_session', None)
            return jsonify({"current_session": None}), 200
        
        return jsonify({
            "current_session": session_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting current session: {e}")
        return jsonify({"error": "Failed to get current session"}), 500


@session_management_bp.route('/sessions/<session_id>/activity', methods=['GET'])
@require_auth
def get_session_activity(session_id):
    """Get session activity log"""
    try:
        # Verify user has access to this session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        # Get activity log
        activity_log = session_info.get('activity_log', [])
        
        return jsonify({
            "session_id": session_id,
            "activity_log": activity_log,
            "total_activities": len(activity_log)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting session activity {session_id}: {e}")
        return jsonify({"error": "Failed to get session activity"}), 500


@session_management_bp.route('/sessions/<session_id>/capabilities', methods=['GET'])
@require_auth
def get_session_capabilities(session_id):
    """Get session capabilities and rate limits"""
    try:
        # Verify user has access to this session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404
        
        user_id = session.get('user_id', 'default_user')
        if session_info['user_id'] != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify({
            "session_id": session_id,
            "capabilities": session_info.get('capabilities', []),
            "rate_limits": session_info.get('rate_limits', {}),
            "session_type": session_info.get('session_type', 'unknown')
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting session capabilities {session_id}: {e}")
        return jsonify({"error": "Failed to get session capabilities"}), 500


# Error handlers
@session_management_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@session_management_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@session_management_bp.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@session_management_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@session_management_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

