import os
import json
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from src.models.profile import DecoyProfile, ProfileContent, ProfileAnalytics
from src.services.profile_generator import ProfileGenerator
from src.models.user import db
import hashlib
import base64

class ProfileManager:
    """Enhanced service for managing decoy profiles with automation features"""
    
    def __init__(self):
        self.profile_generator = ProfileGenerator()
        self.image_generation_enabled = True
        self.content_automation_enabled = True
        
        # SEO and discovery optimization keywords
        self.discovery_keywords = {
            'gaming': ['gamer', 'gaming', 'minecraft', 'fortnite', 'roblox', 'discord', 'twitch'],
            'art': ['artist', 'drawing', 'digital art', 'creative', 'aesthetic', 'artwork'],
            'music': ['music', 'singer', 'musician', 'spotify', 'playlist', 'concert'],
            'social': ['friends', 'chat', 'social', 'meet', 'talk', 'lonely', 'bored'],
            'school': ['student', 'school', 'homework', 'study', 'college', 'education'],
            'teen': ['teen', 'teenager', 'young', 'youth', 'adolescent', 'high school']
        }
        
        # Platform-specific optimization strategies
        self.platform_strategies = {
            'discord': {
                'join_servers': ['gaming', 'art', 'music', 'anime', 'memes', 'study'],
                'activity_patterns': ['evening', 'weekend', 'after_school'],
                'vulnerability_signals': ['looking for friends', 'new to server', 'shy but friendly']
            },
            'instagram': {
                'hashtag_strategy': ['#teen', '#student', '#art', '#music', '#aesthetic', '#lonely'],
                'posting_times': ['after_school', 'evening', 'weekend'],
                'story_content': ['daily_life', 'school', 'hobbies', 'mood']
            },
            'facebook': {
                'group_joining': ['local_teens', 'school_groups', 'hobby_groups', 'support_groups'],
                'activity_types': ['status_updates', 'photo_sharing', 'event_participation'],
                'friend_strategy': ['mutual_friends', 'local_connections', 'interest_based']
            },
            'snapchat': {
                'discovery_methods': ['quick_add', 'snap_map', 'mutual_friends', 'username_sharing'],
                'content_types': ['daily_snaps', 'stories', 'bitmoji_usage'],
                'engagement_tactics': ['snap_streaks', 'group_chats', 'location_sharing']
            },
            'tiktok': {
                'content_strategy': ['trending_sounds', 'popular_hashtags', 'duets', 'challenges'],
                'posting_schedule': ['daily', 'trending_times', 'consistent_schedule'],
                'engagement_methods': ['comments', 'follows', 'likes', 'shares']
            }
        }

    def create_comprehensive_profile(self, platform_type: str, deployment_strategy: str = 'standard') -> Dict:
        """Create a comprehensive profile with all assets and deployment plan"""
        
        # Generate base profile
        base_profile = self.profile_generator.generate_profile(platform_type)
        
        # Generate profile images
        profile_images = self._generate_profile_images(base_profile)
        
        # Create deployment strategy
        deployment_plan = self._create_deployment_strategy(base_profile, deployment_strategy)
        
        # Generate content calendar
        content_calendar = self._generate_content_calendar(base_profile, 30)  # 30 days
        
        # Create discovery optimization plan
        discovery_plan = self._create_discovery_plan(base_profile)
        
        # Save to database
        profile = DecoyProfile(
            name=base_profile['name'],
            username=base_profile['username'],
            age=base_profile['age'],
            location=base_profile['location'],
            platform_type=base_profile['platform_type'],
            bio=base_profile['bio'],
            interests=json.dumps(base_profile['interests']),
            backstory=base_profile['backstory'],
            status='created',
            profile_image_url=profile_images.get('profile_image'),
            cover_image_url=profile_images.get('cover_image'),
            additional_images=json.dumps(profile_images.get('additional_images', [])),
            created_by='profile_manager'
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return {
            'profile': profile.to_dict(),
            'images': profile_images,
            'deployment_plan': deployment_plan,
            'content_calendar': content_calendar,
            'discovery_plan': discovery_plan,
            'automation_settings': self._get_automation_settings(base_profile)
        }

    def _generate_profile_images(self, profile: Dict) -> Dict:
        """Generate AI images for profile"""
        images = {}
        
        if not self.image_generation_enabled:
            return images
        
        try:
            # Generate profile picture
            profile_prompt = self._create_image_prompt(profile, 'profile')
            images['profile_image'] = f"generated_profile_{profile['username']}.jpg"
            
            # Generate cover/banner image
            cover_prompt = self._create_image_prompt(profile, 'cover')
            images['cover_image'] = f"generated_cover_{profile['username']}.jpg"
            
            # Generate additional content images
            additional_images = []
            for i, interest in enumerate(profile['interests'][:3]):
                content_prompt = self._create_image_prompt(profile, 'content', interest)
                additional_images.append(f"generated_content_{profile['username']}_{i}.jpg")
            
            images['additional_images'] = additional_images
            
            # Store image generation prompts for later use
            images['prompts'] = {
                'profile': profile_prompt,
                'cover': cover_prompt,
                'content': [self._create_image_prompt(profile, 'content', interest) 
                           for interest in profile['interests'][:3]]
            }
            
        except Exception as e:
            print(f"Image generation error: {e}")
            images['error'] = str(e)
        
        return images

    def _create_image_prompt(self, profile: Dict, image_type: str, context: str = None) -> str:
        """Create detailed prompts for AI image generation"""
        
        age = profile['age']
        gender = profile.get('gender', 'female')
        interests = profile['interests']
        
        base_descriptors = {
            'female': f"young {age}-year-old teenage girl, friendly and approachable, natural smile",
            'male': f"young {age}-year-old teenage boy, friendly expression, casual demeanor"
        }
        
        if image_type == 'profile':
            return f"{base_descriptors[gender]}, selfie style photo, good lighting, casual clothing, bedroom or home setting, high quality, realistic, safe for work, social media profile picture style"
        
        elif image_type == 'cover':
            interest_themes = {
                'gaming': 'gaming setup, colorful LED lights, computer desk',
                'art': 'art supplies, drawings, creative workspace',
                'music': 'musical instruments, headphones, music notes',
                'photography': 'camera, photos, artistic composition'
            }
            
            main_interest = interests[0] if interests else 'general'
            theme = interest_themes.get(main_interest, 'teenage bedroom, posters, colorful decor')
            
            return f"teenage {gender} cover photo, {theme}, aesthetic, bright colors, social media banner style, high quality, safe for work"
        
        elif image_type == 'content' and context:
            content_themes = {
                'gaming': f"{base_descriptors[gender]} playing video games, gaming setup, casual",
                'art': f"{base_descriptors[gender]} drawing or creating art, art supplies visible",
                'music': f"{base_descriptors[gender]} with headphones or musical instrument",
                'school': f"{base_descriptors[gender]} studying or at school, books visible",
                'friends': f"{base_descriptors[gender]} with friends, group photo, happy"
            }
            
            return content_themes.get(context, f"{base_descriptors[gender]} casual photo, {context} related, natural lighting")
        
        return f"{base_descriptors[gender]}, casual photo, natural lighting, high quality, safe for work"

    def _create_deployment_strategy(self, profile: Dict, strategy_type: str) -> Dict:
        """Create platform-specific deployment strategy"""
        
        platform = profile['platform_type']
        platform_config = self.platform_strategies.get(platform, {})
        
        strategies = {
            'passive': {
                'description': 'Profile waits for contact, minimal proactive engagement',
                'activity_level': 'low',
                'posting_frequency': 'weekly',
                'engagement_style': 'reactive'
            },
            'standard': {
                'description': 'Balanced approach with regular activity and moderate engagement',
                'activity_level': 'medium',
                'posting_frequency': 'daily',
                'engagement_style': 'balanced'
            },
            'active': {
                'description': 'High visibility with frequent posting and proactive engagement',
                'activity_level': 'high',
                'posting_frequency': 'multiple_daily',
                'engagement_style': 'proactive'
            }
        }
        
        base_strategy = strategies.get(strategy_type, strategies['standard'])
        
        deployment_plan = {
            'strategy': base_strategy,
            'platform_specific': platform_config,
            'timeline': self._create_deployment_timeline(profile, strategy_type),
            'risk_assessment': self._assess_deployment_risks(profile),
            'success_metrics': self._define_success_metrics(profile),
            'escalation_triggers': self._define_escalation_triggers()
        }
        
        return deployment_plan

    def _create_deployment_timeline(self, profile: Dict, strategy_type: str) -> List[Dict]:
        """Create detailed deployment timeline"""
        
        timeline = []
        
        # Week 1: Profile setup and initial content
        timeline.append({
            'week': 1,
            'phase': 'setup',
            'tasks': [
                'Create platform account',
                'Upload profile images',
                'Complete bio and profile information',
                'Post initial content (3-5 posts)',
                'Begin following/friending relevant accounts'
            ],
            'goals': ['Establish authentic presence', 'Initial content baseline'],
            'metrics': ['Profile completion', 'Initial followers/friends']
        })
        
        # Week 2-3: Building presence
        timeline.append({
            'week': '2-3',
            'phase': 'building',
            'tasks': [
                'Regular content posting',
                'Join relevant groups/servers',
                'Engage with community content',
                'Respond to initial contacts',
                'Monitor discovery metrics'
            ],
            'goals': ['Increase visibility', 'Build authentic engagement'],
            'metrics': ['Follower growth', 'Engagement rate', 'Contact attempts']
        })
        
        # Week 4+: Active operation
        timeline.append({
            'week': '4+',
            'phase': 'operation',
            'tasks': [
                'Maintain regular posting schedule',
                'Monitor for suspicious contacts',
                'Document all interactions',
                'Escalate threats as needed',
                'Optimize discovery based on analytics'
            ],
            'goals': ['Attract target contacts', 'Gather evidence'],
            'metrics': ['Threat detection rate', 'Evidence quality', 'Conviction rate']
        })
        
        return timeline

    def _generate_content_calendar(self, profile: Dict, days: int) -> List[Dict]:
        """Generate automated content calendar"""
        
        calendar = []
        interests = profile['interests']
        platform = profile['platform_type']
        age = profile['age']
        
        content_types = {
            'instagram': ['photo', 'story', 'reel'],
            'facebook': ['status', 'photo', 'check-in'],
            'discord': ['message', 'status_update'],
            'snapchat': ['snap', 'story'],
            'tiktok': ['video', 'comment']
        }
        
        platform_content_types = content_types.get(platform, ['post'])
        
        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            
            # Determine posting frequency based on day of week
            is_weekend = date.weekday() >= 5
            posts_per_day = 2 if is_weekend else 1
            
            day_content = []
            
            for post_num in range(posts_per_day):
                content_type = random.choice(platform_content_types)
                interest = random.choice(interests)
                
                content = {
                    'date': date.strftime('%Y-%m-%d'),
                    'time': self._get_optimal_posting_time(platform, age),
                    'type': content_type,
                    'topic': interest,
                    'content': self._generate_content_text(content_type, interest, platform, age),
                    'hashtags': self._generate_hashtags(interest, platform),
                    'engagement_goal': random.choice(['discovery', 'authenticity', 'vulnerability']),
                    'risk_level': self._assess_content_risk(content_type, interest)
                }
                
                day_content.append(content)
            
            calendar.extend(day_content)
        
        return calendar

    def _get_optimal_posting_time(self, platform: str, age: int) -> str:
        """Get optimal posting times for platform and demographic"""
        
        # Teen posting patterns
        school_day_times = ['16:30', '17:45', '19:15', '20:30']  # After school
        weekend_times = ['10:30', '14:15', '16:45', '19:30', '21:00']
        
        # Platform-specific adjustments
        platform_adjustments = {
            'instagram': {'peak': '17:00-19:00', 'secondary': '20:00-22:00'},
            'tiktok': {'peak': '18:00-20:00', 'secondary': '21:00-23:00'},
            'discord': {'peak': '19:00-23:00', 'secondary': '15:00-17:00'},
            'snapchat': {'peak': '16:00-18:00', 'secondary': '20:00-22:00'},
            'facebook': {'peak': '15:00-17:00', 'secondary': '19:00-21:00'}
        }
        
        # Randomly select from optimal times
        current_day = datetime.now().weekday()
        if current_day >= 5:  # Weekend
            return random.choice(weekend_times)
        else:
            return random.choice(school_day_times)

    def _generate_hashtags(self, interest: str, platform: str) -> List[str]:
        """Generate platform-appropriate hashtags"""
        
        if platform not in ['instagram', 'tiktok']:
            return []
        
        base_hashtags = {
            'gaming': ['#gaming', '#gamer', '#minecraft', '#fortnite', '#twitch'],
            'art': ['#art', '#drawing', '#artist', '#creative', '#aesthetic'],
            'music': ['#music', '#musician', '#spotify', '#playlist', '#concert'],
            'school': ['#student', '#school', '#study', '#homework', '#college'],
            'friends': ['#friends', '#friendship', '#social', '#hangout', '#fun']
        }
        
        teen_hashtags = ['#teen', '#teenager', '#young', '#youth', '#student']
        location_hashtags = ['#uk', '#england', '#british']
        mood_hashtags = ['#mood', '#vibes', '#aesthetic', '#life', '#daily']
        
        # Combine relevant hashtags
        hashtags = []
        hashtags.extend(base_hashtags.get(interest, [])[:3])
        hashtags.extend(random.sample(teen_hashtags, 2))
        hashtags.extend(random.sample(mood_hashtags, 2))
        
        if random.choice([True, False]):
            hashtags.extend(random.sample(location_hashtags, 1))
        
        return hashtags[:8]  # Limit to 8 hashtags

    def _create_discovery_plan(self, profile: Dict) -> Dict:
        """Create comprehensive discovery optimization plan"""
        
        platform = profile['platform_type']
        interests = profile['interests']
        age = profile['age']
        location = profile['location']
        
        discovery_plan = {
            'seo_optimization': {
                'keywords': self._get_discovery_keywords(interests),
                'bio_optimization': self._optimize_bio_for_discovery(profile),
                'username_strategy': self._analyze_username_effectiveness(profile['username'])
            },
            'platform_specific': {
                'algorithm_optimization': self._get_algorithm_strategies(platform),
                'community_targeting': self._identify_target_communities(platform, interests),
                'engagement_tactics': self._define_engagement_tactics(platform, age)
            },
            'geographic_targeting': {
                'local_optimization': self._create_local_strategy(location),
                'regional_expansion': self._plan_regional_expansion(location),
                'timezone_optimization': self._optimize_for_timezone(location)
            },
            'vulnerability_signaling': {
                'subtle_indicators': self._define_vulnerability_signals(age),
                'escalation_triggers': self._define_discovery_escalation(),
                'safety_boundaries': self._establish_safety_boundaries()
            }
        }
        
        return discovery_plan

    def _get_discovery_keywords(self, interests: List[str]) -> List[str]:
        """Get SEO keywords for profile discovery"""
        
        keywords = []
        
        for interest in interests:
            if interest in self.discovery_keywords:
                keywords.extend(self.discovery_keywords[interest])
        
        # Add general teen keywords
        keywords.extend(self.discovery_keywords['teen'])
        keywords.extend(self.discovery_keywords['social'])
        
        return list(set(keywords))  # Remove duplicates

    def _assess_deployment_risks(self, profile: Dict) -> Dict:
        """Assess risks associated with profile deployment"""
        
        risks = {
            'legal_compliance': {
                'level': 'low',
                'factors': ['Age representation', 'Content appropriateness', 'Evidence integrity'],
                'mitigations': ['Legal review', 'Content guidelines', 'Audit trails']
            },
            'operational_security': {
                'level': 'medium',
                'factors': ['Profile detection', 'Platform suspension', 'Data exposure'],
                'mitigations': ['Authentic behavior', 'Platform compliance', 'Data encryption']
            },
            'officer_safety': {
                'level': 'low',
                'factors': ['Identity exposure', 'Personal safety', 'Psychological impact'],
                'mitigations': ['Anonymization', 'Support systems', 'Rotation schedules']
            }
        }
        
        return risks

    def _get_automation_settings(self, profile: Dict) -> Dict:
        """Define automation settings for profile management"""
        
        return {
            'content_posting': {
                'enabled': True,
                'frequency': 'daily',
                'time_randomization': True,
                'content_variation': True
            },
            'engagement_automation': {
                'enabled': True,
                'auto_like': False,  # Too risky
                'auto_follow': False,  # Manual approval required
                'auto_respond': True,  # Basic responses only
            },
            'monitoring': {
                'threat_detection': True,
                'analytics_collection': True,
                'alert_thresholds': {
                    'suspicious_contact': 1,
                    'threat_level_2': 1,
                    'evidence_capture': 1
                }
            },
            'safety_controls': {
                'auto_escalation': True,
                'content_filtering': True,
                'interaction_limits': True,
                'emergency_shutdown': True
            }
        }

    def deploy_profile_batch(self, count: int, platforms: List[str], strategy: str = 'standard') -> Dict:
        """Deploy multiple profiles with comprehensive setup"""
        
        deployment_results = {
            'successful': [],
            'failed': [],
            'total_count': count,
            'deployment_summary': {}
        }
        
        for i in range(count):
            try:
                platform = random.choice(platforms)
                
                # Create comprehensive profile
                profile_data = self.create_comprehensive_profile(platform, strategy)
                
                # Generate images if enabled
                if self.image_generation_enabled:
                    self._generate_and_save_images(profile_data)
                
                # Schedule initial content
                self._schedule_initial_content(profile_data)
                
                deployment_results['successful'].append({
                    'profile_id': profile_data['profile']['id'],
                    'platform': platform,
                    'username': profile_data['profile']['username'],
                    'deployment_plan': profile_data['deployment_plan']
                })
                
            except Exception as e:
                deployment_results['failed'].append({
                    'platform': platform,
                    'error': str(e)
                })
        
        # Generate deployment summary
        deployment_results['deployment_summary'] = {
            'success_rate': len(deployment_results['successful']) / count * 100,
            'platform_distribution': self._calculate_platform_distribution(deployment_results['successful']),
            'estimated_discovery_time': '2-4 weeks',
            'monitoring_requirements': 'Daily analytics review, immediate threat escalation'
        }
        
        return deployment_results

    def _generate_and_save_images(self, profile_data: Dict) -> None:
        """Generate and save AI images for profile"""
        # This would integrate with the media generation tools
        # For now, we'll store the prompts for manual generation
        pass

    def _schedule_initial_content(self, profile_data: Dict) -> None:
        """Schedule initial content posts for new profile"""
        
        profile_id = profile_data['profile']['id']
        content_calendar = profile_data['content_calendar']
        
        # Schedule first week of content
        for content_item in content_calendar[:7]:
            content = ProfileContent(
                profile_id=profile_id,
                content_type=content_item['type'],
                platform_type=profile_data['profile']['platform_type'],
                content_text=content_item['content'],
                scheduled_time=datetime.strptime(
                    f"{content_item['date']} {content_item['time']}", 
                    '%Y-%m-%d %H:%M'
                ),
                status='scheduled'
            )
            
            db.session.add(content)
        
        db.session.commit()

    def _calculate_platform_distribution(self, successful_profiles: List[Dict]) -> Dict:
        """Calculate distribution of profiles across platforms"""
        
        distribution = {}
        for profile in successful_profiles:
            platform = profile['platform']
            distribution[platform] = distribution.get(platform, 0) + 1
        
        return distribution

    def get_profile_performance_report(self, profile_id: int, days: int = 30) -> Dict:
        """Generate comprehensive performance report for a profile"""
        
        profile = DecoyProfile.query.get(profile_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Get analytics for the period
        start_date = datetime.now() - timedelta(days=days)
        analytics = ProfileAnalytics.query.filter(
            ProfileAnalytics.profile_id == profile_id,
            ProfileAnalytics.date_recorded >= start_date.date()
        ).all()
        
        # Calculate metrics
        total_views = sum(a.profile_views for a in analytics)
        total_contacts = sum(a.messages_received for a in analytics)
        total_threats = sum(a.threat_level_2 + a.threat_level_3 for a in analytics)
        
        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(profile, analytics)
        
        report = {
            'profile_info': profile.to_dict(),
            'performance_period': f'{days} days',
            'metrics': {
                'total_views': total_views,
                'total_contacts': total_contacts,
                'threat_detections': total_threats,
                'conversion_rate': (total_threats / total_contacts * 100) if total_contacts > 0 else 0,
                'daily_average_views': total_views / days,
                'discovery_effectiveness': self._calculate_discovery_effectiveness(analytics)
            },
            'trends': self._analyze_performance_trends(analytics),
            'recommendations': recommendations,
            'risk_assessment': self._assess_current_risks(profile, analytics),
            'next_actions': self._recommend_next_actions(profile, analytics)
        }
        
        return report

    def _generate_optimization_recommendations(self, profile: DecoyProfile, analytics: List[ProfileAnalytics]) -> List[str]:
        """Generate optimization recommendations based on performance"""
        
        recommendations = []
        
        # Analyze contact patterns
        total_contacts = sum(a.messages_received for a in analytics)
        if total_contacts < 5:
            recommendations.append("Increase profile visibility through more frequent posting")
            recommendations.append("Join additional communities relevant to profile interests")
        
        # Analyze threat detection
        total_threats = sum(a.threat_level_2 + a.threat_level_3 for a in analytics)
        if total_threats == 0 and total_contacts > 10:
            recommendations.append("Review threat detection sensitivity settings")
            recommendations.append("Consider adjusting vulnerability signals in profile")
        
        # Platform-specific recommendations
        if profile.platform_type == 'instagram':
            recommendations.append("Optimize hashtag usage for better discovery")
            recommendations.append("Post stories more frequently to increase visibility")
        elif profile.platform_type == 'discord':
            recommendations.append("Join more gaming servers to expand reach")
            recommendations.append("Participate in voice channels to build authenticity")
        
        return recommendations

    def _analyze_performance_trends(self, analytics: List[ProfileAnalytics]) -> Dict:
        """Analyze performance trends over time"""
        
        if len(analytics) < 7:
            return {'insufficient_data': True}
        
        # Sort by date
        analytics.sort(key=lambda x: x.date_recorded)
        
        # Calculate trends
        recent_week = analytics[-7:]
        previous_week = analytics[-14:-7] if len(analytics) >= 14 else []
        
        trends = {
            'views_trend': 'stable',
            'contacts_trend': 'stable',
            'threats_trend': 'stable'
        }
        
        if previous_week:
            recent_views = sum(a.profile_views for a in recent_week)
            previous_views = sum(a.profile_views for a in previous_week)
            
            if recent_views > previous_views * 1.2:
                trends['views_trend'] = 'increasing'
            elif recent_views < previous_views * 0.8:
                trends['views_trend'] = 'decreasing'
        
        return trends

    def _assess_current_risks(self, profile: DecoyProfile, analytics: List[ProfileAnalytics]) -> Dict:
        """Assess current operational risks"""
        
        risks = {
            'detection_risk': 'low',
            'exposure_risk': 'low',
            'operational_risk': 'low'
        }
        
        # Check for unusual patterns
        recent_contacts = sum(a.messages_received for a in analytics[-7:])
        if recent_contacts > 20:
            risks['detection_risk'] = 'medium'
        
        # Check threat levels
        high_threats = sum(a.threat_level_3 for a in analytics)
        if high_threats > 3:
            risks['operational_risk'] = 'high'
        
        return risks

    def _recommend_next_actions(self, profile: DecoyProfile, analytics: List[ProfileAnalytics]) -> List[str]:
        """Recommend next actions based on current state"""
        
        actions = []
        
        # Check if profile needs content update
        last_content = ProfileContent.query.filter_by(
            profile_id=profile.id
        ).order_by(ProfileContent.posted_time.desc()).first()
        
        if not last_content or (datetime.now() - last_content.posted_time).days > 3:
            actions.append("Schedule new content posts to maintain activity")
        
        # Check for pending threats
        recent_threats = sum(a.threat_level_2 + a.threat_level_3 for a in analytics[-7:])
        if recent_threats > 0:
            actions.append("Review recent threat detections for evidence quality")
            actions.append("Consider escalating high-priority cases")
        
        # General maintenance
        actions.append("Update profile analytics and performance metrics")
        actions.append("Review and optimize discovery strategies")
        
        return actions

    def _generate_content_text(self, content_type: str, interest: str, platform: str, age: int) -> str:
        """Generate realistic content text for posts"""
        
        # Age-appropriate slang and expressions
        teen_expressions = {
            13: ['omg', 'literally', 'so cool', 'amazing', 'love this', 'can\'t even'],
            14: ['yasss', 'periodt', 'no cap', 'slaps', 'hits different', 'vibes'],
            15: ['lowkey', 'highkey', 'deadass', 'facts', 'mood', 'same energy'],
            16: ['honestly', 'genuinely', 'actually', 'for real', 'not gonna lie']
        }
        
        expressions = teen_expressions.get(age, teen_expressions[14])
        
        content_templates = {
            'photo': [
                f"just finished working on my {interest} project! {random.choice(expressions)} proud of how it turned out ✨",
                f"spending my evening with {interest} as usual 😊 {random.choice(expressions)} love this",
                f"can't get enough of {interest} lately! anyone else obsessed? 💕"
            ],
            'status': [
                f"anyone else {random.choice(expressions)} into {interest}? just me? 😅",
                f"having such a good time with {interest} today! {random.choice(expressions)}",
                f"feeling really into {interest} lately, any recommendations? 🤔"
            ],
            'story': [
                f"currently: {interest} mode activated 🔥",
                f"today's vibe: all about {interest} {random.choice(expressions)}",
                f"guess what I'm doing... {interest} again! 😂 {random.choice(expressions)}"
            ]
        }
        
        template_list = content_templates.get(content_type, content_templates['status'])
        return random.choice(template_list)

    def _assess_content_risk(self, content_type: str, interest: str) -> str:
        """Assess risk level of content"""
        
        high_risk_interests = ['meeting people', 'dating', 'relationships']
        medium_risk_interests = ['social', 'friends', 'chatting']
        
        if interest in high_risk_interests:
            return 'high'
        elif interest in medium_risk_interests:
            return 'medium'
        else:
            return 'low'

    def _define_vulnerability_signals(self, age: int) -> List[str]:
        """Define subtle vulnerability signals for discovery"""
        
        signals = [
            'looking for new friends',
            'feeling a bit lonely lately',
            'parents are always busy with work',
            'want someone to talk to',
            'going through some stuff',
            'feeling misunderstood',
            'need advice about life',
            'wish I had someone who gets me'
        ]
        
        return signals

    def _define_discovery_escalation(self) -> Dict:
        """Define when to escalate discovery efforts"""
        
        return {
            'low_contact_threshold': {
                'days': 14,
                'min_contacts': 2,
                'action': 'increase_visibility'
            },
            'no_threat_threshold': {
                'days': 30,
                'min_contacts': 10,
                'action': 'adjust_vulnerability_signals'
            },
            'high_contact_threshold': {
                'contacts_per_day': 5,
                'action': 'review_profile_authenticity'
            }
        }

    def _establish_safety_boundaries(self) -> Dict:
        """Establish safety boundaries for profile operation"""
        
        return {
            'content_restrictions': [
                'No personal information sharing',
                'No meeting arrangements',
                'No inappropriate content',
                'No real location details'
            ],
            'interaction_limits': {
                'max_daily_conversations': 10,
                'max_conversation_length': 50,
                'auto_escalation_triggers': ['meeting requests', 'personal info requests', 'inappropriate content']
            },
            'emergency_protocols': {
                'immediate_escalation': ['threats', 'explicit content', 'meeting demands'],
                'profile_suspension': ['platform detection', 'safety concerns', 'legal issues'],
                'evidence_preservation': ['all_conversations', 'metadata', 'timestamps']
            }
        }

    def _calculate_discovery_effectiveness(self, analytics: List[ProfileAnalytics]) -> float:
        """Calculate how effectively the profile is being discovered"""
        
        if not analytics:
            return 0.0
        
        total_views = sum(a.profile_views for a in analytics)
        total_contacts = sum(a.messages_received for a in analytics)
        
        if total_views == 0:
            return 0.0
        
        # Discovery effectiveness = (contacts / views) * 100
        effectiveness = (total_contacts / total_views) * 100
        
        # Cap at 100% for realistic reporting
        return min(effectiveness, 100.0)

    def _get_algorithm_strategies(self, platform: str) -> Dict:
        """Get platform-specific algorithm optimization strategies"""
        
        strategies = {
            'instagram': {
                'posting_frequency': 'daily',
                'optimal_times': ['17:00-19:00', '20:00-22:00'],
                'engagement_tactics': ['stories', 'reels', 'hashtags'],
                'algorithm_factors': ['engagement_rate', 'posting_consistency', 'hashtag_relevance']
            },
            'tiktok': {
                'posting_frequency': 'daily',
                'optimal_times': ['18:00-20:00', '21:00-23:00'],
                'engagement_tactics': ['trending_sounds', 'challenges', 'duets'],
                'algorithm_factors': ['completion_rate', 'engagement_speed', 'trending_participation']
            },
            'discord': {
                'activity_frequency': 'multiple_daily',
                'optimal_times': ['19:00-23:00', '15:00-17:00'],
                'engagement_tactics': ['server_participation', 'voice_chat', 'gaming_activity'],
                'algorithm_factors': ['server_activity', 'friend_connections', 'message_frequency']
            }
        }
        
        return strategies.get(platform, {})

    def _identify_target_communities(self, platform: str, interests: List[str]) -> List[str]:
        """Identify target communities for profile deployment"""
        
        communities = {
            'discord': {
                'gaming': ['Minecraft servers', 'Roblox communities', 'Gaming cafes'],
                'art': ['Digital art servers', 'Drawing communities', 'Creative spaces'],
                'music': ['Music sharing servers', 'Artist communities', 'Playlist sharing']
            },
            'instagram': {
                'art': ['#digitalart', '#teenartist', '#artcommunity'],
                'music': ['#musiclover', '#teenmusician', '#playlist'],
                'photography': ['#photography', '#aesthetic', '#artsy']
            },
            'facebook': {
                'local': ['Teen groups in area', 'School communities', 'Local events'],
                'interests': ['Art groups', 'Music communities', 'Gaming groups']
            }
        }
        
        platform_communities = communities.get(platform, {})
        target_communities = []
        
        for interest in interests:
            if interest in platform_communities:
                target_communities.extend(platform_communities[interest])
        
        return target_communities

    def _define_engagement_tactics(self, platform: str, age: int) -> List[str]:
        """Define age and platform appropriate engagement tactics"""
        
        tactics = {
            'instagram': [
                'Like posts from similar accounts',
                'Comment on posts with age-appropriate responses',
                'Use relevant hashtags consistently',
                'Post stories regularly',
                'Follow accounts with similar interests'
            ],
            'discord': [
                'Join voice channels occasionally',
                'Participate in text conversations',
                'React to messages with emojis',
                'Share gaming achievements',
                'Ask for help or advice'
            ],
            'tiktok': [
                'Like and comment on trending videos',
                'Use trending sounds and hashtags',
                'Participate in challenges',
                'Duet with appropriate content',
                'Follow creators with similar content'
            ]
        }
        
        return tactics.get(platform, [])

    def _create_local_strategy(self, location: str) -> Dict:
        """Create location-based discovery strategy"""
        
        return {
            'local_hashtags': [f'#{location.lower()}', f'#{location.lower()}teen'],
            'local_groups': [f'{location} teens', f'{location} students', f'{location} community'],
            'local_events': ['School events', 'Community activities', 'Local meetups'],
            'geographic_signals': [f'Lives in {location}', f'From {location}', f'{location} area']
        }

    def _plan_regional_expansion(self, location: str) -> Dict:
        """Plan regional expansion strategy"""
        
        uk_regions = {
            'Southampton': ['Portsmouth', 'Winchester', 'Bournemouth'],
            'London': ['Surrey', 'Essex', 'Kent'],
            'Manchester': ['Liverpool', 'Leeds', 'Sheffield']
        }
        
        nearby_areas = uk_regions.get(location, [])
        
        return {
            'expansion_areas': nearby_areas,
            'timeline': '4-6 weeks after initial deployment',
            'strategy': 'Gradual expansion to nearby areas',
            'risk_assessment': 'Low - maintains regional authenticity'
        }

    def _optimize_for_timezone(self, location: str) -> Dict:
        """Optimize posting times for local timezone"""
        
        return {
            'timezone': 'GMT',
            'school_hours': '09:00-15:30',
            'peak_activity': '16:00-22:00',
            'weekend_patterns': '10:00-23:00',
            'optimal_posting_windows': ['16:30-18:00', '19:00-21:00']
        }

