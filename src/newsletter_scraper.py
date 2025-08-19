"""
Newsletter Scraper for DeepLearning.AI content
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin, urlparse
from .config import config

class NewsletterScraper:
    """Scraper for DeepLearning.AI newsletters."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.newsletter_sources = config.get_newsletter_sources()
        self.logger = logging.getLogger(__name__)
    
    def fetch_batch_newsletter(self, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Fetch content from The Batch newsletter."""
        try:
            url = self.newsletter_sources['deeplearning_ai']['batch_newsletter']['url']
            self.logger.info(f"Fetching Batch newsletter from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self._parse_batch_articles(soup, max_articles)
            
            self.logger.info(f"Successfully fetched {len(articles)} articles from Batch newsletter")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error fetching Batch newsletter: {e}")
            return []
    
    def fetch_data_points(self, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Fetch content from Data Points newsletter."""
        try:
            url = self.newsletter_sources['deeplearning_ai']['data_points']['url']
            self.logger.info(f"Fetching Data Points from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self._parse_data_points(soup, max_articles)
            
            self.logger.info(f"Successfully fetched {len(articles)} articles from Data Points")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error fetching Data Points: {e}")
            return []
    
    def _parse_batch_articles(self, soup: BeautifulSoup, max_articles: int) -> List[Dict[str, Any]]:
        """Parse articles from The Batch newsletter."""
        articles = []
        
        # Look for article containers
        article_selectors = [
            'article',
            '.post',
            '.article',
            '.entry',
            '[class*="post"]',
            '[class*="article"]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                break
        
        if not elements:
            # Fallback: look for any content that might be articles
            elements = soup.find_all(['div', 'section'], class_=re.compile(r'post|article|entry'))

        # If still nothing, fallback to link-based discovery for The Batch
        if not elements:
            try:
                link_elems = soup.select('a[href*="/the-batch/"]')
                seen_links = set()
                articles = []
                for a in link_elems:
                    href = a.get('href') or ""
                    text = a.get_text(strip=True) or ""
                    if not href or not text:
                        continue
                    # Deduplicate and only keep article-like links
                    if href in seen_links:
                        continue
                    seen_links.add(href)
                    articles.append({
                        'title': text,
                        'summary': '',
                        'link': urljoin(self.newsletter_sources['deeplearning_ai']['batch_newsletter']['url'], href),
                        'date': '',
                        'insights': [],
                        'source': 'deeplearning_ai',
                        'scraped_at': datetime.now().isoformat()
                    })
                    if len(articles) >= max_articles:
                        break
                if articles:
                    return articles
            except Exception as e:
                self.logger.warning(f"Fallback link parsing failed: {e}")
        
        for element in elements[:max_articles]:
            try:
                article = self._extract_article_data(element)
                if article and self._is_relevant_content(article):
                    articles.append(article)
            except Exception as e:
                self.logger.warning(f"Error parsing article: {e}")
                continue
        
        return articles
    
    def _parse_data_points(self, soup: BeautifulSoup, max_articles: int) -> List[Dict[str, Any]]:
        """Parse articles from Data Points newsletter."""
        articles = []
        
        # Similar parsing logic as batch articles
        article_selectors = [
            'article',
            '.post',
            '.article',
            '.entry',
            '[class*="post"]',
            '[class*="article"]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                break
        
        if not elements:
            elements = soup.find_all(['div', 'section'], class_=re.compile(r'post|article|entry'))
        
        for element in elements[:max_articles]:
            try:
                article = self._extract_article_data(element)
                if article and self._is_relevant_content(article):
                    articles.append(article)
            except Exception as e:
                self.logger.warning(f"Error parsing article: {e}")
                continue
        
        return articles
    
    def _extract_article_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract article data from HTML element.

        More permissive parsing to handle different layouts on the site.
        """
        try:
            # Prefer anchor inside article as title/link
            link_elem = None
            for a in element.find_all('a', href=True):
                href = a.get('href') or ""
                if '/the-batch/' in href:
                    link_elem = a
                    break
            if link_elem is None:
                link_elem = element.find('a', href=True)

            # Title: from header tags or link text
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text(strip=True) if title_elem else ""
            if not title and link_elem is not None:
                title = link_elem.get_text(strip=True)

            # Summary: prefer explicit summary/description, else first paragraph
            summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|description|excerpt'))
            if not summary_elem:
                summary_elem = element.find('p')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""

            # Link: join relative link to base
            link = ""
            if link_elem is not None:
                link = urljoin(
                    self.newsletter_sources['deeplearning_ai']['batch_newsletter']['url'],
                    link_elem.get('href')
                )

            # Date: best-effort
            date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time'))
            date_str = date_elem.get_text(strip=True) if date_elem else ""

            # Insights
            insights = self._extract_insights(element)

            # Require at least a title and link
            if not title or not link:
                return None

            return {
                'title': title,
                'summary': summary,
                'link': link,
                'date': date_str,
                'insights': insights,
                'source': 'deeplearning_ai',
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.warning(f"Error extracting article data: {e}")
            return None
    
    def _extract_insights(self, element) -> List[str]:
        """Extract key insights from article element."""
        insights = []
        
        # Look for bullet points, lists, or highlighted text
        insight_selectors = [
            'ul li',
            'ol li',
            '[class*="insight"]',
            '[class*="key"]',
            '[class*="takeaway"]',
            'strong',
            'b'
        ]
        
        for selector in insight_selectors:
            elements = element.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 200:
                    insights.append(text)
        
        return insights[:5]  # Limit to 5 insights
    
    def _is_relevant_content(self, article: Dict[str, Any]) -> bool:
        """Check if article content is relevant based on keywords."""
        content_filter = config.get_content_processing().get('content_filter', {})
        include_keywords = content_filter.get('keywords', [])
        exclude_keywords = content_filter.get('exclude_keywords', [])
        
        text = f"{article['title']} {article['summary']}".lower()
        
        # Check for excluded keywords
        for keyword in exclude_keywords:
            if keyword.lower() in text:
                return False
        
        # Check for included keywords
        if include_keywords:
            for keyword in include_keywords:
                if keyword.lower() in text:
                    return True
            return False
        
        return True
    
    def fetch_all_newsletters(self, max_articles_per_source: int = 5) -> List[Dict[str, Any]]:
        """Fetch content from all configured newsletter sources."""
        all_articles = []
        
        # Fetch from different sources
        batch_articles = self.fetch_batch_newsletter(max_articles_per_source)
        data_points_articles = self.fetch_data_points(max_articles_per_source)
        
        all_articles.extend(batch_articles)
        all_articles.extend(data_points_articles)
        
        # Sort by date if available
        all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        self.logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def save_articles(self, articles: List[Dict[str, Any]], filename: str = None) -> str:
        """Save fetched articles to JSON file."""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/articles_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Articles saved to: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving articles: {e}")
            raise
