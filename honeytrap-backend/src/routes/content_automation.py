from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.profile import DecoyProfile, ProfileContent
from src.services.content_automation import ContentAutomationService
from src.security import require_auth, log_security_event
from datetime import datetime, timedelta
import json

content_automation_bp = Blueprint('content_automation', __name__)
automation_service = ContentAutomationService()

@content_automation_bp.route('/content-automation/start', methods=['POST'])
@require_auth
def start_automation():
    """Start the content automation service"""
    try:
        result = automation_service.start_automation_service()
        
        log_security_event('automation_service_started', {
            'status': result['status'],
            'user_ip': request.remote_addr
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/stop', methods=['POST'])
@require_auth
def stop_automation():
    """Stop the content automation service"""
    try:
        result = automation_service.stop_automation_service()
        
        log_security_event('automation_service_stopped', {
            'status': result['status'],
            'user_ip': request.remote_addr
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/status', methods=['GET'])
@require_auth
def get_automation_status():
    """Get automation service status"""
    try:
        status = automation_service.get_automation_status()
        statistics = automation_service.get_content_statistics()
        
        return jsonify({
            'automation_status': status,
            'content_statistics': statistics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/generate-content/<int:profile_id>', methods=['POST'])
@require_auth
def generate_content(profile_id):
    """Generate content for a specific profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json() or {}
        
        content_type = data.get('content_type')
        content_data = automation_service.generate_content_for_profile(profile, content_type)
        
        if 'error' in content_data:
            return jsonify(content_data), 400
        
        log_security_event('content_generated', {
            'profile_id': profile_id,
            'content_type': content_data.get('content_type'),
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Content generated successfully',
            'content': content_data,
            'profile': {
                'id': profile.id,
                'username': profile.username,
                'platform_type': profile.platform_type
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/schedule-content/<int:profile_id>', methods=['POST'])
@require_auth
def schedule_content(profile_id):
    """Schedule content for posting"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        # Parse schedule time
        schedule_time_str = data.get('schedule_time')
        if schedule_time_str:
            schedule_time = datetime.fromisoformat(schedule_time_str)
        else:
            # Default to next optimal time
            schedule_time = datetime.now() + timedelta(hours=1)
        
        # Get content data
        content_data = data.get('content_data', {})
        
        result = automation_service.schedule_content_for_profile(
            profile_id, 
            content_data, 
            schedule_time
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        log_security_event('content_scheduled', {
            'profile_id': profile_id,
            'content_id': result['content_id'],
            'schedule_time': schedule_time.isoformat(),
            'user_ip': request.remote_addr
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/generate-calendar/<int:profile_id>', methods=['POST'])
@require_auth
def generate_content_calendar(profile_id):
    """Generate content calendar for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json() or {}
        
        days = data.get('days', 30)
        if days > 90:  # Limit calendar length
            days = 90
        
        calendar_data = automation_service.generate_content_calendar(profile_id, days)
        
        if 'error' in calendar_data:
            return jsonify(calendar_data), 400
        
        log_security_event('calendar_generated', {
            'profile_id': profile_id,
            'days': days,
            'total_posts': calendar_data['total_posts'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Content calendar generated for {days} days',
            'calendar': calendar_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/auto-schedule-calendar/<int:profile_id>', methods=['POST'])
@require_auth
def auto_schedule_calendar(profile_id):
    """Automatically schedule content from calendar"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        calendar_data = data.get('calendar', [])
        if not calendar_data:
            return jsonify({'error': 'Calendar data is required'}), 400
        
        result = automation_service.auto_schedule_calendar(profile_id, calendar_data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        log_security_event('calendar_auto_scheduled', {
            'profile_id': profile_id,
            'scheduled_count': result['scheduled_count'],
            'success_rate': result['success_rate'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Auto-scheduled {result["scheduled_count"]} content items',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/scheduled-content/<int:profile_id>', methods=['GET'])
@require_auth
def get_scheduled_content(profile_id):
    """Get scheduled content for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Get query parameters
        status = request.args.get('status', 'scheduled')
        days_ahead = int(request.args.get('days_ahead', 30))
        
        # Query scheduled content
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        content_query = ProfileContent.query.filter(
            ProfileContent.profile_id == profile_id,
            ProfileContent.scheduled_time <= end_date
        )
        
        if status != 'all':
            content_query = content_query.filter(ProfileContent.status == status)
        
        content_items = content_query.order_by(ProfileContent.scheduled_time).all()
        
        # Format response
        scheduled_content = []
        for item in content_items:
            scheduled_content.append({
                'id': item.id,
                'content_type': item.content_type,
                'content_text': item.content_text,
                'scheduled_time': item.scheduled_time.isoformat(),
                'status': item.status,
                'posted_time': item.posted_time.isoformat() if item.posted_time else None,
                'likes_count': item.likes_count,
                'comments_count': item.comments_count
            })
        
        return jsonify({
            'profile_id': profile_id,
            'profile_username': profile.username,
            'content_count': len(scheduled_content),
            'scheduled_content': scheduled_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/content/<int:content_id>', methods=['PUT'])
@require_auth
def update_scheduled_content(content_id):
    """Update scheduled content"""
    try:
        content = ProfileContent.query.get_or_404(content_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'content_text' in data:
            content.content_text = data['content_text']
        
        if 'scheduled_time' in data:
            content.scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        
        if 'status' in data and data['status'] in ['scheduled', 'cancelled']:
            content.status = data['status']
        
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_security_event('content_updated', {
            'content_id': content_id,
            'profile_id': content.profile_id,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Content updated successfully',
            'content': {
                'id': content.id,
                'content_text': content.content_text,
                'scheduled_time': content.scheduled_time.isoformat(),
                'status': content.status
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/content/<int:content_id>', methods=['DELETE'])
@require_auth
def delete_scheduled_content(content_id):
    """Delete scheduled content"""
    try:
        content = ProfileContent.query.get_or_404(content_id)
        
        # Only allow deletion of scheduled or failed content
        if content.status not in ['scheduled', 'failed', 'cancelled']:
            return jsonify({'error': 'Cannot delete posted content'}), 400
        
        profile_id = content.profile_id
        db.session.delete(content)
        db.session.commit()
        
        log_security_event('content_deleted', {
            'content_id': content_id,
            'profile_id': profile_id,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Content deleted successfully',
            'content_id': content_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/analyze-performance/<int:profile_id>', methods=['GET'])
@require_auth
def analyze_content_performance(profile_id):
    """Analyze content performance for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        days = int(request.args.get('days', 30))
        analysis = automation_service.analyze_content_performance(profile_id, days)
        
        return jsonify({
            'profile': {
                'id': profile.id,
                'username': profile.username,
                'platform_type': profile.platform_type
            },
            'performance_analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/templates', methods=['GET'])
@require_auth
def get_content_templates():
    """Get available content templates"""
    try:
        platform = request.args.get('platform')
        age_group = request.args.get('age_group')
        
        templates = automation_service.content_templates
        
        # Filter by platform if specified
        if platform:
            templates = {platform: templates.get(platform, {})}
        
        # Filter by age group if specified
        if age_group:
            filtered_templates = {}
            for p, platform_data in templates.items():
                if age_group in platform_data:
                    filtered_templates[p] = {age_group: platform_data[age_group]}
            templates = filtered_templates
        
        return jsonify({
            'templates': templates,
            'available_platforms': list(automation_service.content_templates.keys()),
            'available_age_groups': ['13-14', '15-16', 'general']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/templates', methods=['POST'])
@require_auth
def create_custom_template():
    """Create custom content template"""
    try:
        data = request.get_json()
        
        platform = data.get('platform')
        age_group = data.get('age_group')
        content_type = data.get('content_type')
        templates = data.get('templates', [])
        
        if not all([platform, age_group, content_type, templates]):
            return jsonify({'error': 'All fields are required'}), 400
        
        result = automation_service.create_custom_content_template(
            platform, age_group, content_type, templates
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        log_security_event('custom_template_created', {
            'platform': platform,
            'age_group': age_group,
            'content_type': content_type,
            'template_count': len(templates),
            'user_ip': request.remote_addr
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/posting-patterns', methods=['GET'])
@require_auth
def get_posting_patterns():
    """Get posting patterns for platforms"""
    try:
        patterns = automation_service.posting_patterns
        
        return jsonify({
            'posting_patterns': patterns,
            'pattern_explanation': {
                'frequency': {
                    'multiple_daily': '2-4 posts per day',
                    'daily': '1 post per day',
                    'few_times_weekly': '2-3 posts per week',
                    'weekly': '1 post per week'
                },
                'peak_times': 'Optimal posting times for engagement',
                'content_mix': 'Percentage distribution of content types',
                'response_likelihood': 'Probability of receiving responses'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/bulk-generate', methods=['POST'])
@require_auth
def bulk_generate_content():
    """Generate content for multiple profiles"""
    try:
        data = request.get_json()
        profile_ids = data.get('profile_ids', [])
        content_count = data.get('content_count', 5)
        
        if not profile_ids:
            return jsonify({'error': 'Profile IDs are required'}), 400
        
        if len(profile_ids) > 20:  # Limit bulk operations
            return jsonify({'error': 'Maximum 20 profiles per bulk operation'}), 400
        
        results = []
        
        for profile_id in profile_ids:
            try:
                profile = DecoyProfile.query.get(profile_id)
                if not profile:
                    results.append({
                        'profile_id': profile_id,
                        'error': 'Profile not found'
                    })
                    continue
                
                profile_content = []
                for _ in range(content_count):
                    content_data = automation_service.generate_content_for_profile(profile)
                    if 'error' not in content_data:
                        profile_content.append(content_data)
                
                results.append({
                    'profile_id': profile_id,
                    'username': profile.username,
                    'generated_content': profile_content,
                    'success_count': len(profile_content)
                })
                
            except Exception as e:
                results.append({
                    'profile_id': profile_id,
                    'error': str(e)
                })
        
        log_security_event('bulk_content_generated', {
            'profile_count': len(profile_ids),
            'content_per_profile': content_count,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Bulk content generation completed for {len(profile_ids)} profiles',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/emergency-stop', methods=['POST'])
@require_auth
def emergency_stop_all():
    """Emergency stop all automation and cancel scheduled content"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Emergency stop requested')
        
        # Stop automation service
        automation_service.stop_automation_service()
        
        # Cancel all scheduled content
        scheduled_content = ProfileContent.query.filter_by(status='scheduled').all()
        cancelled_count = 0
        
        for content in scheduled_content:
            content.status = 'cancelled'
            cancelled_count += 1
        
        db.session.commit()
        
        log_security_event('emergency_stop_all', {
            'reason': reason,
            'cancelled_content_count': cancelled_count,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Emergency stop completed',
            'automation_stopped': True,
            'cancelled_content_count': cancelled_count,
            'reason': reason
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_automation_bp.route('/content-automation/content-variables', methods=['GET'])
@require_auth
def get_content_variables():
    """Get available content variables for templates"""
    try:
        variables = automation_service.content_variables
        
        return jsonify({
            'content_variables': variables,
            'usage_examples': {
                'activities': 'Use {activity} in templates for random activities',
                'games': 'Use {game} for popular games among teens',
                'subjects': 'Use {subject} for school subjects',
                'moods': 'Use {mood} for emotional states',
                'interests': 'Use {interest} for hobbies and interests'
            },
            'template_syntax': {
                'placeholders': 'Use {variable_name} for dynamic content',
                'example': 'just finished {activity} and feeling {mood}!'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

