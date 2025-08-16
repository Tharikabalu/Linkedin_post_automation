"""
Content Processor for LinkedIn Post Automation
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import nltk
from textblob import TextBlob
from .config import config

class ContentProcessor:
    """Process and format newsletter content for LinkedIn posts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.content_config = config.get_content_processing()
        self._setup_nltk()
    
    def _setup_nltk(self):
        """Setup NLTK data for text processing."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
            except Exception as e:
                self.logger.warning(f"Could not download NLTK data: {e}")
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of articles for LinkedIn posting."""
        processed_articles = []
        
        for article in articles:
            try:
                processed = self.process_single_article(article)
                if processed:
                    processed_articles.append(processed)
            except Exception as e:
                self.logger.error(f"Error processing article '{article.get('title', 'Unknown')}': {e}")
                continue
        
        self.logger.info(f"Processed {len(processed_articles)} articles")
        return processed_articles
    
    def process_single_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single article for LinkedIn posting."""
        try:
            # Clean and format content
            cleaned_title = self._clean_text(article.get('title', ''))
            cleaned_summary = self._clean_text(article.get('summary', ''))
            cleaned_insights = [self._clean_text(insight) for insight in article.get('insights', [])]
            
            # Validate content length
            if not self._validate_content_length(cleaned_title, cleaned_summary):
                self.logger.warning(f"Article '{cleaned_title}' too short or too long")
                return None
            
            # Extract key insights
            key_insights = self._extract_key_insights(cleaned_summary, cleaned_insights)
            
            # Generate hashtags
            hashtags = self._generate_hashtags(cleaned_title, cleaned_summary)
            
            # Create processed article
            processed_article = {
                'original_article': article,
                'title': cleaned_title,
                'summary': cleaned_summary,
                'key_insights': key_insights,
                'hashtags': hashtags,
                'link': article.get('link', ''),
                'source': article.get('source', ''),
                'processed_at': datetime.now().isoformat(),
                'content_score': self._calculate_content_score(cleaned_title, cleaned_summary, key_insights)
            }
            
            return processed_article
            
        except Exception as e:
            self.logger.error(f"Error processing article: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()]', '', text)
        
        # Fix common formatting issues
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', text)
        
        # Capitalize first letter of sentences
        sentences = text.split('. ')
        sentences = [s.capitalize() if s else s for s in sentences]
        text = '. '.join(sentences)
        
        return text
    
    def _validate_content_length(self, title: str, summary: str) -> bool:
        """Validate that content meets length requirements."""
        min_length = self.content_config.get('min_post_length', 100)
        max_length = self.content_config.get('max_post_length', 1300)
        
        total_length = len(title) + len(summary)
        
        # Allow shorter content for testing and flexibility
        if total_length < 50:  # Very short content
            return False
        
        return total_length <= max_length
    
    def _extract_key_insights(self, summary: str, insights: List[str]) -> List[str]:
        """Extract key insights from summary and existing insights."""
        key_insights = []
        
        # Use existing insights if available
        if insights:
            key_insights.extend(insights[:3])  # Take first 3 insights
        
        # Extract additional insights from summary if needed
        if len(key_insights) < 3:
            summary_insights = self._extract_insights_from_text(summary)
            key_insights.extend(summary_insights[:3 - len(key_insights)])
        
        # Clean and format insights
        key_insights = [self._clean_text(insight) for insight in key_insights if insight]
        key_insights = [insight for insight in key_insights if len(insight) > 10 and len(insight) < 150]
        
        return key_insights[:3]  # Return max 3 insights
    
    def _extract_insights_from_text(self, text: str) -> List[str]:
        """Extract insights from text using NLP techniques."""
        insights = []
        
        try:
            # Use TextBlob for sentiment and key phrase extraction
            blob = TextBlob(text)
            
            # Extract noun phrases as potential insights
            noun_phrases = blob.noun_phrases
            for phrase in noun_phrases:
                if len(phrase) > 3 and len(phrase) < 50:
                    insights.append(f"Key focus: {phrase}")
            
            # Extract sentences with high information content
            sentences = blob.sentences
            for sentence in sentences:
                if len(str(sentence)) > 20 and len(str(sentence)) < 100:
                    # Check if sentence contains important keywords
                    important_words = ['AI', 'machine learning', 'deep learning', 'data', 'model', 'algorithm']
                    if any(word.lower() in str(sentence).lower() for word in important_words):
                        insights.append(str(sentence))
            
        except Exception as e:
            self.logger.warning(f"Error extracting insights from text: {e}")
        
        return insights[:5]
    
    def _generate_hashtags(self, title: str, summary: str) -> List[str]:
        """Generate relevant hashtags for the content."""
        hashtags = []
        
        # Get default hashtags from config
        default_hashtags = config.get_post_generation().get('hashtags', {}).get('default', [])
        hashtags.extend(default_hashtags)
        
        # Extract topic-specific hashtags
        text = f"{title} {summary}".lower()
        
        # AI/ML specific hashtags
        if any(word in text for word in ['ai', 'artificial intelligence']):
            hashtags.append('#ArtificialIntelligence')
        if any(word in text for word in ['machine learning', 'ml']):
            hashtags.append('#MachineLearning')
        if any(word in text for word in ['deep learning', 'neural network']):
            hashtags.append('#DeepLearning')
        if any(word in text for word in ['data science', 'data scientist']):
            hashtags.append('#DataScience')
        if any(word in text for word in ['nlp', 'natural language']):
            hashtags.append('#NLP')
        if any(word in text for word in ['computer vision', 'cv']):
            hashtags.append('#ComputerVision')
        if any(word in text for word in ['robotics', 'robot']):
            hashtags.append('#Robotics')
        if any(word in text for word in ['startup', 'entrepreneur']):
            hashtags.append('#Startup')
        if any(word in text for word in ['tech', 'technology']):
            hashtags.append('#Tech')
        
        # Remove duplicates and limit to max hashtags
        max_hashtags = self.content_config.get('max_hashtags', 5)
        unique_hashtags = list(dict.fromkeys(hashtags))  # Preserve order while removing duplicates
        
        return unique_hashtags[:max_hashtags]
    
    def _calculate_content_score(self, title: str, summary: str, insights: List[str]) -> float:
        """Calculate a score for content quality and relevance."""
        score = 0.0
        
        # Title quality
        if len(title) > 10 and len(title) < 100:
            score += 0.2
        
        # Summary quality
        if len(summary) > 50 and len(summary) < 500:
            score += 0.3
        
        # Insights quality
        if insights:
            score += 0.2 * len(insights)
        
        # Content relevance (check for AI/ML keywords)
        ai_keywords = ['ai', 'machine learning', 'deep learning', 'artificial intelligence', 'data science']
        text = f"{title} {summary}".lower()
        keyword_count = sum(1 for keyword in ai_keywords if keyword in text)
        score += 0.1 * keyword_count
        
        # Sentiment analysis
        try:
            blob = TextBlob(f"{title} {summary}")
            sentiment = blob.sentiment.polarity
            if sentiment > 0:  # Positive sentiment
                score += 0.1
        except:
            pass
        
        return min(score, 1.0)  # Cap at 1.0
    
    def filter_by_quality(self, processed_articles: List[Dict[str, Any]], min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Filter articles by quality score."""
        filtered_articles = [
            article for article in processed_articles 
            if article.get('content_score', 0) >= min_score
        ]
        
        # Sort by content score (highest first)
        filtered_articles.sort(key=lambda x: x.get('content_score', 0), reverse=True)
        
        self.logger.info(f"Filtered {len(processed_articles)} articles to {len(filtered_articles)} high-quality articles")
        return filtered_articles
    
    def save_processed_articles(self, articles: List[Dict[str, Any]], filename: str = None) -> str:
        """Save processed articles to JSON file."""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/processed_articles_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Processed articles saved to: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving processed articles: {e}")
            raise
