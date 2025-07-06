from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.profile import DecoyProfile, ProfileContent, ProfileAnalytics
from src.services.profile_generator import ProfileGenerator
from src.security import require_auth, log_security_event
from datetime import datetime
import json

profiles_bp = Blueprint('profiles', __name__)
profile_generator = ProfileGenerator()

@profiles_bp.route('/profiles', methods=['GET'])
@require_auth
def get_profiles():
    """Get all decoy profiles with filtering options"""
    try:
        # Get query parameters
        platform = request.args.get('platform')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = DecoyProfile.query
        
        if platform:
            query = query.filter(DecoyProfile.platform_type == platform)
        if status:
            query = query.filter(DecoyProfile.status == status)
        
        # Paginate results
        profiles = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        log_security_event('profile_list_accessed', {
            'user_ip': request.remote_addr,
            'filters': {'platform': platform, 'status': status},
            'total_profiles': profiles.total
        })
        
        return jsonify({
            'profiles': [profile.to_dict() for profile in profiles.items],
            'total': profiles.total,
            'pages': profiles.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/generate', methods=['POST'])
@require_auth
def generate_profile():
    """Generate a new decoy profile"""
    try:
        data = request.get_json()
        
        # Generate profile using ProfileGenerator
        generated_profile = profile_generator.generate_profile(
            platform_type=data.get('platform_type', 'discord'),
            age_range=data.get('age_range', '13-16'),
            gender=data.get('gender'),
            location=data.get('location')
        )
        
        # Create database record
        profile = DecoyProfile(
            name=generated_profile['name'],
            username=generated_profile['username'],
            age=generated_profile['age'],
            location=generated_profile['location'],
            platform_type=generated_profile['platform_type'],
            bio=generated_profile['bio'],
            interests=json.dumps(generated_profile['interests']),
            backstory=generated_profile['backstory'],
            status='created',
            created_by=request.headers.get('X-User-ID', 'system')
        )
        
        db.session.add(profile)
        db.session.commit()
        
        log_security_event('profile_generated', {
            'profile_id': profile.id,
            'platform_type': profile.platform_type,
            'user_ip': request.remote_addr
        })
        
        # Return profile with generation suggestions
        response = profile.to_dict()
        response['image_prompt'] = generated_profile['profile_image_prompt']
        response['content_suggestions'] = generated_profile['content_suggestions']
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/batch-generate', methods=['POST'])
@require_auth
def batch_generate_profiles():
    """Generate multiple profiles for deployment"""
    try:
        data = request.get_json()
        count = data.get('count', 5)
        platform_types = data.get('platform_types', ['discord', 'instagram', 'facebook'])
        
        if count > 20:  # Limit batch size
            return jsonify({'error': 'Maximum batch size is 20 profiles'}), 400
        
        # Generate profiles
        generated_profiles = profile_generator.generate_batch_profiles(count, platform_types)
        created_profiles = []
        
        for gen_profile in generated_profiles:
            profile = DecoyProfile(
                name=gen_profile['name'],
                username=gen_profile['username'],
                age=gen_profile['age'],
                location=gen_profile['location'],
                platform_type=gen_profile['platform_type'],
                bio=gen_profile['bio'],
                interests=json.dumps(gen_profile['interests']),
                backstory=gen_profile['backstory'],
                status='created',
                created_by=request.headers.get('X-User-ID', 'system')
            )
            
            db.session.add(profile)
            created_profiles.append(profile)
        
        db.session.commit()
        
        log_security_event('batch_profiles_generated', {
            'count': count,
            'platform_types': platform_types,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Successfully generated {count} profiles',
            'profiles': [profile.to_dict() for profile in created_profiles]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/<int:profile_id>', methods=['GET'])
@require_auth
def get_profile(profile_id):
    """Get detailed profile information"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Include content and analytics
        response = profile.to_dict()
        response['content'] = [content.to_dict() for content in profile.content]
        response['analytics'] = [analytics.to_dict() for analytics in profile.analytics]
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/<int:profile_id>', methods=['PUT'])
@require_auth
def update_profile(profile_id):
    """Update profile information"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = [
            'name', 'username', 'bio', 'location', 'status', 
            'platform_profile_id', 'profile_url', 'profile_image_url'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        if 'interests' in data:
            profile.interests = json.dumps(data['interests'])
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_security_event('profile_updated', {
            'profile_id': profile_id,
            'updated_fields': list(data.keys()),
            'user_ip': request.remote_addr
        })
        
        return jsonify(profile.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/<int:profile_id>/deploy', methods=['POST'])
@require_auth
def deploy_profile(profile_id):
    """Mark profile as deployed and update deployment info"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        profile.status = 'deployed'
        profile.deployment_date = datetime.utcnow()
        profile.platform_profile_id = data.get('platform_profile_id')
        profile.profile_url = data.get('profile_url')
        
        db.session.commit()
        
        log_security_event('profile_deployed', {
            'profile_id': profile_id,
            'platform_type': profile.platform_type,
            'platform_profile_id': profile.platform_profile_id,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Profile deployed successfully',
            'profile': profile.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/<int:profile_id>/analytics', methods=['POST'])
@require_auth
def update_analytics(profile_id):
    """Update profile analytics data"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        # Create or update today's analytics
        today = datetime.utcnow().date()
        analytics = ProfileAnalytics.query.filter_by(
            profile_id=profile_id,
            date_recorded=today
        ).first()
        
        if not analytics:
            analytics = ProfileAnalytics(
                profile_id=profile_id,
                date_recorded=today
            )
            db.session.add(analytics)
        
        # Update metrics
        metrics = [
            'profile_views', 'search_appearances', 'friend_requests', 'follow_requests',
            'messages_received', 'suspicious_contacts', 'threat_level_1', 
            'threat_level_2', 'threat_level_3'
        ]
        
        for metric in metrics:
            if metric in data:
                current_value = getattr(analytics, metric, 0)
                setattr(analytics, metric, current_value + data[metric])
        
        if 'contact_locations' in data:
            existing_locations = json.loads(analytics.contact_locations or '[]')
            existing_locations.extend(data['contact_locations'])
            analytics.contact_locations = json.dumps(existing_locations)
        
        # Update profile summary stats
        profile.contact_attempts = ProfileAnalytics.query.filter_by(
            profile_id=profile_id
        ).with_entities(db.func.sum(ProfileAnalytics.messages_received)).scalar() or 0
        
        profile.evidence_captured = ProfileAnalytics.query.filter_by(
            profile_id=profile_id
        ).with_entities(db.func.sum(ProfileAnalytics.threat_level_2 + ProfileAnalytics.threat_level_3)).scalar() or 0
        
        profile.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analytics updated successfully',
            'analytics': analytics.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/stats', methods=['GET'])
@require_auth
def get_profile_stats():
    """Get overall profile deployment statistics"""
    try:
        stats = {
            'total_profiles': DecoyProfile.query.count(),
            'deployed_profiles': DecoyProfile.query.filter_by(status='deployed').count(),
            'active_profiles': DecoyProfile.query.filter_by(status='active').count(),
            'total_contacts': db.session.query(db.func.sum(DecoyProfile.contact_attempts)).scalar() or 0,
            'total_evidence': db.session.query(db.func.sum(DecoyProfile.evidence_captured)).scalar() or 0,
            'platform_breakdown': {}
        }
        
        # Platform breakdown
        platforms = db.session.query(
            DecoyProfile.platform_type,
            db.func.count(DecoyProfile.id)
        ).group_by(DecoyProfile.platform_type).all()
        
        for platform, count in platforms:
            stats['platform_breakdown'][platform] = count
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles/<int:profile_id>', methods=['DELETE'])
@require_auth
def delete_profile(profile_id):
    """Delete a profile (use with caution)"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Check if profile has evidence
        if profile.evidence_captured > 0:
            return jsonify({
                'error': 'Cannot delete profile with captured evidence'
            }), 400
        
        log_security_event('profile_deleted', {
            'profile_id': profile_id,
            'platform_type': profile.platform_type,
            'user_ip': request.remote_addr
        })
        
        db.session.delete(profile)
        db.session.commit()
        
        return jsonify({'message': 'Profile deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

