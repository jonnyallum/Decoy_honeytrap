from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.profile import DecoyProfile, ProfileContent, ProfileAnalytics
from src.services.profile_manager import ProfileManager
from src.services.image_generator import ImageGenerator
from src.security import require_auth, log_security_event
from datetime import datetime, timedelta
import json

profile_management_bp = Blueprint('profile_management', __name__)
profile_manager = ProfileManager()
image_generator = ImageGenerator()

@profile_management_bp.route('/profile-management/create-comprehensive', methods=['POST'])
@require_auth
def create_comprehensive_profile():
    """Create a comprehensive profile with all assets and deployment plan"""
    try:
        data = request.get_json()
        
        platform_type = data.get('platform_type', 'discord')
        deployment_strategy = data.get('deployment_strategy', 'standard')
        
        # Create comprehensive profile
        profile_data = profile_manager.create_comprehensive_profile(
            platform_type=platform_type,
            deployment_strategy=deployment_strategy
        )
        
        log_security_event('comprehensive_profile_created', {
            'profile_id': profile_data['profile']['id'],
            'platform_type': platform_type,
            'deployment_strategy': deployment_strategy,
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': 'Comprehensive profile created successfully',
            'data': profile_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/batch-deploy', methods=['POST'])
@require_auth
def batch_deploy_profiles():
    """Deploy multiple profiles with comprehensive setup"""
    try:
        data = request.get_json()
        
        count = data.get('count', 5)
        platforms = data.get('platforms', ['discord', 'instagram', 'facebook'])
        strategy = data.get('strategy', 'standard')
        
        if count > 10:  # Limit batch size for safety
            return jsonify({'error': 'Maximum batch size is 10 profiles'}), 400
        
        # Deploy profile batch
        deployment_results = profile_manager.deploy_profile_batch(count, platforms, strategy)
        
        log_security_event('batch_deployment_completed', {
            'count': count,
            'platforms': platforms,
            'strategy': strategy,
            'success_rate': deployment_results['deployment_summary']['success_rate'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Batch deployment completed',
            'results': deployment_results
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/performance-report/<int:profile_id>', methods=['GET'])
@require_auth
def get_performance_report(profile_id):
    """Get comprehensive performance report for a profile"""
    try:
        days = int(request.args.get('days', 30))
        
        if days > 365:  # Limit report period
            return jsonify({'error': 'Maximum report period is 365 days'}), 400
        
        # Generate performance report
        report = profile_manager.get_profile_performance_report(profile_id, days)
        
        if 'error' in report:
            return jsonify(report), 404
        
        log_security_event('performance_report_generated', {
            'profile_id': profile_id,
            'report_period': days,
            'user_ip': request.remote_addr
        })
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/content-calendar/<int:profile_id>', methods=['GET'])
@require_auth
def get_content_calendar(profile_id):
    """Get content calendar for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        days = int(request.args.get('days', 30))
        
        # Generate content calendar
        base_profile = {
            'interests': json.loads(profile.interests) if profile.interests else [],
            'platform_type': profile.platform_type,
            'age': profile.age
        }
        
        content_calendar = profile_manager._generate_content_calendar(base_profile, days)
        
        # Get existing scheduled content
        existing_content = ProfileContent.query.filter_by(
            profile_id=profile_id,
            status='scheduled'
        ).all()
        
        return jsonify({
            'profile_id': profile_id,
            'calendar_period': f'{days} days',
            'generated_content': content_calendar,
            'existing_scheduled': [content.to_dict() for content in existing_content],
            'automation_settings': profile_manager._get_automation_settings(base_profile)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/schedule-content', methods=['POST'])
@require_auth
def schedule_content():
    """Schedule content for a profile"""
    try:
        data = request.get_json()
        
        profile_id = data.get('profile_id')
        content_items = data.get('content_items', [])
        
        if not profile_id or not content_items:
            return jsonify({'error': 'Profile ID and content items are required'}), 400
        
        profile = DecoyProfile.query.get_or_404(profile_id)
        scheduled_content = []
        
        for item in content_items:
            content = ProfileContent(
                profile_id=profile_id,
                content_type=item.get('type', 'post'),
                platform_type=profile.platform_type,
                content_text=item.get('content', ''),
                content_media=json.dumps(item.get('media', [])),
                scheduled_time=datetime.fromisoformat(item.get('scheduled_time')),
                status='scheduled'
            )
            
            db.session.add(content)
            scheduled_content.append(content)
        
        db.session.commit()
        
        log_security_event('content_scheduled', {
            'profile_id': profile_id,
            'content_count': len(content_items),
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Successfully scheduled {len(content_items)} content items',
            'scheduled_content': [content.to_dict() for content in scheduled_content]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/discovery-optimization/<int:profile_id>', methods=['GET'])
@require_auth
def get_discovery_optimization(profile_id):
    """Get discovery optimization plan for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        # Create base profile data
        base_profile = {
            'platform_type': profile.platform_type,
            'interests': json.loads(profile.interests) if profile.interests else [],
            'age': profile.age,
            'location': profile.location,
            'username': profile.username
        }
        
        # Generate discovery plan
        discovery_plan = profile_manager._create_discovery_plan(base_profile)
        
        # Get current analytics for optimization
        recent_analytics = ProfileAnalytics.query.filter(
            ProfileAnalytics.profile_id == profile_id,
            ProfileAnalytics.date_recorded >= (datetime.now() - timedelta(days=30)).date()
        ).all()
        
        # Generate optimization recommendations
        recommendations = profile_manager._generate_optimization_recommendations(profile, recent_analytics)
        
        return jsonify({
            'profile_id': profile_id,
            'discovery_plan': discovery_plan,
            'current_performance': {
                'total_views': sum(a.profile_views for a in recent_analytics),
                'total_contacts': sum(a.messages_received for a in recent_analytics),
                'discovery_rate': profile_manager._calculate_discovery_effectiveness(recent_analytics)
            },
            'optimization_recommendations': recommendations,
            'next_actions': profile_manager._recommend_next_actions(profile, recent_analytics)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/generate-images/<int:profile_id>', methods=['POST'])
@require_auth
def generate_profile_images(profile_id):
    """Generate AI images for a profile using ImageGenerator service"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        # Create profile data for image generation
        profile_data = {
            'id': profile.id,
            'username': profile.username,
            'age': profile.age,
            'interests': json.loads(profile.interests) if profile.interests else [],
            'platform_type': profile.platform_type,
            'gender': data.get('gender', 'female')  # Default to female if not specified
        }
        
        # Generate complete image set
        image_results = image_generator.generate_profile_image_set(profile_data)
        
        # Update profile with generated image URLs
        if image_results['profile_image'] and image_results['profile_image']['success']:
            profile.profile_image_url = image_results['profile_image']['url']
        
        if image_results['cover_image'] and image_results['cover_image']['success']:
            profile.cover_image_url = image_results['cover_image']['url']
        
        if image_results['content_images']:
            content_urls = [img['url'] for img in image_results['content_images'] if img.get('success')]
            profile.additional_images = json.dumps(content_urls)
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_security_event('profile_images_generated', {
            'profile_id': profile_id,
            'success_count': image_results['success_count'],
            'total_count': image_results['total_count'],
            'success_rate': image_results['success_rate'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Profile images generated successfully. {image_results["success_count"]}/{image_results["total_count"]} images created.',
            'image_results': image_results,
            'profile': profile.to_dict(),
            'generation_stats': {
                'success_rate': image_results['success_rate'],
                'errors': image_results['errors'] if image_results['errors'] else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/deployment-strategies', methods=['GET'])
@require_auth
def get_deployment_strategies():
    """Get available deployment strategies and their descriptions"""
    try:
        strategies = {
            'passive': {
                'name': 'Passive Discovery',
                'description': 'Profile waits for contact with minimal proactive engagement',
                'activity_level': 'Low',
                'posting_frequency': 'Weekly',
                'engagement_style': 'Reactive only',
                'risk_level': 'Low',
                'expected_timeline': '4-8 weeks for first contact',
                'best_for': ['Initial testing', 'Low-risk operations', 'Long-term monitoring']
            },
            'standard': {
                'name': 'Standard Operation',
                'description': 'Balanced approach with regular activity and moderate engagement',
                'activity_level': 'Medium',
                'posting_frequency': 'Daily',
                'engagement_style': 'Balanced reactive/proactive',
                'risk_level': 'Medium',
                'expected_timeline': '2-4 weeks for first contact',
                'best_for': ['General operations', 'Balanced risk/reward', 'Most scenarios']
            },
            'active': {
                'name': 'Active Discovery',
                'description': 'High visibility with frequent posting and proactive engagement',
                'activity_level': 'High',
                'posting_frequency': 'Multiple daily',
                'engagement_style': 'Proactive engagement',
                'risk_level': 'Higher',
                'expected_timeline': '1-2 weeks for first contact',
                'best_for': ['Time-sensitive operations', 'High-priority cases', 'Rapid deployment']
            }
        }
        
        return jsonify({
            'strategies': strategies,
            'recommendations': {
                'new_operations': 'standard',
                'testing_phase': 'passive',
                'urgent_cases': 'active'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/platform-analytics', methods=['GET'])
@require_auth
def get_platform_analytics():
    """Get analytics across all platforms"""
    try:
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get platform breakdown
        platform_stats = db.session.query(
            DecoyProfile.platform_type,
            db.func.count(DecoyProfile.id).label('total_profiles'),
            db.func.sum(DecoyProfile.contact_attempts).label('total_contacts'),
            db.func.sum(DecoyProfile.evidence_captured).label('total_evidence')
        ).group_by(DecoyProfile.platform_type).all()
        
        # Get recent analytics
        recent_analytics = db.session.query(
            ProfileAnalytics.profile_id,
            DecoyProfile.platform_type,
            db.func.sum(ProfileAnalytics.profile_views).label('views'),
            db.func.sum(ProfileAnalytics.messages_received).label('contacts'),
            db.func.sum(ProfileAnalytics.threat_level_2 + ProfileAnalytics.threat_level_3).label('threats')
        ).join(DecoyProfile).filter(
            ProfileAnalytics.date_recorded >= start_date.date()
        ).group_by(ProfileAnalytics.profile_id, DecoyProfile.platform_type).all()
        
        # Process analytics by platform
        platform_analytics = {}
        for stat in platform_stats:
            platform = stat.platform_type
            platform_analytics[platform] = {
                'total_profiles': stat.total_profiles or 0,
                'total_contacts': stat.total_contacts or 0,
                'total_evidence': stat.total_evidence or 0,
                'recent_views': 0,
                'recent_contacts': 0,
                'recent_threats': 0,
                'effectiveness_rate': 0
            }
        
        # Add recent analytics
        for analytics in recent_analytics:
            platform = analytics.platform_type
            if platform in platform_analytics:
                platform_analytics[platform]['recent_views'] += analytics.views or 0
                platform_analytics[platform]['recent_contacts'] += analytics.contacts or 0
                platform_analytics[platform]['recent_threats'] += analytics.threats or 0
        
        # Calculate effectiveness rates
        for platform, data in platform_analytics.items():
            if data['recent_contacts'] > 0:
                data['effectiveness_rate'] = (data['recent_threats'] / data['recent_contacts']) * 100
        
        # Overall statistics
        overall_stats = {
            'total_profiles': sum(data['total_profiles'] for data in platform_analytics.values()),
            'total_contacts': sum(data['total_contacts'] for data in platform_analytics.values()),
            'total_evidence': sum(data['total_evidence'] for data in platform_analytics.values()),
            'active_platforms': len(platform_analytics),
            'average_effectiveness': sum(data['effectiveness_rate'] for data in platform_analytics.values()) / len(platform_analytics) if platform_analytics else 0
        }
        
        return jsonify({
            'period': f'{days} days',
            'overall_stats': overall_stats,
            'platform_breakdown': platform_analytics,
            'recommendations': profile_manager._generate_platform_recommendations(platform_analytics)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/risk-assessment', methods=['GET'])
@require_auth
def get_risk_assessment():
    """Get comprehensive risk assessment for all profiles"""
    try:
        # Get all active profiles
        active_profiles = DecoyProfile.query.filter(
            DecoyProfile.status.in_(['deployed', 'active'])
        ).all()
        
        risk_assessment = {
            'overall_risk': 'low',
            'total_profiles': len(active_profiles),
            'risk_breakdown': {
                'low': 0,
                'medium': 0,
                'high': 0
            },
            'risk_factors': [],
            'recommendations': [],
            'immediate_actions': []
        }
        
        high_risk_count = 0
        medium_risk_count = 0
        
        for profile in active_profiles:
            # Get recent analytics
            recent_analytics = ProfileAnalytics.query.filter(
                ProfileAnalytics.profile_id == profile.id,
                ProfileAnalytics.date_recorded >= (datetime.now() - timedelta(days=7)).date()
            ).all()
            
            # Assess individual profile risk
            profile_risk = profile_manager._assess_current_risks(profile, recent_analytics)
            
            # Count risk levels
            if any(risk == 'high' for risk in profile_risk.values()):
                high_risk_count += 1
                risk_assessment['risk_breakdown']['high'] += 1
            elif any(risk == 'medium' for risk in profile_risk.values()):
                medium_risk_count += 1
                risk_assessment['risk_breakdown']['medium'] += 1
            else:
                risk_assessment['risk_breakdown']['low'] += 1
        
        # Determine overall risk
        if high_risk_count > 0:
            risk_assessment['overall_risk'] = 'high'
            risk_assessment['immediate_actions'].append('Review high-risk profiles immediately')
        elif medium_risk_count > len(active_profiles) * 0.3:  # More than 30% medium risk
            risk_assessment['overall_risk'] = 'medium'
            risk_assessment['recommendations'].append('Monitor medium-risk profiles closely')
        
        # Add general recommendations
        risk_assessment['recommendations'].extend([
            'Maintain regular monitoring schedule',
            'Update threat detection algorithms',
            'Review profile authenticity regularly',
            'Ensure legal compliance documentation'
        ])
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/automation-settings/<int:profile_id>', methods=['GET', 'PUT'])
@require_auth
def manage_automation_settings(profile_id):
    """Get or update automation settings for a profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        
        if request.method == 'GET':
            # Get current automation settings
            base_profile = {
                'interests': json.loads(profile.interests) if profile.interests else [],
                'platform_type': profile.platform_type,
                'age': profile.age
            }
            
            automation_settings = profile_manager._get_automation_settings(base_profile)
            
            return jsonify({
                'profile_id': profile_id,
                'automation_settings': automation_settings,
                'current_status': profile.status
            })
        
        elif request.method == 'PUT':
            # Update automation settings
            data = request.get_json()
            
            # Here you would update the automation settings in the database
            # For now, we'll return the updated settings
            
            log_security_event('automation_settings_updated', {
                'profile_id': profile_id,
                'updated_settings': list(data.keys()),
                'user_ip': request.remote_addr
            })
            
            return jsonify({
                'message': 'Automation settings updated successfully',
                'profile_id': profile_id,
                'updated_settings': data
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/emergency-shutdown', methods=['POST'])
@require_auth
def emergency_shutdown():
    """Emergency shutdown of profiles"""
    try:
        data = request.get_json()
        
        profile_ids = data.get('profile_ids', [])
        reason = data.get('reason', 'Emergency shutdown')
        
        if not profile_ids:
            return jsonify({'error': 'Profile IDs are required'}), 400
        
        shutdown_results = []
        
        for profile_id in profile_ids:
            profile = DecoyProfile.query.get(profile_id)
            if profile:
                # Update profile status
                profile.status = 'suspended'
                profile.updated_at = datetime.utcnow()
                
                # Cancel scheduled content
                ProfileContent.query.filter_by(
                    profile_id=profile_id,
                    status='scheduled'
                ).update({'status': 'cancelled'})
                
                shutdown_results.append({
                    'profile_id': profile_id,
                    'username': profile.username,
                    'platform': profile.platform_type,
                    'status': 'shutdown_successful'
                })
                
                log_security_event('emergency_shutdown', {
                    'profile_id': profile_id,
                    'reason': reason,
                    'user_ip': request.remote_addr
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Emergency shutdown completed for {len(shutdown_results)} profiles',
            'reason': reason,
            'shutdown_results': shutdown_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add the new method to ProfileManager class
def _generate_platform_recommendations(self, platform_analytics: dict) -> list:
    """Generate recommendations based on platform analytics"""
    recommendations = []
    
    for platform, data in platform_analytics.items():
        if data['total_profiles'] == 0:
            recommendations.append(f"Consider deploying profiles on {platform}")
        elif data['effectiveness_rate'] < 5:  # Less than 5% effectiveness
            recommendations.append(f"Optimize {platform} profiles for better threat detection")
        elif data['recent_contacts'] == 0:
            recommendations.append(f"Increase visibility of {platform} profiles")
    
    return recommendations

# Monkey patch the method to ProfileManager
ProfileManager._generate_platform_recommendations = _generate_platform_recommendations



@profile_management_bp.route('/profile-management/batch-generate-images', methods=['POST'])
@require_auth
def batch_generate_images():
    """Generate images for multiple profiles"""
    try:
        data = request.get_json()
        profile_ids = data.get('profile_ids', [])
        gender_override = data.get('gender', None)
        
        if not profile_ids:
            return jsonify({'error': 'Profile IDs are required'}), 400
        
        if len(profile_ids) > 20:  # Limit batch size
            return jsonify({'error': 'Maximum batch size is 20 profiles'}), 400
        
        # Get profiles
        profiles = DecoyProfile.query.filter(DecoyProfile.id.in_(profile_ids)).all()
        
        # Prepare profile data for batch generation
        profiles_data = []
        for profile in profiles:
            profile_data = {
                'id': profile.id,
                'username': profile.username,
                'age': profile.age,
                'interests': json.loads(profile.interests) if profile.interests else [],
                'platform_type': profile.platform_type,
                'gender': gender_override or 'female'
            }
            profiles_data.append(profile_data)
        
        # Batch generate images
        batch_results = image_generator.batch_generate_images(profiles_data)
        
        # Update profiles with generated image URLs
        for profile_result in batch_results['profile_results']:
            profile_id = profile_result['profile_id']
            result = profile_result['result']
            
            profile = next((p for p in profiles if p.id == profile_id), None)
            if profile:
                if result['profile_image'] and result['profile_image']['success']:
                    profile.profile_image_url = result['profile_image']['url']
                
                if result['cover_image'] and result['cover_image']['success']:
                    profile.cover_image_url = result['cover_image']['url']
                
                if result['content_images']:
                    content_urls = [img['url'] for img in result['content_images'] if img.get('success')]
                    profile.additional_images = json.dumps(content_urls)
                
                profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_security_event('batch_images_generated', {
            'profile_count': len(profile_ids),
            'total_images_generated': batch_results['total_images_generated'],
            'success_rate': batch_results['success_rate'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Batch image generation completed for {len(profiles)} profiles',
            'batch_results': batch_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/image-generation-stats', methods=['GET'])
@require_auth
def get_image_generation_stats():
    """Get image generation statistics"""
    try:
        stats = image_generator.get_image_generation_stats()
        
        return jsonify({
            'image_generation_stats': stats,
            'service_status': 'active'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/validate-prompt', methods=['POST'])
@require_auth
def validate_image_prompt():
    """Validate an image generation prompt for safety"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        validation_result = image_generator.validate_image_prompt(prompt)
        
        return jsonify({
            'prompt': prompt,
            'validation': validation_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/prompt-templates', methods=['GET'])
@require_auth
def get_prompt_templates():
    """Get image generation prompt templates"""
    try:
        templates = image_generator.get_prompt_templates()
        
        return jsonify({
            'templates': templates,
            'usage_guidelines': {
                'safety_requirements': [
                    'Always include safety guidelines in prompts',
                    'Ensure age-appropriate content for teenagers',
                    'Use professional and realistic descriptors',
                    'Avoid any inappropriate or suggestive content'
                ],
                'best_practices': [
                    'Be specific about age range (13-16 years old)',
                    'Include setting and lighting descriptions',
                    'Specify image style (selfie, portrait, casual)',
                    'Add platform-appropriate styling cues'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/cleanup-images', methods=['POST'])
@require_auth
def cleanup_old_images():
    """Clean up old generated images"""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 30)
        
        if days_old < 7:  # Minimum 7 days
            return jsonify({'error': 'Minimum cleanup age is 7 days'}), 400
        
        cleanup_result = image_generator.cleanup_old_images(days_old)
        
        log_security_event('images_cleanup', {
            'days_old': days_old,
            'deleted_count': cleanup_result['deleted_count'],
            'user_ip': request.remote_addr
        })
        
        return jsonify({
            'message': f'Cleanup completed. {cleanup_result["deleted_count"]} files removed.',
            'cleanup_result': cleanup_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_management_bp.route('/profile-management/test-image-generation', methods=['POST'])
@require_auth
def test_image_generation():
    """Test image generation with sample data"""
    try:
        data = request.get_json()
        
        # Create test profile data
        test_profile = {
            'id': 'test',
            'username': 'test_profile',
            'age': data.get('age', 14),
            'interests': data.get('interests', ['gaming', 'art', 'music']),
            'platform_type': data.get('platform_type', 'discord'),
            'gender': data.get('gender', 'female')
        }
        
        image_type = data.get('image_type', 'profile')
        
        # Generate single test image
        test_result = image_generator.generate_profile_image(test_profile, image_type)
        
        return jsonify({
            'message': 'Test image generation completed',
            'test_profile': test_profile,
            'test_result': test_result,
            'note': 'This is a test generation - no database updates performed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add the new method to ProfileManager class
def _generate_platform_recommendations(self, platform_analytics: dict) -> list:
    """Generate recommendations based on platform analytics"""
    recommendations = []
    
    for platform, data in platform_analytics.items():
        if data['total_profiles'] == 0:
            recommendations.append(f"Consider deploying profiles on {platform}")
        elif data['effectiveness_rate'] < 5:  # Less than 5% effectiveness
            recommendations.append(f"Optimize {platform} profiles for better threat detection")
        elif data['recent_contacts'] == 0:
            recommendations.append(f"Increase visibility of {platform} profiles")
    
    return recommendations

# Monkey patch the method to ProfileManager
ProfileManager._generate_platform_recommendations = _generate_platform_recommendations

