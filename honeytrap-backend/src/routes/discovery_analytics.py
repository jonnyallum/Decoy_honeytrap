from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.profile import DecoyProfile
from src.services.discovery_analytics import DiscoveryAnalyticsService
from src.security import require_auth, log_security_event
from datetime import datetime
import json

discovery_analytics_bp = Blueprint('discovery_analytics', __name__)
analytics_service = DiscoveryAnalyticsService()

@discovery_analytics_bp.route('/analytics/track-discovery', methods=['POST'])
@require_auth
def track_profile_discovery():
    """Track profile discovery event"""
    try:
        data = request.get_json()
        
        profile_id = data.get('profile_id')
        if not profile_id:
            return jsonify({'error': 'Profile ID is required'}), 400
        
        # Verify profile exists
        profile = DecoyProfile.query.get(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Prepare discovery data
        discovery_data = {
            'platform_type': data.get('platform_type', profile.platform_type),
            'discovery_method': data.get('discovery_method', 'unknown'),
            'user_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'referrer': request.headers.get('Referer'),
            'session_id': data.get('session_id'),
            'geolocation': data.get('geolocation', {}),
            'device_info': data.get('device_info', {})
        }
        
        result = analytics_service.track_profile_discovery(profile_id, discovery_data)
        
        if result['success']:
            log_security_event('profile_discovery_tracked', {
                'profile_id': profile_id,
                'discovery_method': discovery_data['discovery_method'],
                'platform_type': discovery_data['platform_type'],
                'user_ip': request.remote_addr
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/track-engagement', methods=['POST'])
@require_auth
def track_engagement_event():
    """Track engagement event and analyze threats"""
    try:
        data = request.get_json()
        
        profile_id = data.get('profile_id')
        session_id = data.get('session_id')
        
        if not profile_id or not session_id:
            return jsonify({'error': 'Profile ID and session ID are required'}), 400
        
        # Verify profile exists
        profile = DecoyProfile.query.get(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Prepare event data
        event_data = {
            'event_type': data.get('event_type', 'message'),
            'event_details': data.get('event_details', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        result = analytics_service.track_engagement_event(profile_id, session_id, event_data)
        
        if result['success']:
            log_security_event('engagement_tracked', {
                'profile_id': profile_id,
                'session_id': session_id,
                'event_type': event_data['event_type'],
                'threat_level': result['threat_analysis']['threat_level'],
                'requires_escalation': result['requires_escalation'],
                'user_ip': request.remote_addr
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/discovery-analytics', methods=['GET'])
@require_auth
def get_discovery_analytics():
    """Get discovery analytics data"""
    try:
        profile_id = request.args.get('profile_id', type=int)
        days = request.args.get('days', default=30, type=int)
        
        # Limit days to reasonable range
        days = min(max(days, 1), 365)
        
        analytics_data = analytics_service.get_discovery_analytics(profile_id, days)
        
        return jsonify({
            'discovery_analytics': analytics_data,
            'query_parameters': {
                'profile_id': profile_id,
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/threat-analytics', methods=['GET'])
@require_auth
def get_threat_analytics():
    """Get threat analytics data"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        # Limit days to reasonable range
        days = min(max(days, 1), 365)
        
        threat_data = analytics_service.get_threat_analytics(days)
        
        return jsonify({
            'threat_analytics': threat_data,
            'query_parameters': {
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/platform-performance', methods=['GET'])
@require_auth
def get_platform_performance():
    """Get platform performance metrics"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        # Limit days to reasonable range
        days = min(max(days, 1), 365)
        
        performance_data = analytics_service.get_platform_performance_metrics(days)
        
        return jsonify({
            'platform_performance': performance_data,
            'query_parameters': {
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/comprehensive-report', methods=['GET'])
@require_auth
def get_comprehensive_report():
    """Get comprehensive analytics report"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        # Limit days to reasonable range
        days = min(max(days, 1), 365)
        
        report = analytics_service.generate_comprehensive_report(days)
        
        log_security_event('analytics_report_generated', {
            'days': days,
            'user_ip': request.remote_addr
        })
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/threat-indicators', methods=['GET'])
@require_auth
def get_threat_indicators():
    """Get available threat indicators and their descriptions"""
    try:
        return jsonify({
            'threat_indicators': analytics_service.threat_indicators,
            'discovery_methods': analytics_service.discovery_methods,
            'platform_patterns': analytics_service.platform_discovery_patterns
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/profile-performance/<int:profile_id>', methods=['GET'])
@require_auth
def get_profile_performance(profile_id):
    """Get detailed performance analytics for a specific profile"""
    try:
        profile = DecoyProfile.query.get_or_404(profile_id)
        days = request.args.get('days', default=30, type=int)
        
        # Get discovery analytics for this profile
        discovery_data = analytics_service.get_discovery_analytics(profile_id, days)
        
        # Get threat analytics (filtered by profile would require additional query)
        threat_data = analytics_service.get_threat_analytics(days)
        
        # Calculate profile-specific metrics
        profile_metrics = {
            'profile_id': profile_id,
            'profile_name': profile.name,
            'username': profile.username,
            'platform_type': profile.platform_type,
            'age': profile.age,
            'status': profile.status,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'discovery_analytics': discovery_data,
            'performance_period': f'{days} days'
        }
        
        return jsonify({
            'profile_performance': profile_metrics,
            'recommendations': analytics_service._generate_discovery_recommendations(
                profile.platform_type, 
                {'discovery_method': 'general', 'platform_type': profile.platform_type}
            )
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/real-time-dashboard', methods=['GET'])
@require_auth
def get_real_time_dashboard():
    """Get real-time dashboard data"""
    try:
        # Get recent activity (last 24 hours)
        recent_discoveries = analytics_service.get_discovery_analytics(days=1)
        recent_threats = analytics_service.get_threat_analytics(days=1)
        
        # Get current active sessions (this would need to be implemented in chat service)
        # For now, we'll provide a placeholder
        active_sessions = {
            'total_active': 0,
            'high_risk_active': 0,
            'platforms': {}
        }
        
        # Get hourly activity for today
        hourly_activity = recent_discoveries.get('hourly_distribution', [])
        
        return jsonify({
            'real_time_data': {
                'last_updated': datetime.now().isoformat(),
                'recent_discoveries': recent_discoveries.get('total_discoveries', 0),
                'recent_threats': sum(item['count'] for item in recent_threats.get('threat_level_distribution', [])),
                'active_sessions': active_sessions,
                'hourly_activity': hourly_activity
            },
            'alerts': {
                'high_risk_sessions': len(recent_threats.get('high_risk_sessions', [])),
                'critical_threats': len([
                    session for session in recent_threats.get('high_risk_sessions', [])
                    if session.get('risk_score', 0) >= 80
                ])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/export-data', methods=['POST'])
@require_auth
def export_analytics_data():
    """Export analytics data in various formats"""
    try:
        data = request.get_json()
        
        export_type = data.get('export_type', 'json')  # json, csv, pdf
        days = data.get('days', 30)
        include_sections = data.get('include_sections', ['discovery', 'threats', 'performance'])
        
        # Generate comprehensive report
        report = analytics_service.generate_comprehensive_report(days)
        
        if export_type == 'json':
            # Filter report based on requested sections
            filtered_report = {}
            
            if 'discovery' in include_sections:
                filtered_report['discovery_analytics'] = report.get('discovery_analytics', {})
            
            if 'threats' in include_sections:
                filtered_report['threat_analytics'] = report.get('threat_analytics', {})
            
            if 'performance' in include_sections:
                filtered_report['platform_performance'] = report.get('platform_performance', {})
            
            filtered_report['export_metadata'] = {
                'export_type': export_type,
                'exported_at': datetime.now().isoformat(),
                'period': f'{days} days',
                'sections_included': include_sections
            }
            
            log_security_event('analytics_data_exported', {
                'export_type': export_type,
                'days': days,
                'sections': include_sections,
                'user_ip': request.remote_addr
            })
            
            return jsonify(filtered_report)
        
        else:
            return jsonify({
                'error': f'Export type {export_type} not yet implemented',
                'available_types': ['json']
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/search-patterns', methods=['GET'])
@require_auth
def analyze_search_patterns():
    """Analyze search and discovery patterns"""
    try:
        days = request.args.get('days', default=30, type=int)
        platform = request.args.get('platform')
        
        # This would require more sophisticated analysis
        # For now, return basic pattern analysis
        discovery_data = analytics_service.get_discovery_analytics(days=days)
        
        # Analyze patterns
        patterns = {
            'peak_discovery_hours': [],
            'most_effective_methods': [],
            'platform_trends': [],
            'geographic_hotspots': []
        }
        
        # Extract peak hours
        hourly_dist = discovery_data.get('hourly_distribution', [])
        if hourly_dist:
            max_count = max(item['count'] for item in hourly_dist)
            patterns['peak_discovery_hours'] = [
                item['hour'] for item in hourly_dist 
                if item['count'] >= max_count * 0.8  # Hours with 80%+ of peak activity
            ]
        
        # Extract effective methods
        discovery_breakdown = discovery_data.get('discovery_breakdown', [])
        if discovery_breakdown:
            patterns['most_effective_methods'] = [
                {
                    'platform': item['platform'],
                    'method': item['method'],
                    'count': item['count']
                }
                for item in discovery_breakdown[:5]  # Top 5
            ]
        
        return jsonify({
            'search_patterns': patterns,
            'analysis_period': f'{days} days',
            'platform_filter': platform,
            'recommendations': [
                'Focus discovery efforts during peak hours',
                'Optimize most effective discovery methods',
                'Consider geographic targeting for hotspots'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/threat-timeline/<session_id>', methods=['GET'])
@require_auth
def get_threat_timeline(session_id):
    """Get detailed threat timeline for a specific session"""
    try:
        # This would require querying engagement events for the session
        # For now, return a placeholder structure
        
        timeline = {
            'session_id': session_id,
            'timeline_events': [
                # This would be populated from engagement_events table
            ],
            'threat_progression': {
                'initial_contact': None,
                'escalation_points': [],
                'current_threat_level': 0,
                'evidence_collected': []
            },
            'risk_assessment': {
                'current_risk_score': 0,
                'risk_factors': [],
                'recommended_actions': []
            }
        }
        
        return jsonify({
            'threat_timeline': timeline,
            'note': 'Detailed timeline implementation requires integration with chat session data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@discovery_analytics_bp.route('/analytics/effectiveness-score', methods=['POST'])
@require_auth
def calculate_effectiveness_score():
    """Calculate effectiveness score for profiles or strategies"""
    try:
        data = request.get_json()
        
        profile_ids = data.get('profile_ids', [])
        time_period = data.get('time_period', 30)
        
        if not profile_ids:
            return jsonify({'error': 'Profile IDs are required'}), 400
        
        effectiveness_scores = []
        
        for profile_id in profile_ids:
            profile = DecoyProfile.query.get(profile_id)
            if not profile:
                continue
            
            # Get analytics for this profile
            discovery_data = analytics_service.get_discovery_analytics(profile_id, time_period)
            
            # Calculate effectiveness score
            discoveries = discovery_data.get('total_discoveries', 0)
            unique_sessions = discovery_data.get('unique_sessions', 0)
            
            # Simple effectiveness calculation
            base_score = min(discoveries * 10, 50)  # Up to 50 points for discoveries
            engagement_score = min(unique_sessions * 15, 30)  # Up to 30 points for engagements
            
            total_score = base_score + engagement_score
            
            effectiveness_scores.append({
                'profile_id': profile_id,
                'profile_name': profile.name,
                'platform': profile.platform_type,
                'discoveries': discoveries,
                'unique_sessions': unique_sessions,
                'effectiveness_score': total_score,
                'grade': 'A' if total_score >= 70 else 'B' if total_score >= 50 else 'C' if total_score >= 30 else 'D'
            })
        
        return jsonify({
            'effectiveness_analysis': {
                'time_period': f'{time_period} days',
                'profiles_analyzed': len(effectiveness_scores),
                'scores': effectiveness_scores,
                'average_score': sum(item['effectiveness_score'] for item in effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

