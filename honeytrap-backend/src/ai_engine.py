import json
import random
import re
from typing import List, Dict, Any
from datetime import datetime

class AIPersonaEngine:
    """
    AI engine for generating persona-based chat responses
    This is a sophisticated rule-based system that simulates AI responses
    In production, this would integrate with OpenAI GPT or similar models
    """
    
    def __init__(self):
        self.threat_keywords = {
            'high_risk': [
                'meet', 'meet up', 'come over', 'my place', 'your place',
                'secret', 'don\'t tell', 'between us', 'our secret',
                'send photo', 'send pic', 'picture', 'selfie', 'video call',
                'address', 'where do you live', 'location',
                'alone', 'when parents', 'home alone',
                'older', 'mature', 'grown up', 'adult things'
            ],
            'medium_risk': [
                'private', 'dm me', 'text me', 'call me',
                'cute', 'pretty', 'beautiful', 'hot',
                'boyfriend', 'girlfriend', 'relationship',
                'age', 'how old', 'young', 'little'
            ],
            'escalation_phrases': [
                'what are you wearing', 'describe yourself',
                'are you alone', 'parents home',
                'special friend', 'our little secret',
                'trust me', 'i won\'t tell'
            ]
        }
        
        self.response_templates = {
            'deflection': [
                "haha idk about that",
                "my parents are pretty strict about that stuff",
                "maybe we should talk about something else?",
                "that makes me a bit uncomfortable",
                "i don't really do that kind of thing"
            ],
            'curiosity': [
                "what do you mean?",
                "i'm not sure i understand",
                "can you explain that?",
                "that's interesting, tell me more"
            ],
            'engagement': [
                "that's cool!",
                "awesome!",
                "i love that too!",
                "tell me more about that!"
            ]
        }

    def generate_response(self, persona: Dict[str, Any], message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        Generate a contextual response based on persona and conversation
        """
        # Analyze the incoming message
        threat_level = self.analyze_threat_level(message)
        message_type = self.classify_message_type(message)
        
        # Get persona characteristics
        personality_traits = persona.get('personality_traits', {})
        language_style = persona.get('language_style', {})
        response_patterns = persona.get('response_patterns', {})
        age = persona.get('age', 14)
        
        # Generate appropriate response
        if threat_level >= 2:
            response = self.generate_defensive_response(persona, message, conversation_history)
        elif threat_level == 1:
            response = self.generate_cautious_response(persona, message, conversation_history)
        else:
            response = self.generate_normal_response(persona, message, message_type, conversation_history)
        
        # Apply persona-specific language styling
        styled_response = self.apply_persona_styling(response, language_style, age)
        
        return {
            'response': styled_response,
            'threat_level': threat_level,
            'message_type': message_type,
            'confidence': 0.85  # Simulated confidence score
        }

    def analyze_threat_level(self, message: str) -> int:
        """
        Analyze message for threat indicators
        Returns: 0 (safe), 1 (suspicious), 2 (high risk)
        """
        message_lower = message.lower()
        
        # Check for high-risk keywords
        high_risk_count = sum(1 for keyword in self.threat_keywords['high_risk'] 
                             if keyword in message_lower)
        
        # Check for medium-risk keywords
        medium_risk_count = sum(1 for keyword in self.threat_keywords['medium_risk'] 
                               if keyword in message_lower)
        
        # Check for escalation phrases
        escalation_count = sum(1 for phrase in self.threat_keywords['escalation_phrases'] 
                              if phrase in message_lower)
        
        # Calculate threat level
        if high_risk_count >= 2 or escalation_count >= 1:
            return 2  # High risk
        elif high_risk_count >= 1 or medium_risk_count >= 2:
            return 1  # Suspicious
        else:
            return 0  # Normal

    def classify_message_type(self, message: str) -> str:
        """
        Classify the type of message for appropriate response
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'what\'s up']):
            return 'greeting'
        elif '?' in message:
            return 'question'
        elif any(word in message_lower for word in ['like', 'love', 'enjoy', 'favorite']):
            return 'interest'
        elif any(word in message_lower for word in ['lol', 'haha', 'funny', 'joke']):
            return 'humor'
        else:
            return 'casual'

    def generate_defensive_response(self, persona: Dict, message: str, history: List) -> str:
        """
        Generate defensive responses for high-risk messages
        """
        age = persona.get('age', 14)
        
        if age <= 13:
            responses = [
                "um that's weird, i don't want to talk about that",
                "my mom says i shouldn't talk to people about stuff like that",
                "that makes me uncomfortable, can we talk about something else?",
                "i don't think i should be talking about this",
                "my parents check my messages so maybe we shouldn't"
            ]
        else:
            responses = [
                "that's not really something i'm comfortable with",
                "i don't think we should be talking about that",
                "that's kind of inappropriate don't you think?",
                "i'm not really into that kind of conversation",
                "maybe we should stick to normal topics"
            ]
        
        return random.choice(responses)

    def generate_cautious_response(self, persona: Dict, message: str, history: List) -> str:
        """
        Generate cautious responses for suspicious messages
        """
        responses = [
            "i'm not sure about that",
            "maybe... but i'd have to think about it",
            "that's interesting but idk",
            "i don't really know much about that",
            "hmm not sure what you mean"
        ]
        
        return random.choice(responses)

    def generate_normal_response(self, persona: Dict, message: str, message_type: str, history: List) -> str:
        """
        Generate normal conversational responses
        """
        response_patterns = persona.get('response_patterns', {})
        age = persona.get('age', 14)
        interests = persona.get('personality_traits', {}).get('interests', [])
        
        # Use persona-specific response patterns if available
        if message_type in response_patterns:
            base_responses = response_patterns[message_type]
        else:
            base_responses = self.response_templates.get(message_type, self.response_templates['engagement'])
        
        # Add interest-based responses
        if message_type == 'interest' and interests:
            interest_responses = [
                f"oh cool! i love {random.choice(interests)} too!",
                f"that's awesome! have you tried {random.choice(interests)}?",
                f"nice! i'm really into {random.choice(interests)} myself"
            ]
            base_responses.extend(interest_responses)
        
        return random.choice(base_responses)

    def apply_persona_styling(self, response: str, language_style: Dict, age: int) -> str:
        """
        Apply persona-specific language styling to responses
        """
        styled_response = response
        
        # Get language characteristics
        emoji_usage = language_style.get('emoji_usage', 'moderate')
        slang = language_style.get('slang', [])
        common_phrases = language_style.get('common_phrases', [])
        
        # Add age-appropriate modifications
        if age <= 13:
            # Younger personas use more basic language
            styled_response = styled_response.lower()
            
            # Add emojis based on usage preference
            if emoji_usage == 'very frequent':
                emojis = ['😊', '😄', '🤔', '😅', '👍', '❤️', '🎮', '🎨']
                if random.random() < 0.7:  # 70% chance to add emoji
                    styled_response += ' ' + random.choice(emojis)
            elif emoji_usage == 'frequent':
                emojis = ['😊', '😄', '🤔', '👍']
                if random.random() < 0.4:  # 40% chance to add emoji
                    styled_response += ' ' + random.choice(emojis)
        
        # Add slang occasionally
        if slang and random.random() < 0.3:  # 30% chance to add slang
            slang_word = random.choice(slang)
            if slang_word not in styled_response:
                styled_response += f' {slang_word}'
        
        # Occasionally add common phrases
        if common_phrases and random.random() < 0.2:  # 20% chance
            phrase = random.choice(common_phrases)
            if phrase not in styled_response:
                styled_response = f'{phrase} {styled_response}'
        
        return styled_response

    def get_conversation_context(self, history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze conversation history for context
        """
        if not history:
            return {'length': 0, 'escalation_trend': 0, 'topics': []}
        
        # Analyze escalation trend
        recent_messages = history[-5:]  # Last 5 messages
        threat_levels = [msg.get('threat_level', 0) for msg in recent_messages]
        escalation_trend = sum(threat_levels) / len(threat_levels) if threat_levels else 0
        
        # Extract topics (simplified)
        all_text = ' '.join([msg.get('message_content', '') for msg in history])
        topics = self.extract_topics(all_text)
        
        return {
            'length': len(history),
            'escalation_trend': escalation_trend,
            'topics': topics,
            'recent_threat_levels': threat_levels
        }

    def extract_topics(self, text: str) -> List[str]:
        """
        Extract conversation topics (simplified implementation)
        """
        topic_keywords = {
            'gaming': ['game', 'gaming', 'play', 'xbox', 'playstation', 'pc'],
            'school': ['school', 'class', 'teacher', 'homework', 'test'],
            'music': ['music', 'song', 'band', 'artist', 'listen'],
            'sports': ['sport', 'football', 'basketball', 'soccer', 'team'],
            'social_media': ['instagram', 'tiktok', 'snapchat', 'youtube', 'post']
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics

