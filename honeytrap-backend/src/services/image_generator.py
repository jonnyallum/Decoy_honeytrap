import os
import json
import random
from typing import Dict, List, Optional
from datetime import datetime

class ImageGenerator:
    """Service for generating AI images for decoy profiles"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'generated_images')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Image generation settings
        self.image_settings = {
            'profile': {
                'aspect_ratio': 'square',
                'style': 'portrait photo',
                'quality': 'high quality, realistic'
            },
            'cover': {
                'aspect_ratio': 'landscape',
                'style': 'banner style',
                'quality': 'high quality, aesthetic'
            },
            'content': {
                'aspect_ratio': 'square',
                'style': 'casual photo',
                'quality': 'high quality, natural'
            }
        }
        
        # Safety guidelines for image generation
        self.safety_guidelines = [
            'safe for work',
            'appropriate for teenagers',
            'no inappropriate content',
            'family friendly',
            'professional quality'
        ]

    def generate_profile_image(self, profile_data: Dict, image_type: str = 'profile') -> Dict:
        """Generate a single profile image"""
        
        try:
            # Create image prompt
            prompt = self._create_detailed_prompt(profile_data, image_type)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{profile_data.get('username', 'profile')}_{image_type}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # For now, we'll create a placeholder implementation
            # In a real deployment, this would call the actual image generation API
            image_result = self._generate_image_placeholder(prompt, filepath)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'prompt': prompt,
                'url': f'/static/generated_images/{filename}',
                'metadata': {
                    'profile_id': profile_data.get('id'),
                    'image_type': image_type,
                    'generated_at': datetime.now().isoformat(),
                    'prompt_used': prompt
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt if 'prompt' in locals() else None
            }

    def generate_profile_image_set(self, profile_data: Dict) -> Dict:
        """Generate a complete set of images for a profile"""
        
        results = {
            'profile_image': None,
            'cover_image': None,
            'content_images': [],
            'success_count': 0,
            'total_count': 0,
            'errors': []
        }
        
        # Generate profile image
        results['total_count'] += 1
        profile_result = self.generate_profile_image(profile_data, 'profile')
        if profile_result['success']:
            results['profile_image'] = profile_result
            results['success_count'] += 1
        else:
            results['errors'].append(f"Profile image: {profile_result['error']}")
        
        # Generate cover image
        results['total_count'] += 1
        cover_result = self.generate_profile_image(profile_data, 'cover')
        if cover_result['success']:
            results['cover_image'] = cover_result
            results['success_count'] += 1
        else:
            results['errors'].append(f"Cover image: {cover_result['error']}")
        
        # Generate content images (3-5 images)
        interests = profile_data.get('interests', [])
        num_content_images = min(len(interests), 5)
        
        for i in range(num_content_images):
            results['total_count'] += 1
            interest = interests[i] if i < len(interests) else 'general'
            
            # Create context-specific profile data
            content_profile_data = profile_data.copy()
            content_profile_data['content_context'] = interest
            
            content_result = self.generate_profile_image(content_profile_data, 'content')
            if content_result['success']:
                content_result['context'] = interest
                results['content_images'].append(content_result)
                results['success_count'] += 1
            else:
                results['errors'].append(f"Content image ({interest}): {content_result['error']}")
        
        results['success_rate'] = (results['success_count'] / results['total_count']) * 100 if results['total_count'] > 0 else 0
        
        return results

    def _create_detailed_prompt(self, profile_data: Dict, image_type: str) -> str:
        """Create detailed prompt for AI image generation"""
        
        age = profile_data.get('age', 14)
        gender = profile_data.get('gender', 'female')
        interests = profile_data.get('interests', [])
        platform = profile_data.get('platform_type', 'general')
        
        # Base descriptors
        base_descriptors = {
            'female': f"young {age}-year-old teenage girl, friendly and approachable, natural smile, casual modern clothing",
            'male': f"young {age}-year-old teenage boy, friendly expression, casual demeanor, modern casual outfit"
        }
        
        base_desc = base_descriptors.get(gender, base_descriptors['female'])
        
        # Image type specific prompts
        if image_type == 'profile':
            prompt = f"{base_desc}, selfie style portrait photo, good natural lighting, bedroom or home setting"
            
        elif image_type == 'cover':
            # Create cover based on interests
            main_interest = interests[0] if interests else 'general'
            cover_themes = {
                'gaming': 'gaming setup with colorful LED lights, computer desk, gaming peripherals',
                'art': 'art supplies, drawings on wall, creative workspace, colorful art materials',
                'music': 'musical instruments, headphones, music notes, recording setup',
                'photography': 'camera equipment, photos on wall, artistic composition',
                'sports': 'sports equipment, trophies, athletic gear',
                'reading': 'books, cozy reading nook, bookshelf, warm lighting',
                'general': 'teenage bedroom, colorful decor, posters, modern aesthetic'
            }
            
            theme = cover_themes.get(main_interest, cover_themes['general'])
            prompt = f"teenage {gender} cover photo background, {theme}, aesthetic, bright colors, social media banner style"
            
        elif image_type == 'content':
            # Create content based on context
            context = profile_data.get('content_context', 'general')
            content_themes = {
                'gaming': f"{base_desc} playing video games, gaming setup visible, casual gaming session",
                'art': f"{base_desc} drawing or creating art, art supplies visible, creative activity",
                'music': f"{base_desc} with headphones or musical instrument, music-related activity",
                'school': f"{base_desc} studying or with school materials, books visible, academic setting",
                'friends': f"{base_desc} in social setting, friendly atmosphere, group activity implied",
                'photography': f"{base_desc} taking photos or with camera, photography hobby",
                'sports': f"{base_desc} in athletic wear or with sports equipment, active lifestyle",
                'reading': f"{base_desc} reading a book, cozy setting, intellectual activity",
                'general': f"{base_desc} casual daily activity, natural setting, authentic moment"
            }
            
            prompt = content_themes.get(context, content_themes['general'])
        
        else:
            prompt = f"{base_desc}, casual photo, natural lighting"
        
        # Add platform-specific styling
        platform_styles = {
            'instagram': 'Instagram style, aesthetic, well-lit, trendy',
            'discord': 'casual gaming style, relaxed atmosphere',
            'facebook': 'natural social media photo, friendly',
            'snapchat': 'casual selfie style, fun and spontaneous',
            'tiktok': 'trendy, modern, Gen Z aesthetic'
        }
        
        platform_style = platform_styles.get(platform, 'natural social media style')
        
        # Combine all elements
        full_prompt = f"{prompt}, {platform_style}, {', '.join(self.safety_guidelines)}, high quality, realistic, professional photography"
        
        return full_prompt

    def _generate_image_placeholder(self, prompt: str, filepath: str) -> Dict:
        """Placeholder for actual image generation - creates a text file with the prompt"""
        
        try:
            # For now, create a text file with the prompt
            # In production, this would call the actual image generation API
            prompt_file = filepath.replace('.png', '_prompt.txt')
            
            with open(prompt_file, 'w') as f:
                f.write(f"Image Generation Prompt:\n\n{prompt}\n\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n")
                f.write("Note: This is a placeholder. In production, this would generate an actual image.\n")
            
            return {
                'success': True,
                'placeholder_file': prompt_file,
                'note': 'Placeholder implementation - prompt saved to file'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_image_generation_stats(self) -> Dict:
        """Get statistics about image generation"""
        
        try:
            # Count generated files
            files = os.listdir(self.output_dir)
            image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg'))]
            prompt_files = [f for f in files if f.endswith('_prompt.txt')]
            
            # Analyze by type
            profile_images = [f for f in image_files if '_profile_' in f]
            cover_images = [f for f in image_files if '_cover_' in f]
            content_images = [f for f in image_files if '_content_' in f]
            
            return {
                'total_images': len(image_files),
                'total_prompts': len(prompt_files),
                'breakdown': {
                    'profile_images': len(profile_images),
                    'cover_images': len(cover_images),
                    'content_images': len(content_images)
                },
                'output_directory': self.output_dir,
                'recent_files': sorted(files, key=lambda x: os.path.getctime(os.path.join(self.output_dir, x)), reverse=True)[:10]
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_images': 0,
                'total_prompts': 0
            }

    def cleanup_old_images(self, days_old: int = 30) -> Dict:
        """Clean up old generated images"""
        
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            files = os.listdir(self.output_dir)
            deleted_files = []
            
            for file in files:
                file_path = os.path.join(self.output_dir, file)
                if os.path.getctime(file_path) < cutoff_time:
                    os.remove(file_path)
                    deleted_files.append(file)
            
            return {
                'success': True,
                'deleted_count': len(deleted_files),
                'deleted_files': deleted_files,
                'cutoff_days': days_old
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }

    def validate_image_prompt(self, prompt: str) -> Dict:
        """Validate image prompt for safety and appropriateness"""
        
        # Safety keywords to check for
        unsafe_keywords = [
            'inappropriate', 'explicit', 'adult', 'sexual', 'nude', 'naked',
            'provocative', 'suggestive', 'revealing', 'intimate'
        ]
        
        # Required safety elements
        required_safety = ['safe for work', 'appropriate', 'family friendly']
        
        prompt_lower = prompt.lower()
        
        # Check for unsafe content
        unsafe_found = [keyword for keyword in unsafe_keywords if keyword in prompt_lower]
        
        # Check for safety elements
        safety_found = [safety for safety in required_safety if any(word in prompt_lower for word in safety.split())]
        
        is_safe = len(unsafe_found) == 0 and len(safety_found) > 0
        
        return {
            'is_safe': is_safe,
            'unsafe_keywords_found': unsafe_found,
            'safety_elements_found': safety_found,
            'recommendations': self._get_safety_recommendations(unsafe_found, safety_found)
        }

    def _get_safety_recommendations(self, unsafe_found: List[str], safety_found: List[str]) -> List[str]:
        """Get recommendations for improving prompt safety"""
        
        recommendations = []
        
        if unsafe_found:
            recommendations.append(f"Remove unsafe keywords: {', '.join(unsafe_found)}")
        
        if not safety_found:
            recommendations.append("Add safety guidelines: 'safe for work', 'appropriate for teenagers', 'family friendly'")
        
        if len(safety_found) < 2:
            recommendations.append("Add more explicit safety guidelines to ensure appropriate content")
        
        recommendations.append("Always include age-appropriate descriptors")
        recommendations.append("Specify professional quality and realistic style")
        
        return recommendations

    def get_prompt_templates(self) -> Dict:
        """Get template prompts for different scenarios"""
        
        return {
            'profile_templates': {
                'female_teen': "young teenage girl, 13-16 years old, friendly smile, casual modern clothing, selfie style portrait, natural lighting, bedroom setting, safe for work, appropriate for teenagers, high quality, realistic",
                'male_teen': "young teenage boy, 13-16 years old, friendly expression, casual modern outfit, selfie style portrait, natural lighting, bedroom setting, safe for work, appropriate for teenagers, high quality, realistic"
            },
            'cover_templates': {
                'gaming': "teenage bedroom background, gaming setup with colorful LED lights, computer desk, gaming peripherals, aesthetic, bright colors, social media banner style, safe for work, high quality",
                'art': "teenage bedroom background, art supplies, drawings on wall, creative workspace, colorful art materials, aesthetic, bright colors, social media banner style, safe for work, high quality",
                'music': "teenage bedroom background, musical instruments, headphones, music notes, recording setup, aesthetic, bright colors, social media banner style, safe for work, high quality"
            },
            'content_templates': {
                'school': "young teenager studying with books, school materials visible, academic setting, natural lighting, casual clothing, safe for work, appropriate for teenagers, high quality",
                'hobby': "young teenager engaged in hobby activity, casual setting, natural lighting, authentic moment, safe for work, appropriate for teenagers, high quality",
                'social': "young teenager in friendly social setting, casual atmosphere, natural lighting, safe for work, appropriate for teenagers, high quality"
            }
        }

    def batch_generate_images(self, profiles_data: List[Dict]) -> Dict:
        """Generate images for multiple profiles"""
        
        results = {
            'total_profiles': len(profiles_data),
            'successful_profiles': 0,
            'failed_profiles': 0,
            'total_images_generated': 0,
            'profile_results': [],
            'overall_errors': []
        }
        
        for profile_data in profiles_data:
            try:
                profile_result = self.generate_profile_image_set(profile_data)
                
                if profile_result['success_count'] > 0:
                    results['successful_profiles'] += 1
                else:
                    results['failed_profiles'] += 1
                
                results['total_images_generated'] += profile_result['success_count']
                results['profile_results'].append({
                    'profile_id': profile_data.get('id'),
                    'username': profile_data.get('username'),
                    'result': profile_result
                })
                
            except Exception as e:
                results['failed_profiles'] += 1
                results['overall_errors'].append(f"Profile {profile_data.get('id', 'unknown')}: {str(e)}")
        
        results['success_rate'] = (results['successful_profiles'] / results['total_profiles']) * 100 if results['total_profiles'] > 0 else 0
        
        return results

