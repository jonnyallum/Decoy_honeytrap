import os
import json
import random
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from threading import Thread
import logging
from src.models.profile import DecoyProfile, ProfileContent, ProfileAnalytics
from src.models.user import db

class ContentAutomationService:
    """Advanced service for automated content posting and management"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        
        # Content generation templates by platform and age
        self.content_templates = {
            'discord': {
                '13-14': {
                    'casual': [
                        "just finished {activity} and i'm so tired 😴",
                        "anyone else playing {game}? it's so fun!",
                        "omg {subject} homework is so hard 😭",
                        "can't wait for the weekend! {activity} time ✨",
                        "feeling {mood} today, anyone want to chat?",
                        "just discovered {interest} and i'm obsessed!",
                        "school was {adjective} today, how was yours?",
                        "watching {show} and it's amazing! anyone else seen it?"
                    ],
                    'gaming': [
                        "just beat {game_level} in {game}! so proud 🎮",
                        "looking for someone to play {game} with!",
                        "omg {game} is so addictive, been playing for hours",
                        "anyone know how to {game_task} in {game}?",
                        "just got {game_item} in {game}! finally!",
                        "streaming {game} if anyone wants to watch",
                        "new {game} update is amazing! loving the changes",
                        "stuck on {game_level}, any tips?"
                    ],
                    'social': [
                        "feeling lonely today, anyone want to be friends?",
                        "new to this server, everyone seems so nice!",
                        "having a rough day, could use some cheering up",
                        "anyone else feel like they don't fit in sometimes?",
                        "looking for people who understand me",
                        "wish i had more friends who get my interests",
                        "parents are being so annoying lately 🙄",
                        "feeling misunderstood, anyone else feel this way?"
                    ]
                },
                '15-16': {
                    'casual': [
                        "lowkey stressed about {subject} exam tomorrow",
                        "anyone else think {topic} is actually interesting?",
                        "deadass can't focus on homework rn",
                        "that {event} was actually fire ngl",
                        "feeling {mood} vibes today, wbu?",
                        "no cap, {activity} hits different when you're good at it",
                        "honestly {opinion}, don't @ me",
                        "periodt, {statement} and that's facts"
                    ],
                    'interests': [
                        "been working on my {skill} lately, getting better!",
                        "found this amazing {content_type} about {topic}",
                        "anyone else into {hobby}? need recommendations",
                        "just finished {project}, pretty proud of it",
                        "thinking about getting into {new_interest}",
                        "spent all day on {activity}, time well spent",
                        "{interest} community is so supportive and nice",
                        "learning {skill} is harder than i thought but fun"
                    ]
                }
            },
            'instagram': {
                '13-14': {
                    'photo_captions': [
                        "just me being me ✨ #{hashtag1} #{hashtag2}",
                        "feeling cute today 💕 #{mood} #{aesthetic}",
                        "lazy {day_part} vibes #{relaxed} #{cozy}",
                        "{activity} time! love doing this #{hobby} #{fun}",
                        "can't believe how {adjective} today was #{daily} #{life}",
                        "obsessed with {item/activity} lately #{obsession} #{love}",
                        "weekend mood: {activity} #{weekend} #{vibes}",
                        "just {achievement}, so happy! #{proud} #{achievement}"
                    ],
                    'story_content': [
                        "currently: {current_activity}",
                        "mood: {emoji} {mood_description}",
                        "today's vibe: {vibe_description}",
                        "obsessing over: {current_interest}",
                        "listening to: {music_type}",
                        "craving: {food/activity}",
                        "thinking about: {thought}",
                        "grateful for: {gratitude}"
                    ]
                },
                '15-16': {
                    'photo_captions': [
                        "main character energy today #{confidence} #{aesthetic}",
                        "it's giving {vibe} and i'm here for it #{mood}",
                        "periodt. #{statement} #{facts}",
                        "this {item/moment} really said {expression} #{relatable}",
                        "no thoughts, just {activity} #{mindless} #{fun}",
                        "that {adjective} life chose me #{lifestyle} #{blessed}",
                        "serving {type} looks today #{fashion} #{style}",
                        "when {situation} hits different #{relatable} #{mood}"
                    ]
                }
            },
            'facebook': {
                'general': {
                    'status_updates': [
                        "Having a great day at {location}! Love spending time {activity}.",
                        "Just finished {task/homework} and feeling accomplished!",
                        "Anyone else excited about {upcoming_event}?",
                        "Grateful for {positive_thing} in my life today.",
                        "Learning so much in {subject} class this year!",
                        "Weekend plans: {activity} with {people}. Can't wait!",
                        "Feeling blessed to have such amazing {people} in my life.",
                        "Just discovered {new_interest} and loving it!"
                    ],
                    'life_updates': [
                        "Started {new_activity} this week and really enjoying it!",
                        "Proud of myself for {achievement} today.",
                        "Looking forward to {future_event} next week.",
                        "Had such a fun time {activity} with {people}.",
                        "Feeling grateful for all the support from family and friends.",
                        "Excited to share that I {accomplishment}!",
                        "Beautiful day for {outdoor_activity}!",
                        "Thankful for {positive_aspect} in my life."
                    ]
                }
            },
            'snapchat': {
                'general': {
                    'snap_captions': [
                        "just vibing ✨",
                        "{current_activity} mode",
                        "today's mood: {emoji}",
                        "life update: {brief_update}",
                        "currently obsessed with {interest}",
                        "weekend energy: {vibe}",
                        "feeling {emotion} today",
                        "guess what i'm doing... {activity}!"
                    ],
                    'story_content': [
                        "daily check-in: {status}",
                        "current situation: {description}",
                        "today i learned: {fact/lesson}",
                        "grateful for: {gratitude}",
                        "excited about: {future_thing}",
                        "random thought: {thought}",
                        "life lately: {summary}",
                        "sending good vibes to: {people}"
                    ]
                }
            },
            'tiktok': {
                '13-14': {
                    'video_ideas': [
                        "POV: you're {scenario} #{pov} #{relatable}",
                        "Things that just hit different: {list_items} #{relatable}",
                        "Tell me you're {type} without telling me #{tellmewithout}",
                        "Rating {category} as a {age}yo #{rating} #{teen}",
                        "When {situation} happens #{relatable} #{mood}",
                        "Day in my life as a {description} #{dayinmylife}",
                        "Trying {trend/challenge} for the first time #{trend}",
                        "Things I wish I knew at {younger_age} #{advice}"
                    ]
                },
                '15-16': {
                    'video_ideas': [
                        "This trend but make it {personal_twist} #{trend}",
                        "Unpopular opinion: {opinion} #{unpopularopinion}",
                        "Green screen to show you {topic} #{greenscreen}",
                        "Explaining {complex_topic} in {simple_way} #{education}",
                        "Plot twist: {unexpected_element} #{plottwist}",
                        "That one friend who {characteristic} #{friend} #{relatable}",
                        "When someone says {statement} #{reaction} #{relatable}",
                        "Life hack: {useful_tip} #{lifehack} #{helpful}"
                    ]
                }
            }
        }
        
        # Platform-specific posting patterns
        self.posting_patterns = {
            'discord': {
                'frequency': 'multiple_daily',
                'peak_times': ['16:00-18:00', '19:00-23:00'],
                'content_mix': {'casual': 40, 'gaming': 35, 'social': 25},
                'response_likelihood': 0.8
            },
            'instagram': {
                'frequency': 'daily',
                'peak_times': ['17:00-19:00', '20:00-22:00'],
                'content_mix': {'photo': 60, 'story': 40},
                'response_likelihood': 0.6
            },
            'facebook': {
                'frequency': 'few_times_weekly',
                'peak_times': ['15:00-17:00', '19:00-21:00'],
                'content_mix': {'status': 70, 'life_update': 30},
                'response_likelihood': 0.5
            },
            'snapchat': {
                'frequency': 'multiple_daily',
                'peak_times': ['16:00-18:00', '20:00-22:00'],
                'content_mix': {'snap': 60, 'story': 40},
                'response_likelihood': 0.7
            },
            'tiktok': {
                'frequency': 'daily',
                'peak_times': ['18:00-20:00', '21:00-23:00'],
                'content_mix': {'video': 100},
                'response_likelihood': 0.4
            }
        }
        
        # Content variables for template filling
        self.content_variables = {
            'activities': ['gaming', 'drawing', 'listening to music', 'watching netflix', 'doing homework', 'chatting with friends'],
            'games': ['minecraft', 'roblox', 'among us', 'fortnite', 'genshin impact', 'valorant'],
            'subjects': ['math', 'english', 'science', 'history', 'art', 'music'],
            'moods': ['happy', 'excited', 'tired', 'bored', 'creative', 'chill'],
            'adjectives': ['amazing', 'boring', 'fun', 'weird', 'cool', 'interesting'],
            'interests': ['art', 'music', 'gaming', 'reading', 'photography', 'dance'],
            'shows': ['stranger things', 'wednesday', 'euphoria', 'the office', 'friends'],
            'emotions': ['happy', 'excited', 'grateful', 'peaceful', 'energetic', 'content']
        }
        
        # Vulnerability signaling content (used sparingly and carefully)
        self.vulnerability_content = {
            'subtle_signals': [
                "feeling a bit lonely lately, anyone want to chat?",
                "parents are always busy, wish someone understood me",
                "having a tough time at school, could use a friend",
                "feeling left out sometimes, anyone else feel this way?",
                "looking for someone who gets me",
                "wish i had someone to talk to about stuff",
                "going through some things, need advice",
                "feeling misunderstood by everyone around me"
            ],
            'usage_frequency': 0.05,  # 5% of posts
            'escalation_triggers': ['meeting requests', 'personal info requests', 'inappropriate responses']
        }

    def start_automation_service(self):
        """Start the content automation scheduler"""
        if self.is_running:
            return {'status': 'already_running'}
        
        self.is_running = True
        
        # Schedule content posting jobs
        schedule.every(30).minutes.do(self._check_scheduled_content)
        schedule.every(1).hours.do(self._generate_automatic_content)
        schedule.every(6).hours.do(self._update_activity_patterns)
        schedule.every(24).hours.do(self._cleanup_old_content)
        
        # Start scheduler thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        return {'status': 'started', 'message': 'Content automation service started successfully'}

    def stop_automation_service(self):
        """Stop the content automation scheduler"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        return {'status': 'stopped', 'message': 'Content automation service stopped'}

    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def generate_content_for_profile(self, profile: DecoyProfile, content_type: str = None) -> Dict:
        """Generate content for a specific profile"""
        
        try:
            # Get profile data
            interests = json.loads(profile.interests) if profile.interests else []
            age = profile.age
            platform = profile.platform_type
            
            # Determine age group
            age_group = '13-14' if age <= 14 else '15-16'
            
            # Get platform templates
            platform_templates = self.content_templates.get(platform, {})
            age_templates = platform_templates.get(age_group, platform_templates.get('general', {}))
            
            if not age_templates:
                return {'error': f'No templates found for platform {platform} and age {age}'}
            
            # Select content type if not specified
            if not content_type:
                content_types = list(age_templates.keys())
                content_type = random.choice(content_types)
            
            # Get templates for content type
            templates = age_templates.get(content_type, [])
            if not templates:
                return {'error': f'No templates found for content type {content_type}'}
            
            # Select random template
            template = random.choice(templates)
            
            # Fill template with variables
            content_text = self._fill_template(template, interests, age, platform)
            
            # Generate hashtags if applicable
            hashtags = self._generate_hashtags(interests, platform, content_type)
            
            # Determine posting time
            posting_time = self._get_optimal_posting_time(platform, age)
            
            return {
                'content_text': content_text,
                'content_type': content_type,
                'hashtags': hashtags,
                'platform_type': platform,
                'suggested_posting_time': posting_time,
                'engagement_prediction': self._predict_engagement(content_text, platform),
                'risk_assessment': self._assess_content_risk(content_text, content_type)
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _fill_template(self, template: str, interests: List[str], age: int, platform: str) -> str:
        """Fill template with appropriate variables"""
        
        filled_template = template
        
        # Replace placeholders with random selections
        replacements = {
            '{activity}': random.choice(self.content_variables['activities']),
            '{game}': random.choice(self.content_variables['games']),
            '{subject}': random.choice(self.content_variables['subjects']),
            '{mood}': random.choice(self.content_variables['moods']),
            '{adjective}': random.choice(self.content_variables['adjectives']),
            '{interest}': random.choice(interests) if interests else random.choice(self.content_variables['interests']),
            '{show}': random.choice(self.content_variables['shows']),
            '{emotion}': random.choice(self.content_variables['emotions'])
        }
        
        # Add age-specific replacements
        if age <= 14:
            replacements.update({
                '{game_level}': random.choice(['level 5', 'the boss', 'that hard part']),
                '{game_task}': random.choice(['beat this level', 'get this item', 'unlock this area']),
                '{game_item}': random.choice(['a rare sword', 'new skin', 'special power'])
            })
        else:
            replacements.update({
                '{opinion}': random.choice(['this is actually good', 'people sleep on this', 'this hits different']),
                '{statement}': random.choice(['this is facts', 'no cap', 'periodt']),
                '{vibe}': random.choice(['main character', 'aesthetic', 'unbothered'])
            })
        
        # Apply replacements
        for placeholder, replacement in replacements.items():
            filled_template = filled_template.replace(placeholder, replacement)
        
        return filled_template

    def _generate_hashtags(self, interests: List[str], platform: str, content_type: str) -> List[str]:
        """Generate appropriate hashtags for content"""
        
        if platform not in ['instagram', 'tiktok']:
            return []
        
        hashtags = []
        
        # Add interest-based hashtags
        interest_hashtags = {
            'gaming': ['#gaming', '#gamer', '#videogames'],
            'art': ['#art', '#drawing', '#creative'],
            'music': ['#music', '#musician', '#playlist'],
            'photography': ['#photography', '#aesthetic', '#artsy'],
            'reading': ['#bookworm', '#reading', '#books'],
            'dance': ['#dance', '#dancing', '#choreography']
        }
        
        for interest in interests[:2]:  # Limit to 2 interests
            if interest in interest_hashtags:
                hashtags.extend(interest_hashtags[interest][:2])
        
        # Add general teen hashtags
        teen_hashtags = ['#teen', '#teenager', '#student', '#youth']
        hashtags.extend(random.sample(teen_hashtags, 2))
        
        # Add mood/aesthetic hashtags
        mood_hashtags = ['#mood', '#vibes', '#aesthetic', '#daily', '#life']
        hashtags.extend(random.sample(mood_hashtags, 2))
        
        # Platform-specific hashtags
        if platform == 'tiktok':
            tiktok_hashtags = ['#fyp', '#foryou', '#viral', '#trending']
            hashtags.extend(random.sample(tiktok_hashtags, 1))
        
        return hashtags[:8]  # Limit to 8 hashtags

    def _get_optimal_posting_time(self, platform: str, age: int) -> str:
        """Get optimal posting time for platform and age group"""
        
        pattern = self.posting_patterns.get(platform, {})
        peak_times = pattern.get('peak_times', ['17:00-19:00'])
        
        # Select random time from peak periods
        time_range = random.choice(peak_times)
        start_time, end_time = time_range.split('-')
        
        # Generate random time within range
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        
        # Random hour within range
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        
        return f"{hour:02d}:{minute:02d}"

    def _predict_engagement(self, content_text: str, platform: str) -> Dict:
        """Predict engagement level for content"""
        
        # Simple engagement prediction based on content characteristics
        engagement_score = 0.5  # Base score
        
        # Boost for questions
        if '?' in content_text:
            engagement_score += 0.2
        
        # Boost for emotional content
        emotional_words = ['love', 'hate', 'excited', 'sad', 'happy', 'angry', 'amazing']
        for word in emotional_words:
            if word in content_text.lower():
                engagement_score += 0.1
                break
        
        # Boost for platform-specific elements
        if platform == 'instagram' and '#' in content_text:
            engagement_score += 0.1
        
        if platform == 'discord' and any(emoji in content_text for emoji in ['😊', '😭', '✨', '🎮']):
            engagement_score += 0.1
        
        # Platform response likelihood
        platform_likelihood = self.posting_patterns.get(platform, {}).get('response_likelihood', 0.5)
        final_score = min(engagement_score * platform_likelihood, 1.0)
        
        return {
            'predicted_engagement': final_score,
            'engagement_level': 'high' if final_score > 0.7 else 'medium' if final_score > 0.4 else 'low',
            'factors': {
                'has_question': '?' in content_text,
                'has_emotion': any(word in content_text.lower() for word in emotional_words),
                'platform_optimized': True
            }
        }

    def _assess_content_risk(self, content_text: str, content_type: str) -> Dict:
        """Assess risk level of content"""
        
        risk_level = 'low'
        risk_factors = []
        
        # Check for vulnerability signals
        vulnerability_indicators = [
            'lonely', 'misunderstood', 'parents', 'trouble', 'need someone',
            'looking for friends', 'no one understands', 'feeling left out'
        ]
        
        for indicator in vulnerability_indicators:
            if indicator in content_text.lower():
                risk_level = 'medium'
                risk_factors.append(f'Contains vulnerability signal: {indicator}')
        
        # Check for high-risk content types
        high_risk_types = ['social', 'vulnerability']
        if content_type in high_risk_types:
            if risk_level == 'low':
                risk_level = 'medium'
            risk_factors.append(f'High-risk content type: {content_type}')
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'monitoring_required': risk_level in ['medium', 'high'],
            'escalation_triggers': self.vulnerability_content['escalation_triggers']
        }

    def schedule_content_for_profile(self, profile_id: int, content_data: Dict, schedule_time: datetime) -> Dict:
        """Schedule content for posting"""
        
        try:
            # Create scheduled content entry
            content = ProfileContent(
                profile_id=profile_id,
                content_type=content_data.get('content_type', 'post'),
                platform_type=content_data.get('platform_type'),
                content_text=content_data.get('content_text'),
                content_media=json.dumps(content_data.get('media', [])),
                scheduled_time=schedule_time,
                status='scheduled'
            )
            
            db.session.add(content)
            db.session.commit()
            
            return {
                'success': True,
                'content_id': content.id,
                'scheduled_time': schedule_time.isoformat(),
                'message': 'Content scheduled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_content_calendar(self, profile_id: int, days: int = 30) -> Dict:
        """Generate a complete content calendar for a profile"""
        
        try:
            profile = DecoyProfile.query.get(profile_id)
            if not profile:
                return {'error': 'Profile not found'}
            
            calendar = []
            platform = profile.platform_type
            posting_pattern = self.posting_patterns.get(platform, {})
            frequency = posting_pattern.get('frequency', 'daily')
            
            # Determine posts per day based on frequency
            posts_per_day = {
                'multiple_daily': random.randint(2, 4),
                'daily': 1,
                'few_times_weekly': 0.4,  # Will be handled probabilistically
                'weekly': 0.14
            }.get(frequency, 1)
            
            for day in range(days):
                date = datetime.now() + timedelta(days=day)
                
                # Determine if we should post today (for lower frequency platforms)
                if frequency == 'few_times_weekly':
                    should_post = random.random() < 0.4  # 40% chance per day
                    day_posts = 1 if should_post else 0
                elif frequency == 'weekly':
                    should_post = random.random() < 0.14  # ~1 post per week
                    day_posts = 1 if should_post else 0
                else:
                    day_posts = posts_per_day if isinstance(posts_per_day, int) else 1
                
                for post_num in range(day_posts):
                    # Generate content
                    content_data = self.generate_content_for_profile(profile)
                    
                    if 'error' not in content_data:
                        # Schedule at optimal time
                        posting_time = content_data['suggested_posting_time']
                        hour, minute = map(int, posting_time.split(':'))
                        
                        scheduled_datetime = date.replace(
                            hour=hour, 
                            minute=minute, 
                            second=0, 
                            microsecond=0
                        )
                        
                        calendar_entry = {
                            'date': date.strftime('%Y-%m-%d'),
                            'time': posting_time,
                            'scheduled_datetime': scheduled_datetime.isoformat(),
                            'content': content_data,
                            'auto_schedule': True
                        }
                        
                        calendar.append(calendar_entry)
            
            return {
                'profile_id': profile_id,
                'platform': platform,
                'calendar_period': f'{days} days',
                'total_posts': len(calendar),
                'average_posts_per_day': len(calendar) / days,
                'calendar': calendar
            }
            
        except Exception as e:
            return {'error': str(e)}

    def auto_schedule_calendar(self, profile_id: int, calendar_data: List[Dict]) -> Dict:
        """Automatically schedule all content from a calendar"""
        
        try:
            scheduled_count = 0
            failed_count = 0
            errors = []
            
            for entry in calendar_data:
                try:
                    scheduled_datetime = datetime.fromisoformat(entry['scheduled_datetime'])
                    content_data = entry['content']
                    
                    result = self.schedule_content_for_profile(
                        profile_id, 
                        content_data, 
                        scheduled_datetime
                    )
                    
                    if result['success']:
                        scheduled_count += 1
                    else:
                        failed_count += 1
                        errors.append(result['error'])
                        
                except Exception as e:
                    failed_count += 1
                    errors.append(str(e))
            
            return {
                'profile_id': profile_id,
                'scheduled_count': scheduled_count,
                'failed_count': failed_count,
                'total_entries': len(calendar_data),
                'success_rate': (scheduled_count / len(calendar_data)) * 100 if calendar_data else 0,
                'errors': errors[:5]  # Limit error list
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _check_scheduled_content(self):
        """Check for content that should be posted now"""
        
        try:
            current_time = datetime.now()
            
            # Get content scheduled for posting (within 30 minutes)
            scheduled_content = ProfileContent.query.filter(
                ProfileContent.status == 'scheduled',
                ProfileContent.scheduled_time <= current_time + timedelta(minutes=30),
                ProfileContent.scheduled_time >= current_time - timedelta(minutes=30)
            ).all()
            
            for content in scheduled_content:
                try:
                    # Simulate posting (in real implementation, this would post to actual platforms)
                    self._simulate_content_posting(content)
                    
                    # Update status
                    content.status = 'posted'
                    content.posted_time = current_time
                    
                    # Update profile activity
                    profile = content.profile
                    profile.last_activity = current_time
                    
                    db.session.commit()
                    
                    logging.info(f"Posted content {content.id} for profile {content.profile_id}")
                    
                except Exception as e:
                    content.status = 'failed'
                    db.session.commit()
                    logging.error(f"Failed to post content {content.id}: {str(e)}")
            
        except Exception as e:
            logging.error(f"Error checking scheduled content: {str(e)}")

    def _simulate_content_posting(self, content: ProfileContent):
        """Simulate posting content to platform (placeholder for actual posting)"""
        
        # In a real implementation, this would:
        # 1. Connect to the actual platform API
        # 2. Post the content using the profile's credentials
        # 3. Handle platform-specific formatting
        # 4. Manage rate limits and API restrictions
        
        # For now, we'll just log the posting simulation
        logging.info(f"SIMULATED POST - Platform: {content.platform_type}, "
                    f"Content: {content.content_text[:50]}...")
        
        # Simulate engagement (random likes, comments, etc.)
        if random.random() < 0.3:  # 30% chance of engagement
            content.likes_count = random.randint(1, 10)
            content.comments_count = random.randint(0, 3)

    def _generate_automatic_content(self):
        """Generate and schedule automatic content for active profiles"""
        
        try:
            # Get active profiles that need content
            active_profiles = DecoyProfile.query.filter(
                DecoyProfile.status.in_(['deployed', 'active'])
            ).all()
            
            for profile in active_profiles:
                try:
                    # Check if profile needs new content
                    last_content = ProfileContent.query.filter_by(
                        profile_id=profile.id
                    ).order_by(ProfileContent.scheduled_time.desc()).first()
                    
                    # If no content in last 24 hours, generate new content
                    if not last_content or (datetime.now() - last_content.scheduled_time).days >= 1:
                        
                        # Generate content
                        content_data = self.generate_content_for_profile(profile)
                        
                        if 'error' not in content_data:
                            # Schedule for next optimal time
                            next_posting_time = datetime.now() + timedelta(
                                hours=random.randint(1, 6)
                            )
                            
                            self.schedule_content_for_profile(
                                profile.id,
                                content_data,
                                next_posting_time
                            )
                            
                            logging.info(f"Auto-generated content for profile {profile.id}")
                
                except Exception as e:
                    logging.error(f"Error generating content for profile {profile.id}: {str(e)}")
        
        except Exception as e:
            logging.error(f"Error in automatic content generation: {str(e)}")

    def _update_activity_patterns(self):
        """Update activity patterns based on analytics"""
        
        try:
            # Analyze posting performance and adjust patterns
            # This would involve machine learning in a full implementation
            
            logging.info("Updated activity patterns based on analytics")
            
        except Exception as e:
            logging.error(f"Error updating activity patterns: {str(e)}")

    def _cleanup_old_content(self):
        """Clean up old content entries"""
        
        try:
            # Remove old failed/cancelled content
            cutoff_date = datetime.now() - timedelta(days=30)
            
            old_content = ProfileContent.query.filter(
                ProfileContent.status.in_(['failed', 'cancelled']),
                ProfileContent.created_at < cutoff_date
            ).all()
            
            for content in old_content:
                db.session.delete(content)
            
            db.session.commit()
            
            logging.info(f"Cleaned up {len(old_content)} old content entries")
            
        except Exception as e:
            logging.error(f"Error cleaning up old content: {str(e)}")

    def get_automation_status(self) -> Dict:
        """Get current status of automation service"""
        
        return {
            'is_running': self.is_running,
            'scheduler_active': self.scheduler_thread is not None and self.scheduler_thread.is_alive(),
            'scheduled_jobs': len(schedule.jobs),
            'next_run_times': [str(job.next_run) for job in schedule.jobs[:5]]
        }

    def get_content_statistics(self) -> Dict:
        """Get content generation and posting statistics"""
        
        try:
            # Get content statistics
            total_content = ProfileContent.query.count()
            posted_content = ProfileContent.query.filter_by(status='posted').count()
            scheduled_content = ProfileContent.query.filter_by(status='scheduled').count()
            failed_content = ProfileContent.query.filter_by(status='failed').count()
            
            # Platform breakdown
            platform_stats = db.session.query(
                ProfileContent.platform_type,
                db.func.count(ProfileContent.id)
            ).group_by(ProfileContent.platform_type).all()
            
            # Recent activity
            recent_posts = ProfileContent.query.filter(
                ProfileContent.posted_time >= datetime.now() - timedelta(days=7)
            ).count()
            
            return {
                'total_content': total_content,
                'posted_content': posted_content,
                'scheduled_content': scheduled_content,
                'failed_content': failed_content,
                'success_rate': (posted_content / total_content * 100) if total_content > 0 else 0,
                'platform_breakdown': dict(platform_stats),
                'recent_posts_7_days': recent_posts,
                'automation_status': self.get_automation_status()
            }
            
        except Exception as e:
            return {'error': str(e)}

    def create_custom_content_template(self, platform: str, age_group: str, content_type: str, templates: List[str]) -> Dict:
        """Create custom content templates"""
        
        try:
            # Validate inputs
            if platform not in self.content_templates:
                self.content_templates[platform] = {}
            
            if age_group not in self.content_templates[platform]:
                self.content_templates[platform][age_group] = {}
            
            # Add custom templates
            self.content_templates[platform][age_group][content_type] = templates
            
            return {
                'success': True,
                'platform': platform,
                'age_group': age_group,
                'content_type': content_type,
                'template_count': len(templates),
                'message': 'Custom templates created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_content_performance(self, profile_id: int, days: int = 30) -> Dict:
        """Analyze content performance for a profile"""
        
        try:
            # Get content for analysis period
            start_date = datetime.now() - timedelta(days=days)
            content_items = ProfileContent.query.filter(
                ProfileContent.profile_id == profile_id,
                ProfileContent.posted_time >= start_date
            ).all()
            
            if not content_items:
                return {'message': 'No content found for analysis period'}
            
            # Analyze performance metrics
            total_posts = len(content_items)
            total_likes = sum(item.likes_count for item in content_items)
            total_comments = sum(item.comments_count for item in content_items)
            
            # Content type performance
            type_performance = {}
            for item in content_items:
                content_type = item.content_type
                if content_type not in type_performance:
                    type_performance[content_type] = {
                        'count': 0,
                        'likes': 0,
                        'comments': 0
                    }
                
                type_performance[content_type]['count'] += 1
                type_performance[content_type]['likes'] += item.likes_count
                type_performance[content_type]['comments'] += item.comments_count
            
            # Calculate averages
            for content_type in type_performance:
                data = type_performance[content_type]
                data['avg_likes'] = data['likes'] / data['count'] if data['count'] > 0 else 0
                data['avg_comments'] = data['comments'] / data['count'] if data['count'] > 0 else 0
            
            return {
                'profile_id': profile_id,
                'analysis_period': f'{days} days',
                'total_posts': total_posts,
                'total_engagement': total_likes + total_comments,
                'average_likes_per_post': total_likes / total_posts if total_posts > 0 else 0,
                'average_comments_per_post': total_comments / total_posts if total_posts > 0 else 0,
                'content_type_performance': type_performance,
                'recommendations': self._generate_content_recommendations(type_performance)
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _generate_content_recommendations(self, type_performance: Dict) -> List[str]:
        """Generate content recommendations based on performance"""
        
        recommendations = []
        
        if not type_performance:
            return ['Generate more content to analyze performance']
        
        # Find best performing content type
        best_type = max(type_performance.keys(), 
                       key=lambda x: type_performance[x]['avg_likes'] + type_performance[x]['avg_comments'])
        
        recommendations.append(f"Focus more on {best_type} content - it performs best")
        
        # Find underperforming content
        for content_type, data in type_performance.items():
            if data['avg_likes'] < 1 and data['count'] > 3:
                recommendations.append(f"Consider improving {content_type} content quality")
        
        # General recommendations
        recommendations.extend([
            "Post during peak engagement hours",
            "Use relevant hashtags for better discovery",
            "Engage with comments to boost algorithm visibility",
            "Vary content types to maintain audience interest"
        ])
        
        return recommendations

