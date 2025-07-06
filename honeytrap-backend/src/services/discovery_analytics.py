import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import logging
from src.models.user import db
from src.models.profile import DecoyProfile, ProfileContent, ProfileAnalytics
from src.models.chat import ChatSession, ChatMessage, Evidence

class DiscoveryAnalyticsService:
    """Advanced analytics service for tracking profile discovery and threat behavior"""
    
    def __init__(self):
        self.analytics_db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'analytics.db')
        self._initialize_analytics_db()
        
        # Discovery tracking categories
        self.discovery_methods = {
            'search': 'Found through platform search',
            'recommendation': 'Platform algorithm recommendation',
            'mutual_friends': 'Through mutual friends/connections',
            'hashtag': 'Found through hashtag browsing',
            'group': 'Found in groups/servers',
            'direct_link': 'Direct profile link access',
            'unknown': 'Discovery method unknown'
        }
        
        # Threat behavior patterns
        self.threat_indicators = {
            'rapid_contact': 'Contacted within minutes of discovery',
            'age_focused': 'Specifically asks about age',
            'isolation_attempts': 'Tries to move conversation off-platform',
            'personal_info_requests': 'Requests personal information',
            'meeting_requests': 'Suggests meeting in person',
            'inappropriate_content': 'Sends inappropriate messages/media',
            'grooming_language': 'Uses grooming language patterns',
            'gift_offers': 'Offers gifts or money'
        }
        
        # Platform-specific discovery patterns
        self.platform_discovery_patterns = {
            'discord': {
                'common_methods': ['group', 'mutual_friends', 'search'],
                'peak_discovery_times': ['16:00-20:00', '21:00-23:00'],
                'typical_approach': 'Gaming-related initial contact'
            },
            'instagram': {
                'common_methods': ['hashtag', 'recommendation', 'search'],
                'peak_discovery_times': ['17:00-19:00', '20:00-22:00'],
                'typical_approach': 'Comments on posts or stories'
            },
            'facebook': {
                'common_methods': ['mutual_friends', 'search', 'group'],
                'peak_discovery_times': ['15:00-17:00', '19:00-21:00'],
                'typical_approach': 'Friend request with message'
            },
            'snapchat': {
                'common_methods': ['search', 'recommendation', 'mutual_friends'],
                'peak_discovery_times': ['16:00-18:00', '20:00-22:00'],
                'typical_approach': 'Direct snap or chat'
            },
            'tiktok': {
                'common_methods': ['hashtag', 'recommendation', 'search'],
                'peak_discovery_times': ['18:00-20:00', '21:00-23:00'],
                'typical_approach': 'Comments on videos'
            }
        }

    def _initialize_analytics_db(self):
        """Initialize analytics database with required tables"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            # Discovery events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discovery_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    platform_type TEXT NOT NULL,
                    discovery_method TEXT,
                    discovery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_ip TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    session_id TEXT,
                    geolocation TEXT,
                    device_info TEXT,
                    FOREIGN KEY (profile_id) REFERENCES decoy_profiles (id)
                )
            ''')
            
            # Engagement tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engagement_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    session_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    threat_level INTEGER DEFAULT 0,
                    escalation_indicators TEXT,
                    FOREIGN KEY (profile_id) REFERENCES decoy_profiles (id)
                )
            ''')
            
            # Threat behavior analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    profile_id INTEGER NOT NULL,
                    threat_indicators TEXT,
                    risk_score REAL DEFAULT 0.0,
                    behavior_patterns TEXT,
                    escalation_timeline TEXT,
                    evidence_collected TEXT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES decoy_profiles (id)
                )
            ''')
            
            # Platform performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platform_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_type TEXT NOT NULL,
                    metric_date DATE NOT NULL,
                    profile_views INTEGER DEFAULT 0,
                    contact_attempts INTEGER DEFAULT 0,
                    successful_engagements INTEGER DEFAULT 0,
                    threat_detections INTEGER DEFAULT 0,
                    evidence_captured INTEGER DEFAULT 0,
                    average_discovery_time REAL DEFAULT 0.0,
                    PRIMARY KEY (platform_type, metric_date)
                )
            ''')
            
            # Geographic analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geographic_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    country TEXT,
                    city TEXT,
                    threat_count INTEGER DEFAULT 0,
                    profile_discoveries INTEGER DEFAULT 0,
                    risk_level TEXT DEFAULT 'low',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info("Analytics database initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing analytics database: {str(e)}")

    def track_profile_discovery(self, profile_id: int, discovery_data: Dict) -> Dict:
        """Track when and how a profile is discovered"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            # Extract discovery information
            platform_type = discovery_data.get('platform_type')
            discovery_method = discovery_data.get('discovery_method', 'unknown')
            user_ip = discovery_data.get('user_ip')
            user_agent = discovery_data.get('user_agent')
            referrer = discovery_data.get('referrer')
            session_id = discovery_data.get('session_id')
            geolocation = json.dumps(discovery_data.get('geolocation', {}))
            device_info = json.dumps(discovery_data.get('device_info', {}))
            
            # Insert discovery event
            cursor.execute('''
                INSERT INTO discovery_events 
                (profile_id, platform_type, discovery_method, user_ip, user_agent, 
                 referrer, session_id, geolocation, device_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (profile_id, platform_type, discovery_method, user_ip, user_agent,
                  referrer, session_id, geolocation, device_info))
            
            discovery_id = cursor.lastrowid
            
            # Update profile analytics
            self._update_profile_discovery_stats(cursor, profile_id, discovery_method)
            
            # Update platform metrics
            self._update_platform_discovery_metrics(cursor, platform_type)
            
            conn.commit()
            conn.close()
            
            # Analyze discovery pattern
            discovery_analysis = self._analyze_discovery_pattern(profile_id, discovery_data)
            
            return {
                'success': True,
                'discovery_id': discovery_id,
                'discovery_analysis': discovery_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def track_engagement_event(self, profile_id: int, session_id: str, event_data: Dict) -> Dict:
        """Track engagement events and analyze threat indicators"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            event_type = event_data.get('event_type')
            event_details = json.dumps(event_data.get('event_details', {}))
            
            # Analyze threat indicators
            threat_analysis = self._analyze_threat_indicators(event_data)
            threat_level = threat_analysis['threat_level']
            escalation_indicators = json.dumps(threat_analysis['indicators'])
            
            # Insert engagement event
            cursor.execute('''
                INSERT INTO engagement_events 
                (profile_id, session_id, event_type, event_data, threat_level, escalation_indicators)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (profile_id, session_id, event_type, event_details, threat_level, escalation_indicators))
            
            engagement_id = cursor.lastrowid
            
            # Update threat analysis if significant
            if threat_level >= 2:
                self._update_threat_analysis(cursor, session_id, profile_id, threat_analysis)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'engagement_id': engagement_id,
                'threat_analysis': threat_analysis,
                'requires_escalation': threat_level >= 3
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_discovery_pattern(self, profile_id: int, discovery_data: Dict) -> Dict:
        """Analyze discovery patterns for insights"""
        
        try:
            platform = discovery_data.get('platform_type')
            discovery_method = discovery_data.get('discovery_method')
            discovery_time = datetime.now()
            
            # Get platform-specific patterns
            platform_patterns = self.platform_discovery_patterns.get(platform, {})
            
            # Analyze discovery timing
            hour = discovery_time.hour
            is_peak_time = any(
                int(time_range.split('-')[0].split(':')[0]) <= hour <= int(time_range.split('-')[1].split(':')[0])
                for time_range in platform_patterns.get('peak_discovery_times', [])
            )
            
            # Check if discovery method is common for platform
            common_methods = platform_patterns.get('common_methods', [])
            is_common_method = discovery_method in common_methods
            
            # Calculate discovery effectiveness score
            effectiveness_score = 0.5  # Base score
            if is_peak_time:
                effectiveness_score += 0.2
            if is_common_method:
                effectiveness_score += 0.2
            if discovery_method != 'unknown':
                effectiveness_score += 0.1
            
            return {
                'platform': platform,
                'discovery_method': discovery_method,
                'is_peak_time': is_peak_time,
                'is_common_method': is_common_method,
                'effectiveness_score': min(effectiveness_score, 1.0),
                'recommendations': self._generate_discovery_recommendations(platform, discovery_data)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'effectiveness_score': 0.0
            }

    def _analyze_threat_indicators(self, event_data: Dict) -> Dict:
        """Analyze event data for threat indicators"""
        
        threat_level = 0
        detected_indicators = []
        
        event_type = event_data.get('event_type', '')
        event_details = event_data.get('event_details', {})
        message_content = event_details.get('message_content', '').lower()
        
        # Check for various threat indicators
        
        # Age-focused questions
        age_keywords = ['how old', 'age', 'what grade', 'school year']
        if any(keyword in message_content for keyword in age_keywords):
            detected_indicators.append('age_focused')
            threat_level = max(threat_level, 1)
        
        # Personal information requests
        personal_info_keywords = ['address', 'phone', 'number', 'where do you live', 'what school']
        if any(keyword in message_content for keyword in personal_info_keywords):
            detected_indicators.append('personal_info_requests')
            threat_level = max(threat_level, 2)
        
        # Meeting requests
        meeting_keywords = ['meet up', 'hang out', 'come over', 'visit', 'see you']
        if any(keyword in message_content for keyword in meeting_keywords):
            detected_indicators.append('meeting_requests')
            threat_level = max(threat_level, 3)
        
        # Isolation attempts
        isolation_keywords = ['private chat', 'different app', 'whatsapp', 'telegram', 'snapchat', 'text me']
        if any(keyword in message_content for keyword in isolation_keywords):
            detected_indicators.append('isolation_attempts')
            threat_level = max(threat_level, 2)
        
        # Inappropriate content
        if event_details.get('contains_inappropriate_content'):
            detected_indicators.append('inappropriate_content')
            threat_level = max(threat_level, 4)
        
        # Gift offers
        gift_keywords = ['buy you', 'gift', 'money', 'pay for', 'treat you']
        if any(keyword in message_content for keyword in gift_keywords):
            detected_indicators.append('gift_offers')
            threat_level = max(threat_level, 2)
        
        # Rapid contact (if contacted within 30 minutes of discovery)
        if event_details.get('time_since_discovery', 999) < 30:
            detected_indicators.append('rapid_contact')
            threat_level = max(threat_level, 1)
        
        # Grooming language patterns
        grooming_keywords = ['special', 'mature', 'secret', 'between us', 'dont tell']
        if any(keyword in message_content for keyword in grooming_keywords):
            detected_indicators.append('grooming_language')
            threat_level = max(threat_level, 3)
        
        return {
            'threat_level': threat_level,
            'indicators': detected_indicators,
            'risk_assessment': self._calculate_risk_assessment(threat_level, detected_indicators),
            'recommended_actions': self._get_recommended_actions(threat_level, detected_indicators)
        }

    def _calculate_risk_assessment(self, threat_level: int, indicators: List[str]) -> Dict:
        """Calculate comprehensive risk assessment"""
        
        risk_categories = {
            0: 'minimal',
            1: 'low',
            2: 'medium',
            3: 'high',
            4: 'critical'
        }
        
        risk_level = risk_categories.get(threat_level, 'unknown')
        
        # Calculate composite risk score
        base_score = threat_level * 20  # 0-80 base score
        indicator_bonus = len(indicators) * 5  # Bonus for multiple indicators
        composite_score = min(base_score + indicator_bonus, 100)
        
        return {
            'risk_level': risk_level,
            'threat_level': threat_level,
            'composite_score': composite_score,
            'indicator_count': len(indicators),
            'requires_immediate_attention': threat_level >= 3,
            'evidence_collection_priority': 'high' if threat_level >= 2 else 'medium' if threat_level >= 1 else 'low'
        }

    def _get_recommended_actions(self, threat_level: int, indicators: List[str]) -> List[str]:
        """Get recommended actions based on threat analysis"""
        
        actions = []
        
        if threat_level >= 4:
            actions.extend([
                'IMMEDIATE: Alert law enforcement',
                'IMMEDIATE: Preserve all evidence',
                'IMMEDIATE: Escalate to senior analyst',
                'Continue engagement with extreme caution'
            ])
        elif threat_level >= 3:
            actions.extend([
                'HIGH PRIORITY: Increase monitoring',
                'Begin evidence collection procedures',
                'Notify supervisor',
                'Prepare for potential escalation'
            ])
        elif threat_level >= 2:
            actions.extend([
                'MEDIUM PRIORITY: Enhanced monitoring',
                'Document all interactions',
                'Continue engagement cautiously'
            ])
        elif threat_level >= 1:
            actions.extend([
                'LOW PRIORITY: Standard monitoring',
                'Log interactions for pattern analysis'
            ])
        
        # Specific actions based on indicators
        if 'meeting_requests' in indicators:
            actions.append('CRITICAL: Do not agree to meetings')
        
        if 'isolation_attempts' in indicators:
            actions.append('WARNING: Resist moving to other platforms')
        
        if 'personal_info_requests' in indicators:
            actions.append('CAUTION: Provide only scripted responses')
        
        return actions

    def _update_profile_discovery_stats(self, cursor, profile_id: int, discovery_method: str):
        """Update profile discovery statistics"""
        
        try:
            # Get or create profile analytics record
            cursor.execute('''
                SELECT id FROM profile_analytics WHERE profile_id = ?
            ''', (profile_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                cursor.execute('''
                    UPDATE profile_analytics 
                    SET total_views = total_views + 1,
                        last_viewed = CURRENT_TIMESTAMP
                    WHERE profile_id = ?
                ''', (profile_id,))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO profile_analytics 
                    (profile_id, total_views, last_viewed)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                ''', (profile_id,))
            
        except Exception as e:
            logging.error(f"Error updating profile discovery stats: {str(e)}")

    def _update_platform_discovery_metrics(self, cursor, platform_type: str):
        """Update platform-level discovery metrics"""
        
        try:
            today = datetime.now().date()
            
            # Update or insert platform metrics for today
            cursor.execute('''
                INSERT OR REPLACE INTO platform_metrics 
                (platform_type, metric_date, profile_views)
                VALUES (?, ?, COALESCE((
                    SELECT profile_views FROM platform_metrics 
                    WHERE platform_type = ? AND metric_date = ?
                ), 0) + 1)
            ''', (platform_type, today, platform_type, today))
            
        except Exception as e:
            logging.error(f"Error updating platform discovery metrics: {str(e)}")

    def _update_threat_analysis(self, cursor, session_id: str, profile_id: int, threat_analysis: Dict):
        """Update or create threat analysis record"""
        
        try:
            threat_indicators = json.dumps(threat_analysis['indicators'])
            risk_score = threat_analysis['risk_assessment']['composite_score']
            behavior_patterns = json.dumps({
                'threat_level': threat_analysis['threat_level'],
                'risk_level': threat_analysis['risk_assessment']['risk_level']
            })
            
            # Check if analysis exists for this session
            cursor.execute('''
                SELECT id FROM threat_analysis WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing analysis
                cursor.execute('''
                    UPDATE threat_analysis 
                    SET threat_indicators = ?, risk_score = ?, behavior_patterns = ?,
                        analysis_timestamp = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (threat_indicators, risk_score, behavior_patterns, session_id))
            else:
                # Create new analysis
                cursor.execute('''
                    INSERT INTO threat_analysis 
                    (session_id, profile_id, threat_indicators, risk_score, behavior_patterns)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, profile_id, threat_indicators, risk_score, behavior_patterns))
            
        except Exception as e:
            logging.error(f"Error updating threat analysis: {str(e)}")

    def _generate_discovery_recommendations(self, platform: str, discovery_data: Dict) -> List[str]:
        """Generate recommendations for improving discovery"""
        
        recommendations = []
        discovery_method = discovery_data.get('discovery_method')
        
        if platform == 'discord':
            if discovery_method == 'search':
                recommendations.append('Consider joining more gaming servers to increase visibility')
            elif discovery_method == 'group':
                recommendations.append('Profile is effectively visible in group settings')
            else:
                recommendations.append('Increase activity in gaming communities')
        
        elif platform == 'instagram':
            if discovery_method == 'hashtag':
                recommendations.append('Current hashtag strategy is effective')
            elif discovery_method == 'search':
                recommendations.append('Consider optimizing profile for search discovery')
            else:
                recommendations.append('Increase use of trending hashtags')
        
        elif platform == 'facebook':
            if discovery_method == 'mutual_friends':
                recommendations.append('Friend network strategy is working well')
            else:
                recommendations.append('Consider expanding friend connections')
        
        # General recommendations
        recommendations.extend([
            'Monitor peak discovery times for optimal posting',
            'Analyze successful discovery patterns for replication',
            'Adjust profile visibility settings if needed'
        ])
        
        return recommendations

    def get_discovery_analytics(self, profile_id: Optional[int] = None, days: int = 30) -> Dict:
        """Get comprehensive discovery analytics"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            # Date range
            start_date = datetime.now() - timedelta(days=days)
            
            # Base query conditions
            where_conditions = ['discovery_time >= ?']
            params = [start_date]
            
            if profile_id:
                where_conditions.append('profile_id = ?')
                params.append(profile_id)
            
            where_clause = ' AND '.join(where_conditions)
            
            # Get discovery events
            cursor.execute(f'''
                SELECT platform_type, discovery_method, COUNT(*) as count,
                       AVG(julianday('now') - julianday(discovery_time)) * 24 as avg_hours_ago
                FROM discovery_events 
                WHERE {where_clause}
                GROUP BY platform_type, discovery_method
                ORDER BY count DESC
            ''', params)
            
            discovery_breakdown = cursor.fetchall()
            
            # Get hourly distribution
            cursor.execute(f'''
                SELECT strftime('%H', discovery_time) as hour, COUNT(*) as count
                FROM discovery_events 
                WHERE {where_clause}
                GROUP BY hour
                ORDER BY hour
            ''', params)
            
            hourly_distribution = cursor.fetchall()
            
            # Get geographic distribution
            cursor.execute(f'''
                SELECT geolocation, COUNT(*) as count
                FROM discovery_events 
                WHERE {where_clause} AND geolocation != '{{}}'
                GROUP BY geolocation
                ORDER BY count DESC
                LIMIT 10
            ''', params)
            
            geographic_data = cursor.fetchall()
            
            # Get total statistics
            cursor.execute(f'''
                SELECT COUNT(*) as total_discoveries,
                       COUNT(DISTINCT profile_id) as unique_profiles,
                       COUNT(DISTINCT session_id) as unique_sessions
                FROM discovery_events 
                WHERE {where_clause}
            ''', params)
            
            total_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'period': f'{days} days',
                'total_discoveries': total_stats[0] if total_stats else 0,
                'unique_profiles': total_stats[1] if total_stats else 0,
                'unique_sessions': total_stats[2] if total_stats else 0,
                'discovery_breakdown': [
                    {
                        'platform': row[0],
                        'method': row[1],
                        'count': row[2],
                        'avg_hours_ago': round(row[3], 2) if row[3] else 0
                    }
                    for row in discovery_breakdown
                ],
                'hourly_distribution': [
                    {
                        'hour': int(row[0]),
                        'count': row[1]
                    }
                    for row in hourly_distribution
                ],
                'geographic_distribution': [
                    {
                        'location': json.loads(row[0]) if row[0] != '{}' else {},
                        'count': row[1]
                    }
                    for row in geographic_data
                ]
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_discoveries': 0
            }

    def get_threat_analytics(self, days: int = 30) -> Dict:
        """Get comprehensive threat analytics"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Get threat level distribution
            cursor.execute('''
                SELECT threat_level, COUNT(*) as count
                FROM engagement_events 
                WHERE timestamp >= ?
                GROUP BY threat_level
                ORDER BY threat_level
            ''', (start_date,))
            
            threat_levels = cursor.fetchall()
            
            # Get threat indicators frequency
            cursor.execute('''
                SELECT escalation_indicators, COUNT(*) as count
                FROM engagement_events 
                WHERE timestamp >= ? AND escalation_indicators != '[]'
                GROUP BY escalation_indicators
                ORDER BY count DESC
                LIMIT 10
            ''', (start_date,))
            
            indicator_frequency = cursor.fetchall()
            
            # Get high-risk sessions
            cursor.execute('''
                SELECT session_id, profile_id, risk_score, threat_indicators, analysis_timestamp
                FROM threat_analysis 
                WHERE analysis_timestamp >= ? AND risk_score >= 60
                ORDER BY risk_score DESC
                LIMIT 20
            ''', (start_date,))
            
            high_risk_sessions = cursor.fetchall()
            
            # Get platform threat distribution
            cursor.execute('''
                SELECT p.platform_type, AVG(e.threat_level) as avg_threat_level, 
                       COUNT(*) as total_events, 
                       SUM(CASE WHEN e.threat_level >= 3 THEN 1 ELSE 0 END) as high_threat_events
                FROM engagement_events e
                JOIN decoy_profiles p ON e.profile_id = p.id
                WHERE e.timestamp >= ?
                GROUP BY p.platform_type
                ORDER BY avg_threat_level DESC
            ''', (start_date,))
            
            platform_threats = cursor.fetchall()
            
            conn.close()
            
            # Process indicator frequency
            processed_indicators = []
            for row in indicator_frequency:
                try:
                    indicators = json.loads(row[0])
                    for indicator in indicators:
                        processed_indicators.append({
                            'indicator': indicator,
                            'count': row[1]
                        })
                except:
                    continue
            
            # Aggregate indicator counts
            indicator_counts = Counter()
            for item in processed_indicators:
                indicator_counts[item['indicator']] += item['count']
            
            return {
                'period': f'{days} days',
                'threat_level_distribution': [
                    {
                        'threat_level': row[0],
                        'count': row[1]
                    }
                    for row in threat_levels
                ],
                'top_threat_indicators': [
                    {
                        'indicator': indicator,
                        'count': count,
                        'description': self.threat_indicators.get(indicator, 'Unknown indicator')
                    }
                    for indicator, count in indicator_counts.most_common(10)
                ],
                'high_risk_sessions': [
                    {
                        'session_id': row[0],
                        'profile_id': row[1],
                        'risk_score': row[2],
                        'threat_indicators': json.loads(row[3]) if row[3] else [],
                        'timestamp': row[4]
                    }
                    for row in high_risk_sessions
                ],
                'platform_threat_analysis': [
                    {
                        'platform': row[0],
                        'avg_threat_level': round(row[1], 2),
                        'total_events': row[2],
                        'high_threat_events': row[3],
                        'threat_rate': round((row[3] / row[2]) * 100, 1) if row[2] > 0 else 0
                    }
                    for row in platform_threats
                ]
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'period': f'{days} days'
            }

    def get_platform_performance_metrics(self, days: int = 30) -> Dict:
        """Get platform performance metrics"""
        
        try:
            conn = sqlite3.connect(self.analytics_db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Get platform metrics
            cursor.execute('''
                SELECT platform_type,
                       SUM(profile_views) as total_views,
                       SUM(contact_attempts) as total_contacts,
                       SUM(successful_engagements) as total_engagements,
                       SUM(threat_detections) as total_threats,
                       SUM(evidence_captured) as total_evidence,
                       AVG(average_discovery_time) as avg_discovery_time
                FROM platform_metrics 
                WHERE metric_date >= ?
                GROUP BY platform_type
                ORDER BY total_views DESC
            ''', (start_date,))
            
            platform_metrics = cursor.fetchall()
            
            # Calculate effectiveness scores
            processed_metrics = []
            for row in platform_metrics:
                platform = row[0]
                views = row[1] or 0
                contacts = row[2] or 0
                engagements = row[3] or 0
                threats = row[4] or 0
                evidence = row[5] or 0
                
                # Calculate rates
                contact_rate = (contacts / views * 100) if views > 0 else 0
                engagement_rate = (engagements / contacts * 100) if contacts > 0 else 0
                threat_rate = (threats / engagements * 100) if engagements > 0 else 0
                evidence_rate = (evidence / threats * 100) if threats > 0 else 0
                
                # Overall effectiveness score
                effectiveness = (contact_rate * 0.3 + engagement_rate * 0.3 + 
                               threat_rate * 0.25 + evidence_rate * 0.15)
                
                processed_metrics.append({
                    'platform': platform,
                    'total_views': views,
                    'total_contacts': contacts,
                    'total_engagements': engagements,
                    'total_threats': threats,
                    'total_evidence': evidence,
                    'contact_rate': round(contact_rate, 2),
                    'engagement_rate': round(engagement_rate, 2),
                    'threat_rate': round(threat_rate, 2),
                    'evidence_rate': round(evidence_rate, 2),
                    'effectiveness_score': round(effectiveness, 2),
                    'avg_discovery_time': round(row[6], 2) if row[6] else 0
                })
            
            conn.close()
            
            return {
                'period': f'{days} days',
                'platform_metrics': processed_metrics,
                'recommendations': self._generate_platform_recommendations(processed_metrics)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'platform_metrics': []
            }

    def _generate_platform_recommendations(self, metrics: List[Dict]) -> List[str]:
        """Generate recommendations based on platform performance"""
        
        recommendations = []
        
        if not metrics:
            return ['No data available for recommendations']
        
        # Find best and worst performing platforms
        best_platform = max(metrics, key=lambda x: x['effectiveness_score'])
        worst_platform = min(metrics, key=lambda x: x['effectiveness_score'])
        
        recommendations.append(f"Best performing platform: {best_platform['platform']} "
                             f"(effectiveness: {best_platform['effectiveness_score']}%)")
        
        if worst_platform['effectiveness_score'] < 20:
            recommendations.append(f"Consider optimizing {worst_platform['platform']} strategy "
                                 f"(current effectiveness: {worst_platform['effectiveness_score']}%)")
        
        # Platform-specific recommendations
        for metric in metrics:
            platform = metric['platform']
            
            if metric['contact_rate'] < 5:
                recommendations.append(f"{platform}: Increase profile visibility to improve contact rate")
            
            if metric['engagement_rate'] < 30:
                recommendations.append(f"{platform}: Improve response strategy to increase engagement")
            
            if metric['threat_rate'] < 10:
                recommendations.append(f"{platform}: Consider adjusting vulnerability signals")
        
        return recommendations

    def generate_comprehensive_report(self, days: int = 30) -> Dict:
        """Generate comprehensive analytics report"""
        
        try:
            discovery_analytics = self.get_discovery_analytics(days=days)
            threat_analytics = self.get_threat_analytics(days=days)
            platform_metrics = self.get_platform_performance_metrics(days=days)
            
            # Calculate overall statistics
            total_discoveries = discovery_analytics.get('total_discoveries', 0)
            total_threats = sum(item['count'] for item in threat_analytics.get('threat_level_distribution', []))
            
            threat_conversion_rate = (total_threats / total_discoveries * 100) if total_discoveries > 0 else 0
            
            return {
                'report_period': f'{days} days',
                'generated_at': datetime.now().isoformat(),
                'executive_summary': {
                    'total_discoveries': total_discoveries,
                    'total_threat_events': total_threats,
                    'threat_conversion_rate': round(threat_conversion_rate, 2),
                    'unique_profiles_discovered': discovery_analytics.get('unique_profiles', 0),
                    'high_risk_sessions': len(threat_analytics.get('high_risk_sessions', []))
                },
                'discovery_analytics': discovery_analytics,
                'threat_analytics': threat_analytics,
                'platform_performance': platform_metrics,
                'key_insights': self._generate_key_insights(discovery_analytics, threat_analytics, platform_metrics),
                'recommendations': self._generate_comprehensive_recommendations(discovery_analytics, threat_analytics, platform_metrics)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'report_period': f'{days} days',
                'generated_at': datetime.now().isoformat()
            }

    def _generate_key_insights(self, discovery_data: Dict, threat_data: Dict, platform_data: Dict) -> List[str]:
        """Generate key insights from analytics data"""
        
        insights = []
        
        # Discovery insights
        if discovery_data.get('discovery_breakdown'):
            top_discovery = discovery_data['discovery_breakdown'][0]
            insights.append(f"Most effective discovery method: {top_discovery['method']} "
                          f"on {top_discovery['platform']} ({top_discovery['count']} discoveries)")
        
        # Threat insights
        if threat_data.get('platform_threat_analysis'):
            highest_threat_platform = max(threat_data['platform_threat_analysis'], 
                                        key=lambda x: x['avg_threat_level'])
            insights.append(f"Highest threat activity on {highest_threat_platform['platform']} "
                          f"(avg threat level: {highest_threat_platform['avg_threat_level']})")
        
        # Platform performance insights
        if platform_data.get('platform_metrics'):
            best_platform = max(platform_data['platform_metrics'], 
                               key=lambda x: x['effectiveness_score'])
            insights.append(f"Most effective platform: {best_platform['platform']} "
                          f"({best_platform['effectiveness_score']}% effectiveness)")
        
        return insights

    def _generate_comprehensive_recommendations(self, discovery_data: Dict, threat_data: Dict, platform_data: Dict) -> List[str]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Add discovery recommendations
        if 'recommendations' in discovery_data:
            recommendations.extend(discovery_data['recommendations'][:3])
        
        # Add platform recommendations
        if 'recommendations' in platform_data:
            recommendations.extend(platform_data['recommendations'][:3])
        
        # Add threat-based recommendations
        if threat_data.get('top_threat_indicators'):
            top_indicator = threat_data['top_threat_indicators'][0]
            recommendations.append(f"Focus on detecting '{top_indicator['indicator']}' "
                                 f"(most common threat indicator)")
        
        # General recommendations
        recommendations.extend([
            'Regularly review and update profile vulnerability signals',
            'Monitor peak discovery times for optimal content scheduling',
            'Maintain consistent engagement patterns across platforms',
            'Ensure proper evidence collection procedures are followed'
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations

