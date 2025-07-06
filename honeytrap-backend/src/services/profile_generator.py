import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ProfileGenerator:
    """Service for generating realistic decoy profiles"""
    
    def __init__(self):
        self.names = {
            'female': [
                'Emma', 'Olivia', 'Ava', 'Isabella', 'Sophia', 'Charlotte', 'Mia', 'Amelia',
                'Harper', 'Evelyn', 'Abigail', 'Emily', 'Elizabeth', 'Mila', 'Ella', 'Avery',
                'Sofia', 'Camila', 'Aria', 'Scarlett', 'Victoria', 'Madison', 'Luna', 'Grace'
            ],
            'male': [
                'Liam', 'Noah', 'Oliver', 'Elijah', 'William', 'James', 'Benjamin', 'Lucas',
                'Henry', 'Alexander', 'Mason', 'Michael', 'Ethan', 'Daniel', 'Jacob', 'Logan',
                'Jackson', 'Levi', 'Sebastian', 'Mateo', 'Jack', 'Owen', 'Theodore', 'Aiden'
            ]
        }
        
        self.surnames = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker'
        ]
        
        self.uk_locations = [
            'Southampton', 'Portsmouth', 'Winchester', 'Basingstoke', 'Andover', 'Eastleigh',
            'Fareham', 'Gosport', 'Havant', 'Alton', 'Petersfield', 'Romsey', 'New Forest',
            'Isle of Wight', 'Farnborough', 'Fleet', 'Aldershot', 'Reading', 'Brighton',
            'London', 'Birmingham', 'Manchester', 'Liverpool', 'Leeds', 'Sheffield'
        ]
        
        self.interests_by_age = {
            '13-14': {
                'common': ['gaming', 'music', 'art', 'friends', 'school', 'social media', 'movies', 'books'],
                'gaming': ['Minecraft', 'Roblox', 'Among Us', 'Fortnite', 'Animal Crossing'],
                'music': ['pop music', 'K-pop', 'Taylor Swift', 'Billie Eilish', 'Ariana Grande'],
                'art': ['drawing', 'digital art', 'painting', 'crafts', 'photography'],
                'social': ['making friends', 'chatting', 'texting', 'video calls', 'group chats']
            },
            '15-16': {
                'common': ['music', 'gaming', 'sports', 'art', 'friends', 'school', 'fashion', 'technology'],
                'gaming': ['Valorant', 'League of Legends', 'Minecraft', 'Genshin Impact', 'Call of Duty'],
                'music': ['indie music', 'rock', 'hip hop', 'electronic', 'alternative'],
                'sports': ['football', 'basketball', 'swimming', 'tennis', 'running'],
                'technology': ['coding', 'web design', 'apps', 'gadgets', 'computers']
            }
        }
        
        self.vulnerability_indicators = [
            'feeling lonely lately',
            'parents are always busy',
            'having trouble at school',
            'looking for new friends',
            'feeling misunderstood',
            'want someone to talk to',
            'family problems',
            'feeling left out',
            'need advice',
            'going through tough times'
        ]
        
        self.platform_usernames = {
            'discord': ['_gamer', '_art', '_music', 'xox', '123', '_uwu', '_vibes', '_aesthetic'],
            'instagram': ['_aesthetic', '_vibes', '_art', '_photography', '_style', '.jpg', '_pics'],
            'facebook': [],  # Usually real names
            'snapchat': ['_snaps', '_pics', '123', 'xox', '_vibes'],
            'tiktok': ['_official', '_vibes', '_aesthetic', '_content', '123', 'xox']
        }

    def generate_profile(self, platform_type: str, age_range: str = '13-16', 
                        gender: str = None, location: str = None) -> Dict:
        """Generate a complete decoy profile"""
        
        # Determine gender
        if not gender:
            gender = random.choice(['female', 'male'])
        
        # Generate basic info
        first_name = random.choice(self.names[gender])
        last_name = random.choice(self.surnames)
        age = random.randint(13, 16) if age_range == '13-16' else random.randint(13, 14)
        
        # Generate location
        if not location:
            location = random.choice(self.uk_locations)
        
        # Generate username
        username = self._generate_username(first_name, platform_type)
        
        # Generate interests
        interests = self._generate_interests(age)
        
        # Generate bio
        bio = self._generate_bio(first_name, age, interests, platform_type)
        
        # Generate backstory
        backstory = self._generate_backstory(first_name, age, location, interests)
        
        profile = {
            'name': f"{first_name} {last_name}",
            'username': username,
            'age': age,
            'gender': gender,
            'location': location,
            'platform_type': platform_type,
            'bio': bio,
            'interests': interests,
            'backstory': backstory,
            'vulnerability_level': random.choice(['low', 'medium', 'high']),
            'profile_image_prompt': self._generate_image_prompt(gender, age),
            'content_suggestions': self._generate_content_suggestions(platform_type, interests, age)
        }
        
        return profile

    def _generate_username(self, first_name: str, platform_type: str) -> str:
        """Generate platform-appropriate username"""
        base_name = first_name.lower()
        
        if platform_type == 'facebook':
            # Facebook typically uses real names
            return base_name
        
        suffixes = self.platform_usernames.get(platform_type, ['123', 'xox'])
        suffix = random.choice(suffixes)
        
        # Add random numbers or suffix
        if random.choice([True, False]):
            return f"{base_name}{suffix}"
        else:
            return f"{base_name}{random.randint(10, 99)}"

    def _generate_interests(self, age: int) -> List[str]:
        """Generate age-appropriate interests"""
        age_group = '13-14' if age <= 14 else '15-16'
        interests_pool = self.interests_by_age[age_group]
        
        # Select 4-7 interests
        num_interests = random.randint(4, 7)
        selected_interests = []
        
        # Always include some common interests
        common = random.sample(interests_pool['common'], min(3, num_interests))
        selected_interests.extend(common)
        
        # Add specific interests from categories
        remaining = num_interests - len(selected_interests)
        for category in ['gaming', 'music', 'art']:
            if category in interests_pool and remaining > 0:
                if random.choice([True, False]):
                    specific = random.choice(interests_pool[category])
                    selected_interests.append(specific)
                    remaining -= 1
        
        return selected_interests

    def _generate_bio(self, name: str, age: int, interests: List[str], platform_type: str) -> str:
        """Generate platform-appropriate bio"""
        
        bio_templates = {
            'instagram': [
                f"{age} | {random.choice(self.uk_locations)} | {' | '.join(random.sample(interests, min(3, len(interests))))} ✨",
                f"just a {age}yo trying to figure life out 🌸 love {', '.join(random.sample(interests, min(2, len(interests))))}",
                f"{age} • {random.choice(['art student', 'music lover', 'gamer girl', 'creative soul'])} • dm me! 💕"
            ],
            'discord': [
                f"{name} | {age} | loves {', '.join(random.sample(interests, min(2, len(interests))))}",
                f"hey! i'm {age} and into {random.choice(interests)} - always looking for new friends!",
                f"{age}yo from {random.choice(['UK', 'England'])} | {random.choice(interests)} enthusiast"
            ],
            'facebook': [
                f"Student at {random.choice(['Local Secondary School', 'Community College', 'High School'])}",
                f"Lives in {random.choice(self.uk_locations)} • {age} years old",
                f"Loves {', '.join(random.sample(interests, min(3, len(interests))))} • Looking to connect with friends"
            ],
            'snapchat': [
                f"{age} | {random.choice(self.uk_locations)} | {random.choice(interests)} lover 👻",
                f"just vibing ✨ {age}yo | add me for daily snaps!",
                f"student life 📚 | {', '.join(random.sample(interests, min(2, len(interests))))} | {age}"
            ],
            'tiktok': [
                f"{age} | creating content about {random.choice(interests)} ✨",
                f"just a {age}yo sharing my life | {random.choice(interests)} enthusiast",
                f"{age} • {random.choice(self.uk_locations)} • follow for {random.choice(interests)} content!"
            ]
        }
        
        templates = bio_templates.get(platform_type, bio_templates['instagram'])
        return random.choice(templates)

    def _generate_backstory(self, name: str, age: int, location: str, interests: List[str]) -> str:
        """Generate detailed backstory for operational use"""
        
        school_year = "Year 9" if age <= 14 else "Year 10" if age <= 15 else "Year 11"
        
        family_situations = [
            "lives with both parents who work full-time",
            "lives with mum and stepdad",
            "lives with dad, parents divorced last year",
            "lives with mum, dad travels for work",
            "lives with grandparents during the week"
        ]
        
        school_situations = [
            f"attends local secondary school in {location}",
            f"goes to {random.choice(['St. Mary\'s', 'Oakwood', 'Riverside', 'Greenfield'])} Secondary School",
            f"student at community college in {location}"
        ]
        
        social_situations = [
            "has a small group of close friends",
            "recently moved schools and making new friends",
            "feels left out of main friend group sometimes",
            "popular on social media but shy in person",
            "prefers online friends to school friends"
        ]
        
        vulnerability_factors = [
            "parents are often busy with work",
            "feels pressure to fit in at school",
            "looking for someone who understands them",
            "wants to feel more grown up",
            "curious about relationships and dating"
        ]
        
        backstory = f"""
        {name} is a {age}-year-old {school_year} student who {random.choice(school_situations)}. 
        She {random.choice(family_situations)} and {random.choice(social_situations)}.
        
        Interests: Passionate about {', '.join(interests[:3])}, spends a lot of time online.
        
        Personality: {random.choice(['Friendly and outgoing', 'Shy but opens up online', 'Creative and artistic', 'Curious and eager to learn'])}.
        
        Current situation: {random.choice(vulnerability_factors)}. Often online in the evenings and weekends.
        
        Online behavior: Active on social media, enjoys chatting with new people, 
        sometimes shares personal information when feeling comfortable with someone.
        """
        
        return backstory.strip()

    def _generate_image_prompt(self, gender: str, age: int) -> str:
        """Generate prompt for AI image generation"""
        
        descriptors = {
            'female': ['young teenage girl', 'friendly smile', 'casual clothing', 'natural lighting'],
            'male': ['young teenage boy', 'friendly expression', 'casual outfit', 'natural lighting']
        }
        
        settings = ['bedroom', 'school', 'park', 'home', 'outdoors']
        styles = ['selfie style', 'portrait photo', 'casual photo', 'social media style']
        
        base_desc = random.choice(descriptors[gender])
        setting = random.choice(settings)
        style = random.choice(styles)
        
        prompt = f"{base_desc}, {age} years old, {style}, {setting}, high quality, realistic, safe for work"
        
        return prompt

    def _generate_content_suggestions(self, platform_type: str, interests: List[str], age: int) -> List[Dict]:
        """Generate content posting suggestions"""
        
        content_types = {
            'instagram': ['photo', 'story', 'reel'],
            'facebook': ['status', 'photo', 'check-in'],
            'discord': ['message', 'status'],
            'snapchat': ['snap', 'story'],
            'tiktok': ['video', 'comment']
        }
        
        content_ideas = []
        
        for i in range(5):  # Generate 5 content suggestions
            content_type = random.choice(content_types.get(platform_type, ['post']))
            interest = random.choice(interests)
            
            content_ideas.append({
                'type': content_type,
                'topic': interest,
                'text': self._generate_content_text(content_type, interest, platform_type, age),
                'timing': f"Day {i+1}",
                'engagement_goal': random.choice(['discovery', 'authenticity', 'vulnerability'])
            })
        
        return content_ideas

    def _generate_content_text(self, content_type: str, topic: str, platform_type: str, age: int) -> str:
        """Generate specific content text"""
        
        templates = {
            'photo': [
                f"just finished my {topic} project! pretty proud of it ✨",
                f"spending my evening with {topic} as usual 😊",
                f"can't get enough of {topic} lately!"
            ],
            'status': [
                f"anyone else obsessed with {topic}? just me? 😅",
                f"having such a good time with {topic} today",
                f"feeling really into {topic} lately, any recommendations?"
            ],
            'story': [
                f"currently: {topic} mode activated 🔥",
                f"today's vibe: all about {topic}",
                f"guess what I'm doing... {topic} again! 😂"
            ]
        }
        
        template_list = templates.get(content_type, templates['status'])
        return random.choice(template_list)

    def generate_batch_profiles(self, count: int, platform_types: List[str] = None) -> List[Dict]:
        """Generate multiple profiles for deployment"""
        
        if not platform_types:
            platform_types = ['discord', 'instagram', 'facebook', 'snapchat', 'tiktok']
        
        profiles = []
        
        for i in range(count):
            platform = random.choice(platform_types)
            profile = self.generate_profile(platform)
            profiles.append(profile)
        
        return profiles

