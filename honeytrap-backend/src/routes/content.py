from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.profile import DecoyProfile, ProfileContent
from src.services.content_manager import ContentManager
from src.security import require_auth, log_security_event
from datetime import datetime, timedelta
import json

content_bp = Blueprint('content', __name__)
content_manager = ContentManager()

@content_bp.route('/content/generate', methods=['POST'])
@require_auth
def generate_content():
    """Generate content for a specific profile"""
    try:
        data = request.get_json()
        profile_id = data.get('profile_id')
        content_type = data.get('content_type', 'post')
        
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Generate content
        content_data = content_manager.generate_content(profile, content_type)
        
        # Save to database
        content = content_manager.save_content_to_database(content_data)
        
        log_security_event('content_generated', {
            'profile_id': profile_id,
            'content_type': content_type,
            'platform_type': profile.platform_type,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Content generated successfully',
            'content': content.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/schedule', methods=['POST'])
@require_auth
def create_content_schedule():
    """Create a content schedule for a profile"""
    try:
        data = request.get_json()
        profile_id = data.get('profile_id')
        days = data.get('days', 7)
        
        if days > 30:  # Limit schedule length
            return jsonify({'error': 'Maximum schedule length is 30 days'}), 400
        
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Generate content schedule
        content_schedule = content_manager.create_content_schedule(profile, days)
        
        # Save to database
        saved_content = content_manager.save_content_schedule(content_schedule)
        
        log_security_event('content_schedule_created', {
            'profile_id': profile_id,
            'days': days,
            'content_count': len(saved_content),
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Content schedule created for {days} days',
            'content_count': len(saved_content),
            'content': [content.to_dict() for content in saved_content]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/pending', methods=['GET'])
@require_auth
def get_pending_content():
    """Get content ready to be posted"""
    try:
        platform = request.args.get('platform')
        
        pending_content = content_manager.get_pending_content(platform)
        
        return jsonify({
            'pending_content': [content.to_dict() for content in pending_content],
            'count': len(pending_content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>/post', methods=['POST'])
@require_auth
def mark_content_posted(content_id):
    """Mark content as posted"""
    try:
        data = request.get_json()
        engagement_data = data.get('engagement_data', {})
        
        success = content_manager.mark_content_posted(content_id, engagement_data)
        
        if success:
            log_security_event('content_posted', {
                'content_id': content_id,
                'engagement_data': engagement_data,
                'user_ip': request.remote_addr
            })
            
            return jsonify({'message': 'Content marked as posted'})
        else:
            return jsonify({'error': 'Content not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/profile/<int:profile_id>', methods=['GET'])
@require_auth
def get_profile_content(profile_id):
    """Get all content for a specific profile"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')
        
        query = ProfileContent.query.filter_by(profile_id=profile_id)
        
        if status:
            query = query.filter(ProfileContent.status == status)
        
        content = query.order_by(ProfileContent.scheduled_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'content': [item.to_dict() for item in content.items],
            'total': content.total,
            'pages': content.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['PUT'])
@require_auth
def update_content(content_id):
    """Update content before posting"""
    try:
        content = ProfileContent.query.get_or_404(content_id)
        data = request.get_json()
        
        # Only allow updates if content hasn't been posted
        if content.status == 'posted':
            return jsonify({'error': 'Cannot update posted content'}), 400
        
        # Update allowed fields
        updatable_fields = [
            'content_text', 'scheduled_time', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'scheduled_time':
                    setattr(content, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(content, field, data[field])
        
        if 'content_media' in data:
            content.content_media = json.dumps(data['content_media'])
        
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_security_event('content_updated', {
            'content_id': content_id,
            'updated_fields': list(data.keys()),
            'user_ip': request.remote_addr
        })
        
        return jsonify(content.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['DELETE'])
@require_auth
def delete_content(content_id):
    """Delete content"""
    try:
        content = ProfileContent.query.get_or_404(content_id)
        
        # Only allow deletion if content hasn't been posted
        if content.status == 'posted':
            return jsonify({'error': 'Cannot delete posted content'}), 400
        
        log_security_event('content_deleted', {
            'content_id': content_id,
            'profile_id': content.profile_id,
            'user_ip': request.remote_addr
        })
        
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({'message': 'Content deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/stats', methods=['GET'])
@require_auth
def get_content_stats():
    """Get content statistics"""
    try:
        # Overall stats
        stats = {
            'total_content': ProfileContent.query.count(),
            'scheduled_content': ProfileContent.query.filter_by(status='scheduled').count(),
            'posted_content': ProfileContent.query.filter_by(status='posted').count(),
            'draft_content': ProfileContent.query.filter_by(status='draft').count(),
            'platform_breakdown': {},
            'content_type_breakdown': {}
        }
        
        # Platform breakdown
        platforms = db.session.query(
            ProfileContent.platform_type,
            db.func.count(ProfileContent.id)
        ).group_by(ProfileContent.platform_type).all()
        
        for platform, count in platforms:
            stats['platform_breakdown'][platform] = count
        
        # Content type breakdown
        content_types = db.session.query(
            ProfileContent.content_type,
            db.func.count(ProfileContent.id)
        ).group_by(ProfileContent.content_type).all()
        
        for content_type, count in content_types:
            stats['content_type_breakdown'][content_type] = count
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_posts = ProfileContent.query.filter(
            ProfileContent.posted_time >= week_ago,
            ProfileContent.status == 'posted'
        ).count()
        
        stats['recent_posts'] = recent_posts
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/templates', methods=['GET'])
@require_auth
def get_content_templates():
    """Get available content templates"""
    try:
        platform = request.args.get('platform')
        
        if platform:
            templates = content_manager.content_templates.get(platform, {})
        else:
            templates = content_manager.content_templates
        
        return jsonify({
            'templates': templates,
            'variables': content_manager.content_variables
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

