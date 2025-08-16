"""
LinkedIn Post Generator
"""

import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from .config import config

class PostGenerator:
    """Generate LinkedIn posts from processed content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.post_config = config.get_post_generation()
        self.templates = self.post_config.get('templates', [])
        self.hashtags_config = self.post_config.get('hashtags', {})
    
    def generate_posts(self, processed_articles: List[Dict[str, Any]], max_posts: int = 5) -> List[Dict[str, Any]]:
        """Generate LinkedIn posts from processed articles."""
        posts = []
        
        for article in processed_articles[:max_posts]:
            try:
                post = self.generate_single_post(article)
                if post:
                    posts.append(post)
            except Exception as e:
                self.logger.error(f"Error generating post for article '{article.get('title', 'Unknown')}': {e}")
                continue
        
        self.logger.info(f"Generated {len(posts)} LinkedIn posts")
        return posts
    
    def generate_single_post(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a single LinkedIn post from processed article."""
        try:
            # Select a random template
            template = self._select_template()
            
            # Format insights
            formatted_insights = self._format_insights(article.get('key_insights', []))
            
            # Format hashtags
            formatted_hashtags = self._format_hashtags(article.get('hashtags', []))
            
            # Generate post content
            post_content = template.format(
                title=article.get('title', ''),
                summary=article.get('summary', ''),
                insights=formatted_insights,
                link=article.get('link', ''),
                hashtags=formatted_hashtags
            )
            
            # Clean and validate post
            post_content = self._clean_post_content(post_content)
            
            if not self._validate_post(post_content):
                self.logger.warning(f"Generated post for '{article.get('title', '')}' failed validation")
                return None
            
            # Create post object
            post = {
                'content': post_content,
                'article': article,
                'template_used': template,
                'generated_at': datetime.now().isoformat(),
                'post_length': len(post_content),
                'hashtag_count': len(article.get('hashtags', [])),
                'engagement_score': self._calculate_engagement_score(post_content, article)
            }
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error generating post: {e}")
            return None
    
    def _select_template(self) -> str:
        """Select a random template from available templates."""
        if not self.templates:
            # Fallback template
            return "🎯 {title}\n\n{summary}\n\n💡 Key insights:\n{insights}\n\n🔗 Read more: {link}\n\n{hashtags}"
        
        return random.choice(self.templates)
    
    def _format_insights(self, insights: List[str]) -> str:
        """Format insights for post display."""
        if not insights:
            return "• No specific insights available"
        
        formatted_insights = []
        for i, insight in enumerate(insights[:3], 1):  # Limit to 3 insights
            # Clean and truncate insight
            clean_insight = insight.strip()
            if len(clean_insight) > 100:
                clean_insight = clean_insight[:97] + "..."
            
            formatted_insights.append(f"• {clean_insight}")
        
        return "\n".join(formatted_insights)
    
    def _format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for post display."""
        if not hashtags:
            return ""
        
        # Ensure hashtags start with #
        formatted_hashtags = []
        for hashtag in hashtags:
            if not hashtag.startswith('#'):
                hashtag = f"#{hashtag}"
            formatted_hashtags.append(hashtag)
        
        return " ".join(formatted_hashtags)
    
    def _clean_post_content(self, content: str) -> str:
        """Clean and format post content."""
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Fix common formatting issues
        content = re.sub(r'\s+([.,!?;:])', r'\1', content)
        content = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', content)
        
        # Ensure proper line breaks
        content = content.strip()
        
        return content
    
    def _validate_post(self, content: str) -> bool:
        """Validate generated post content."""
        # Check length
        max_length = config.get_content_processing().get('max_post_length', 1300)
        if len(content) > max_length:
            self.logger.warning(f"Post too long: {len(content)} characters")
            return False
        
        min_length = config.get_content_processing().get('min_post_length', 100)
        if len(content) < min_length:
            self.logger.warning(f"Post too short: {len(content)} characters")
            return False
        
        # Check for required elements
        if not content.strip():
            return False
        
        # Check for placeholder values
        placeholders = ['{title}', '{summary}', '{insights}', '{link}', '{hashtags}']
        for placeholder in placeholders:
            if placeholder in content:
                self.logger.warning(f"Post contains unformatted placeholder: {placeholder}")
                return False
        
        return True
    
    def _calculate_engagement_score(self, content: str, article: Dict[str, Any]) -> float:
        """Calculate potential engagement score for the post."""
        score = 0.0
        
        # Content length score (optimal length around 1000-1300 characters)
        length = len(content)
        if 800 <= length <= 1300:
            score += 0.3
        elif 500 <= length <= 1500:
            score += 0.2
        
        # Hashtag score
        hashtag_count = len(article.get('hashtags', []))
        if 3 <= hashtag_count <= 5:
            score += 0.2
        elif 1 <= hashtag_count <= 7:
            score += 0.1
        
        # Emoji score (presence of emojis)
        emoji_count = len(re.findall(r'[🎯📊🤖💡🚀⚡🔗📖🔍]', content))
        if 1 <= emoji_count <= 5:
            score += 0.1
        
        # Question score (questions increase engagement)
        if '?' in content:
            score += 0.1
        
        # Call-to-action score
        cta_words = ['read', 'learn', 'discover', 'explore', 'check']
        if any(word in content.lower() for word in cta_words):
            score += 0.1
        
        # Original article quality score
        original_score = article.get('content_score', 0)
        score += 0.2 * original_score
        
        return min(score, 1.0)
    
    def generate_custom_post(self, title: str, summary: str, insights: List[str], 
                           link: str, hashtags: List[str], template: str = None) -> Optional[Dict[str, Any]]:
        """Generate a custom post with specific content."""
        try:
            # Use provided template or select random one
            if template:
                selected_template = template
            else:
                selected_template = self._select_template()
            
            # Format content
            formatted_insights = self._format_insights(insights)
            formatted_hashtags = self._format_hashtags(hashtags)
            
            # Generate post
            post_content = selected_template.format(
                title=title,
                summary=summary,
                insights=formatted_insights,
                link=link,
                hashtags=formatted_hashtags
            )
            
            # Clean and validate
            post_content = self._clean_post_content(post_content)
            
            if not self._validate_post(post_content):
                return None
            
            return {
                'content': post_content,
                'template_used': selected_template,
                'generated_at': datetime.now().isoformat(),
                'post_length': len(post_content),
                'hashtag_count': len(hashtags),
                'custom': True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating custom post: {e}")
            return None
    
    def save_posts(self, posts: List[Dict[str, Any]], filename: str = None) -> str:
        """Save generated posts to JSON file."""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/generated_posts_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Generated posts saved to: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving posts: {e}")
            raise
    
    def preview_post(self, post: Dict[str, Any]) -> str:
        """Generate a preview of the post for review."""
        preview = f"""
=== LINKEDIN POST PREVIEW ===
Length: {post.get('post_length', 0)} characters
Hashtags: {post.get('hashtag_count', 0)}
Engagement Score: {post.get('engagement_score', 0):.2f}
Generated: {post.get('generated_at', 'Unknown')}

{post.get('content', 'No content')}

=== END PREVIEW ===
"""
        return preview
