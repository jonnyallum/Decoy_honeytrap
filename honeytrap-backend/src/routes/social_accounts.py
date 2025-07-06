"""
Social Media Account Management API Routes
Provides endpoints for managing social media accounts and authentication
"""

from flask import Blueprint, request, jsonify, redirect, session
from datetime import datetime
import logging

from models.social_account import account_manager
from services.social_auth_manager import auth_manager
from security import require_auth, require_admin


# Create blueprint
social_accounts_bp = Blueprint('social_accounts', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@social_accounts_bp.route('/accounts', methods=['GET'])
@require_auth
def get_accounts():
    """Get all social media accounts"""
    try:
        # Get query parameters
        platform = request.args.get('platform')
        profile_id = request.args.get('profile_id')
        status = request.args.get('status')
        
        # Get accounts based on filters
        if platform:
            accounts = account_manager.get_accounts_by_platform(platform)
        elif profile_id:
            accounts = account_manager.get_accounts_by_profile(profile_id)
        else:
            accounts = list(account_manager.accounts.values())
        
        # Filter by status if specified
        if status:
            accounts = [acc for acc in accounts if acc.status == status]
        
        # Convert to dict representation
        accounts_data = [acc.to_dict() for acc in accounts]
        
        return jsonify({
            "accounts": accounts_data,
            "total": len(accounts_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        return jsonify({"error": "Failed to retrieve accounts"}), 500


@social_accounts_bp.route('/accounts/<account_id>', methods=['GET'])
@require_auth
def get_account(account_id):
    """Get specific social media account"""
    try:
        account = account_manager.get_account(account_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404
        
        # Include sensitive data for authorized users
        include_sensitive = request.args.get('include_sensitive', 'false').lower() == 'true'
        
        return jsonify(account.to_dict(include_sensitive=include_sensitive)), 200
        
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}")
        return jsonify({"error": "Failed to retrieve account"}), 500


@social_accounts_bp.route('/accounts', methods=['POST'])
@require_auth
def create_account():
    """Create a new social media account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['platform', 'username']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create account
        account = account_manager.create_account(
            platform=data['platform'],
            username=data['username'],
            email=data.get('email', ''),
            display_name=data.get('display_name', ''),
            profile_id=data.get('profile_id')
        )
        
        logger.info(f"Created account {account.id} for platform {account.platform}")
        
        return jsonify(account.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        return jsonify({"error": "Failed to create account"}), 500


@social_accounts_bp.route('/accounts/<account_id>', methods=['PUT'])
@require_auth
def update_account(account_id):
    """Update social media account"""
    try:
        data = request.get_json()
        
        success = account_manager.update_account(account_id, data)
        if not success:
            return jsonify({"error": "Account not found"}), 404
        
        account = account_manager.get_account(account_id)
        logger.info(f"Updated account {account_id}")
        
        return jsonify(account.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}")
        return jsonify({"error": "Failed to update account"}), 500


@social_accounts_bp.route('/accounts/<account_id>', methods=['DELETE'])
@require_auth
def delete_account(account_id):
    """Delete social media account"""
    try:
        success = account_manager.delete_account(account_id)
        if not success:
            return jsonify({"error": "Account not found"}), 404
        
        logger.info(f"Deleted account {account_id}")
        
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}")
        return jsonify({"error": "Failed to delete account"}), 500


@social_accounts_bp.route('/auth/platforms', methods=['GET'])
@require_auth
def get_supported_platforms():
    """Get list of supported platforms"""
    try:
        platforms = auth_manager.get_supported_platforms()
        return jsonify({"platforms": platforms}), 200
        
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        return jsonify({"error": "Failed to retrieve platforms"}), 500


@social_accounts_bp.route('/auth/oauth/<platform>', methods=['GET'])
@require_auth
def start_oauth_login(platform):
    """Start OAuth login process for a platform"""
    try:
        account_id = request.args.get('account_id')
        
        auth_url, state = auth_manager.get_oauth_url(platform, account_id)
        
        # Store state in session for security
        session[f'oauth_state_{platform}'] = state
        
        return jsonify({
            "auth_url": auth_url,
            "state": state,
            "platform": platform
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error starting OAuth for {platform}: {e}")
        return jsonify({"error": "Failed to start OAuth process"}), 500


@social_accounts_bp.route('/auth/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    """Handle OAuth callback from social media platform"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            logger.error(f"OAuth error for {platform}: {error}")
            return redirect(f"/admin/accounts?error={error}")
        
        if not code or not state:
            return jsonify({"error": "Missing authorization code or state"}), 400
        
        # Verify state parameter
        session_state = session.get(f'oauth_state_{platform}')
        if not session_state or session_state != state:
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Handle OAuth callback
        result = auth_manager.handle_oauth_callback(platform, code, state)
        
        # Clean up session
        session.pop(f'oauth_state_{platform}', None)
        
        logger.info(f"OAuth login successful for {platform}: {result['username']}")
        
        # Redirect to frontend with success
        return redirect(f"/admin/accounts?success=true&account_id={result['account_id']}")
        
    except ValueError as e:
        logger.error(f"OAuth callback error for {platform}: {e}")
        return redirect(f"/admin/accounts?error={str(e)}")
    except Exception as e:
        logger.error(f"OAuth callback error for {platform}: {e}")
        return redirect(f"/admin/accounts?error=authentication_failed")


@social_accounts_bp.route('/auth/credentials', methods=['POST'])
@require_auth
def login_with_credentials():
    """Login using username/password credentials"""
    try:
        data = request.get_json()
        
        required_fields = ['platform', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        result = auth_manager.login_with_credentials(
            platform=data['platform'],
            username=data['username'],
            password=data['password'],
            account_id=data.get('account_id')
        )
        
        logger.info(f"Credential login successful for {data['platform']}: {data['username']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error with credential login: {e}")
        return jsonify({"error": "Login failed"}), 500


@social_accounts_bp.route('/accounts/<account_id>/refresh', methods=['POST'])
@require_auth
def refresh_account_tokens(account_id):
    """Refresh OAuth tokens for an account"""
    try:
        success = auth_manager.refresh_account_tokens(account_id)
        
        if success:
            account = account_manager.get_account(account_id)
            logger.info(f"Refreshed tokens for account {account_id}")
            return jsonify({
                "message": "Tokens refreshed successfully",
                "account": account.to_dict()
            }), 200
        else:
            return jsonify({"error": "Failed to refresh tokens"}), 400
        
    except Exception as e:
        logger.error(f"Error refreshing tokens for {account_id}: {e}")
        return jsonify({"error": "Failed to refresh tokens"}), 500


@social_accounts_bp.route('/accounts/<account_id>/logout', methods=['POST'])
@require_auth
def logout_account(account_id):
    """Logout an account"""
    try:
        success = auth_manager.logout_account(account_id)
        
        if success:
            logger.info(f"Logged out account {account_id}")
            return jsonify({"message": "Account logged out successfully"}), 200
        else:
            return jsonify({"error": "Account not found"}), 404
        
    except Exception as e:
        logger.error(f"Error logging out account {account_id}: {e}")
        return jsonify({"error": "Failed to logout account"}), 500


@social_accounts_bp.route('/accounts/<account_id>/test', methods=['POST'])
@require_auth
def test_account_connection(account_id):
    """Test account connection"""
    try:
        result = auth_manager.test_account_connection(account_id)
        
        if result["valid"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error testing connection for {account_id}: {e}")
        return jsonify({"error": "Failed to test connection"}), 500


@social_accounts_bp.route('/accounts/<account_id>/capabilities', methods=['GET'])
@require_auth
def get_account_capabilities(account_id):
    """Get account capabilities"""
    try:
        capabilities = auth_manager.get_account_capabilities(account_id)
        
        return jsonify({
            "account_id": account_id,
            "capabilities": capabilities
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting capabilities for {account_id}: {e}")
        return jsonify({"error": "Failed to get capabilities"}), 500


@social_accounts_bp.route('/stats', methods=['GET'])
@require_auth
def get_account_stats():
    """Get account statistics"""
    try:
        stats = account_manager.get_platform_stats()
        
        # Add additional stats
        active_accounts = account_manager.get_active_accounts()
        stats["active_sessions"] = len([acc for acc in active_accounts if acc.is_session_valid()])
        stats["platforms_with_accounts"] = len(stats["platforms"])
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting account stats: {e}")
        return jsonify({"error": "Failed to get statistics"}), 500


@social_accounts_bp.route('/accounts/<account_id>/activity', methods=['GET'])
@require_auth
def get_account_activity(account_id):
    """Get account activity and usage statistics"""
    try:
        account = account_manager.get_account(account_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404
        
        activity_data = {
            "account_id": account_id,
            "platform": account.platform,
            "status": account.status,
            "last_login": account.last_login.isoformat() if account.last_login else None,
            "last_activity": account.last_activity.isoformat() if account.last_activity else None,
            "session_valid": account.is_session_valid(),
            "rate_limits": account.rate_limits,
            "capabilities": account.capabilities,
            "metadata": account.metadata
        }
        
        return jsonify(activity_data), 200
        
    except Exception as e:
        logger.error(f"Error getting activity for {account_id}: {e}")
        return jsonify({"error": "Failed to get account activity"}), 500


@social_accounts_bp.route('/cleanup', methods=['POST'])
@require_admin
def cleanup_expired_data():
    """Clean up expired OAuth states and inactive sessions"""
    try:
        # Clean up expired OAuth states
        auth_manager.cleanup_expired_states()
        
        # Clean up inactive accounts (optional)
        cleanup_count = 0
        for account in list(account_manager.accounts.values()):
            if (account.status == "inactive" and 
                account.last_activity and 
                (datetime.utcnow() - account.last_activity).days > 30):
                # Optionally remove very old inactive accounts
                pass
        
        logger.info("Cleanup completed")
        
        return jsonify({
            "message": "Cleanup completed successfully",
            "cleaned_up": cleanup_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return jsonify({"error": "Cleanup failed"}), 500


# Error handlers
@social_accounts_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@social_accounts_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@social_accounts_bp.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@social_accounts_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@social_accounts_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

