import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.profile import DecoyProfile, ProfileContent
from src.models.user import db

class ContentManager:
    """Service for managing and scheduling profile content"""
    
    def __init__(self):
        self.content_templates = {
            'instagram': {
                'photo_captions': [
                    "just vibing today ✨ {hashtags}",
                    "current mood: {emotion} 💕 {hashtags}",
                    "can't believe it's already {time_period}! {hashtags}",
                    "feeling {emotion} about {topic} rn {hashtags}",
                    "anyone else obsessed with {topic}? {hashtags}",
                    "today's aesthetic: {aesthetic} {hashtags}",
                    "manifesting {goal} ✨ {hashtags}"
                ],
                'story_texts': [
                    "currently: {activity}",
                    "mood: {emotion}",
                    "today's vibe ✨",
                    "guess what I'm doing...",
                    "bored someone talk to me",
                    "feeling {emotion} today",
                    "anyone else {activity}?"
                ],
                'hashtags': [
                    '#teen #aesthetic #vibes #mood',
                    '#student #life #young #free',
                    '#art #creative #inspiration #dream',
                    '#music #love #happy #blessed',
                    '#friends #fun #memories #smile',
                    '#selfie #natural #beautiful #confident',
                    '#school #study #future #goals'
                ]
            },
            'facebook': {
                'status_updates': [
                    "Having such a {emotion} day! Anyone else feeling {emotion} about {topic}?",
                    "Can't believe how fast {time_period} is going by! Time to focus on {goal}.",
                    "Really getting into {topic} lately. Any recommendations?",
                    "Feeling grateful for {positive_thing} today 💕",
                    "School is {emotion} but at least I have {topic} to look forward to!",
                    "Anyone else think {opinion}? Just me? 😅",
                    "Spending my {time_period} working on {activity}. So {emotion}!"
                ],
                'check_ins': [
                    "at {location} with friends 😊",
                    "studying at {location} 📚",
                    "hanging out at {location}",
                    "family time at {location} ❤️"
                ]
            },
            'discord': {
                'status_messages': [
                    "playing {game}",
                    "listening to {music}",
                    "working on {project}",
                    "feeling {emotion}",
                    "studying for {subject}",
                    "chatting with friends",
                    "creating {art_type}"
                ],
                'server_messages': [
                    "hey everyone! new to this server, seems cool!",
                    "anyone want to {activity} together?",
                    "just finished {achievement}, feeling proud!",
                    "having trouble with {problem}, any advice?",
                    "love this community, everyone's so nice!",
                    "can't wait for {event}!",
                    "anyone else into {interest}?"
                ]
            },
            'snapchat': {
                'snap_captions': [
                    "mood rn",
                    "current vibe ✨",
                    "feeling {emotion}",
                    "today's look",
                    "bored af",
                    "someone snap me",
                    "good {time_period} vibes"
                ],
                'story_captions': [
                    "daily life update",
                    "what I'm up to today",
                    "current situation",
                    "today's mood",
                    "life lately",
                    "weekend vibes",
                    "school life"
                ]
            },
            'tiktok': {
                'video_captions': [
                    "POV: you're {situation} #fyp #teen #relatable",
                    "when you {action} and {result} #mood #life #real",
                    "me trying to {goal} be like: #struggle #teen #funny",
                    "this is so {emotion} #aesthetic #vibes #mood",
                    "anyone else {question}? #relatable #teen #real",
                    "current obsession: {topic} #obsessed #love #life",
                    "feeling {emotion} about {topic} #mood #thoughts #real"
                ]
            }
        }
        
        self.content_variables = {
            'emotions': ['happy', 'excited', 'nervous', 'grateful', 'confused', 'proud', 'creative', 'motivated'],
            'activities': ['drawing', 'gaming', 'studying', 'listening to music', 'chatting', 'creating art', 'reading'],
            'topics': ['art', 'music', 'gaming', 'school', 'friends', 'creativity', 'future plans', 'hobbies'],
            'time_periods': ['weekend', 'week', 'month', 'semester', 'year', 'summer', 'winter'],
            'goals': ['good grades', 'new friends', 'creative projects', 'learning new skills', 'happiness'],
            'aesthetics': ['soft girl', 'dark academia', 'cottagecore', 'minimalist', 'vintage', 'indie'],
            'locations': ['library', 'park', 'cafe', 'school', 'home', 'mall', 'beach'],
            'games': ['Minecraft', 'Roblox', 'Among Us', 'Valorant', 'Genshin Impact', 'Animal Crossing'],
            'music': ['Taylor Swift', 'Billie Eilish', 'indie music', 'K-pop', 'pop music', 'alternative rock'],
            'subjects': ['math', 'english', 'science', 'history', 'art', 'music', 'languages']
        }

    def generate_content(self, profile: DecoyProfile, content_type: str, 
                        scheduled_time: datetime = None) -> Dict:
        """Generate content for a specific profile and platform"""
        
        platform = profile.platform_type
        interests = json.loads(profile.interests) if profile.interests else []
        
        # Get platform-specific templates
        templates = self.content_templates.get(platform, {})
        
        if content_type not in templates:
            # Fallback to generic content
            content_text = self._generate_generic_content(profile, content_type)
        else:
            content_text = self._generate_platform_content(profile, content_type, templates[content_type])
        
        # Generate media suggestions if applicable
        media_suggestions = self._generate_media_suggestions(profile, content_type, platform)
        
        content = {
            'profile_id': profile.id,
            'content_type': content_type,
            'platform_type': platform,
            'content_text': content_text,
            'content_media': json.dumps(media_suggestions),
            'scheduled_time': scheduled_time or self._get_optimal_posting_time(platform),
            'status': 'draft',
            'engagement_goal': self._determine_engagement_goal(content_type, profile.age)
        }
        
        return content

    def _generate_platform_content(self, profile: DecoyProfile, content_type: str, 
                                 templates: List[str]) -> str:
        """Generate content using platform-specific templates"""
        
        template = random.choice(templates)
        interests = json.loads(profile.interests) if profile.interests else []
        
        # Fill template variables
        variables = {
            'emotion': random.choice(self.content_variables['emotions']),
            'activity': random.choice(self.content_variables['activities']),
            'topic': random.choice(interests) if interests else random.choice(self.content_variables['topics']),
            'time_period': random.choice(self.content_variables['time_periods']),
            'goal': random.choice(self.content_variables['goals']),
            'aesthetic': random.choice(self.content_variables['aesthetics']),
            'location': random.choice(self.content_variables['locations']),
            'game': random.choice(self.content_variables['games']),
            'music': random.choice(self.content_variables['music']),
            'subject': random.choice(self.content_variables['subjects'])
        }
        
        # Add platform-specific variables
        if profile.platform_type == 'instagram':
            variables['hashtags'] = random.choice(self.content_templates['instagram']['hashtags'])
        
        # Fill template
        try:
            content = template.format(**variables)
        except KeyError:
            # If template has variables we don't have, use as-is
            content = template
        
        return content

    def _generate_generic_content(self, profile: DecoyProfile, content_type: str) -> str:
        """Generate generic content when platform-specific templates aren't available"""
        
        interests = json.loads(profile.interests) if profile.interests else []
        topic = random.choice(interests) if interests else random.choice(self.content_variables['topics'])
        emotion = random.choice(self.content_variables['emotions'])
        
        generic_templates = [
            f"really into {topic} lately!",
            f"feeling {emotion} about {topic} today",
            f"anyone else love {topic} as much as I do?",
            f"having such a {emotion} day!",
            f"can't stop thinking about {topic}",
            f"so {emotion} to share my {topic} with everyone!"
        ]
        
        return random.choice(generic_templates)

    def _generate_media_suggestions(self, profile: DecoyProfile, content_type: str, 
                                  platform: str) -> List[Dict]:
        """Generate media suggestions for content"""
        
        media_suggestions = []
        interests = json.loads(profile.interests) if profile.interests else []
        
        # Determine if media is needed
        media_types = {
            'instagram': ['photo', 'story'],
            'facebook': ['photo', 'video'],
            'snapchat': ['photo', 'video'],
            'tiktok': ['video'],
            'discord': []  # Usually text-based
        }
        
        if content_type in media_types.get(platform, []):
            if content_type in ['photo', 'story']:
                # Generate image prompt
                image_prompt = self._generate_content_image_prompt(profile, interests, content_type)
                media_suggestions.append({
                    'type': 'image',
                    'prompt': image_prompt,
                    'style': self._get_platform_image_style(platform)
                })
            elif content_type == 'video':
                # Generate video concept
                video_concept = self._generate_video_concept(profile, interests)
                media_suggestions.append({
                    'type': 'video',
                    'concept': video_concept,
                    'duration': '15-30 seconds'
                })
        
        return media_suggestions

    def _generate_content_image_prompt(self, profile: DecoyProfile, interests: List[str], 
                                     content_type: str) -> str:
        """Generate AI image prompt for content"""
        
        age = profile.age
        gender = 'teenage girl' if 'emma' in profile.name.lower() else 'teenage person'
        
        settings = ['bedroom', 'study desk', 'park', 'cafe', 'school', 'home']
        activities = ['studying', 'drawing', 'listening to music', 'reading', 'using phone']
        
        if interests:
            activity = f"doing {random.choice(interests)}" if random.choice([True, False]) else random.choice(activities)
        else:
            activity = random.choice(activities)
        
        setting = random.choice(settings)
        
        prompt = f"{gender}, {age} years old, {activity}, {setting}, natural lighting, casual clothing, social media style photo, realistic, safe for work"
        
        return prompt

    def _generate_video_concept(self, profile: DecoyProfile, interests: List[str]) -> str:
        """Generate video concept for platforms like TikTok"""
        
        concepts = [
            "day in the life routine",
            "showing off art/creative work",
            "lip sync to popular song",
            "study routine or tips",
            "room tour or aesthetic setup",
            "getting ready routine",
            "hobby showcase",
            "relatable teen moments"
        ]
        
        if interests:
            interest_concepts = [f"showcasing {interest}" for interest in interests[:2]]
            concepts.extend(interest_concepts)
        
        return random.choice(concepts)

    def _get_platform_image_style(self, platform: str) -> str:
        """Get platform-appropriate image style"""
        
        styles = {
            'instagram': 'aesthetic, well-lit, Instagram-style',
            'facebook': 'natural, casual, social media',
            'snapchat': 'casual, spontaneous, Snapchat-style',
            'tiktok': 'trendy, engaging, TikTok-style',
            'discord': 'casual, gaming setup'
        }
        
        return styles.get(platform, 'casual, social media style')

    def _get_optimal_posting_time(self, platform: str) -> datetime:
        """Calculate optimal posting time based on platform and teen behavior"""
        
        now = datetime.utcnow()
        
        # Teen activity patterns
        optimal_hours = {
            'instagram': [16, 17, 18, 19, 20, 21],  # After school hours
            'facebook': [17, 18, 19, 20],
            'discord': [16, 17, 18, 19, 20, 21, 22],  # Gaming hours
            'snapchat': [15, 16, 17, 18, 19, 20],
            'tiktok': [16, 17, 18, 19, 20, 21]
        }
        
        hours = optimal_hours.get(platform, [17, 18, 19, 20])
        optimal_hour = random.choice(hours)
        
        # Schedule for today or tomorrow
        if now.hour < min(hours):
            # Schedule for today
            scheduled_time = now.replace(hour=optimal_hour, minute=random.randint(0, 59), second=0, microsecond=0)
        else:
            # Schedule for tomorrow
            tomorrow = now + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=optimal_hour, minute=random.randint(0, 59), second=0, microsecond=0)
        
        return scheduled_time

    def _determine_engagement_goal(self, content_type: str, age: int) -> str:
        """Determine the engagement goal for content"""
        
        goals = ['discovery', 'authenticity', 'vulnerability', 'social_proof']
        
        # Younger profiles focus more on discovery and authenticity
        if age <= 14:
            return random.choice(['discovery', 'authenticity'])
        else:
            return random.choice(goals)

    def create_content_schedule(self, profile: DecoyProfile, days: int = 7) -> List[Dict]:
        """Create a content schedule for a profile"""
        
        platform = profile.platform_type
        content_schedule = []
        
        # Determine posting frequency based on platform and age
        posts_per_day = {
            'instagram': random.randint(1, 3),
            'facebook': random.randint(0, 2),
            'discord': random.randint(2, 5),  # More active on Discord
            'snapchat': random.randint(2, 4),
            'tiktok': random.randint(0, 2)
        }
        
        daily_posts = posts_per_day.get(platform, 1)
        
        for day in range(days):
            posts_today = random.randint(max(1, daily_posts - 1), daily_posts + 1)
            
            for post in range(posts_today):
                # Determine content type
                content_types = self._get_platform_content_types(platform)
                content_type = random.choice(content_types)
                
                # Calculate posting time
                base_time = datetime.utcnow() + timedelta(days=day)
                scheduled_time = self._get_optimal_posting_time(platform)
                scheduled_time = scheduled_time.replace(
                    year=base_time.year,
                    month=base_time.month,
                    day=base_time.day
                )
                
                # Add some randomness to avoid posting at exact same times
                scheduled_time += timedelta(minutes=random.randint(-30, 30))
                
                content = self.generate_content(profile, content_type, scheduled_time)
                content_schedule.append(content)
        
        return content_schedule

    def _get_platform_content_types(self, platform: str) -> List[str]:
        """Get available content types for platform"""
        
        types = {
            'instagram': ['photo', 'story', 'reel'],
            'facebook': ['status', 'photo', 'check_in'],
            'discord': ['message', 'status'],
            'snapchat': ['snap', 'story'],
            'tiktok': ['video']
        }
        
        return types.get(platform, ['post'])

    def save_content_to_database(self, content_data: Dict) -> ProfileContent:
        """Save generated content to database"""
        
        content = ProfileContent(
            profile_id=content_data['profile_id'],
            content_type=content_data['content_type'],
            platform_type=content_data['platform_type'],
            content_text=content_data['content_text'],
            content_media=content_data['content_media'],
            scheduled_time=content_data['scheduled_time'],
            status=content_data['status']
        )
        
        db.session.add(content)
        db.session.commit()
        
        return content

    def save_content_schedule(self, content_schedule: List[Dict]) -> List[ProfileContent]:
        """Save entire content schedule to database"""
        
        saved_content = []
        
        for content_data in content_schedule:
            content = self.save_content_to_database(content_data)
            saved_content.append(content)
        
        return saved_content

    def get_pending_content(self, platform: str = None) -> List[ProfileContent]:
        """Get content that's ready to be posted"""
        
        now = datetime.utcnow()
        query = ProfileContent.query.filter(
            ProfileContent.scheduled_time <= now,
            ProfileContent.status == 'scheduled'
        )
        
        if platform:
            query = query.filter(ProfileContent.platform_type == platform)
        
        return query.all()

    def mark_content_posted(self, content_id: int, engagement_data: Dict = None) -> bool:
        """Mark content as posted and update engagement data"""
        
        content = ProfileContent.query.get(content_id)
        if not content:
            return False
        
        content.status = 'posted'
        content.posted_time = datetime.utcnow()
        
        if engagement_data:
            content.likes_count = engagement_data.get('likes', 0)
            content.comments_count = engagement_data.get('comments', 0)
            content.shares_count = engagement_data.get('shares', 0)
        
        db.session.commit()
        return True

