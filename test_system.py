#!/usr/bin/env python3
"""
Test script for LinkedIn Post Automation System
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from src.newsletter_scraper import NewsletterScraper
from src.content_processor import ContentProcessor
from src.post_generator import PostGenerator
from src.scheduler import PostScheduler

def setup_logging():
    """Setup basic logging for testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_configuration():
    """Test configuration loading."""
    print("=== Testing Configuration ===")
    try:
        newsletter_sources = config.get_newsletter_sources()
        print(f"✓ Newsletter sources loaded: {list(newsletter_sources.keys())}")
        
        content_config = config.get_content_processing()
        print(f"✓ Content processing config loaded: {len(content_config)} settings")
        
        post_config = config.get_post_generation()
        print(f"✓ Post generation config loaded: {len(post_config.get('templates', []))} templates")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_newsletter_scraper():
    """Test newsletter scraper initialization."""
    print("\n=== Testing Newsletter Scraper ===")
    try:
        scraper = NewsletterScraper()
        print("✓ Newsletter scraper initialized successfully")
        
        # Test fetching (this will fail without actual content, but tests the structure)
        sources = scraper.newsletter_sources
        print(f"✓ Found {len(sources)} newsletter sources")
        
        return True
    except Exception as e:
        print(f"✗ Newsletter scraper test failed: {e}")
        return False

def test_content_processor():
    """Test content processor initialization."""
    print("\n=== Testing Content Processor ===")
    try:
        processor = ContentProcessor()
        print("✓ Content processor initialized successfully")
        
        # Test with sample data
        sample_article = {
            'title': 'Test AI Article',
            'summary': 'This is a test article about artificial intelligence and machine learning.',
            'insights': ['AI is transforming industries', 'Machine learning is key'],
            'link': 'https://example.com',
            'source': 'test'
        }
        
        processed = processor.process_single_article(sample_article)
        if processed:
            print(f"✓ Sample article processed successfully")
            print(f"  - Content score: {processed.get('content_score', 0):.2f}")
            print(f"  - Hashtags: {len(processed.get('hashtags', []))}")
        else:
            print("✗ Sample article processing failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Content processor test failed: {e}")
        return False

def test_post_generator():
    """Test post generator."""
    print("\n=== Testing Post Generator ===")
    try:
        generator = PostGenerator()
        print("✓ Post generator initialized successfully")
        
        # Test with sample processed article
        sample_processed = {
            'title': 'Test AI Article',
            'summary': 'This is a test article about artificial intelligence and machine learning.',
            'key_insights': ['AI is transforming industries', 'Machine learning is key'],
            'hashtags': ['#AI', '#MachineLearning'],
            'link': 'https://example.com',
            'content_score': 0.8
        }
        
        post = generator.generate_single_post(sample_processed)
        if post:
            print(f"✓ Sample post generated successfully")
            print(f"  - Post length: {post.get('post_length', 0)} characters")
            print(f"  - Engagement score: {post.get('engagement_score', 0):.2f}")
            print(f"  - Template used: {post.get('template_used', 'Unknown')[:50]}...")
        else:
            print("✗ Sample post generation failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Post generator test failed: {e}")
        return False

def test_scheduler():
    """Test scheduler initialization."""
    print("\n=== Testing Scheduler ===")
    try:
        scheduler = PostScheduler()
        print("✓ Scheduler initialized successfully")
        
        # Test queue status
        status = scheduler.get_queue_status()
        print(f"✓ Queue status: {status}")
        
        # Test analytics
        analytics = scheduler.get_posting_analytics()
        print(f"✓ Analytics loaded: {len(analytics)} metrics")
        
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        return False

def test_full_pipeline():
    """Test the complete pipeline with sample data."""
    print("\n=== Testing Full Pipeline ===")
    try:
        # Sample articles
        sample_articles = [
            {
                'title': 'Breakthrough in AI Research',
                'summary': 'Researchers have developed a new machine learning algorithm that improves accuracy by 15%.',
                'insights': ['15% accuracy improvement', 'New algorithm developed', 'Research breakthrough'],
                'link': 'https://example.com/ai-research',
                'source': 'deeplearning_ai',
                'date': '2024-01-15'
            },
            {
                'title': 'Data Science Trends 2024',
                'summary': 'Key trends in data science and machine learning for 2024 include automated ML and edge computing.',
                'insights': ['Automated ML growing', 'Edge computing important', '2024 trends identified'],
                'link': 'https://example.com/trends-2024',
                'source': 'deeplearning_ai',
                'date': '2024-01-14'
            }
        ]
        
        # Step 1: Process content
        processor = ContentProcessor()
        processed_articles = processor.process_articles(sample_articles)
        print(f"✓ Processed {len(processed_articles)} articles")
        
        # Step 2: Generate posts
        generator = PostGenerator()
        posts = generator.generate_posts(processed_articles, max_posts=2)
        print(f"✓ Generated {len(posts)} posts")
        
        # Step 3: Schedule posts
        scheduler = PostScheduler()
        scheduled_posts = scheduler.schedule_posts(posts)
        print(f"✓ Scheduled {len(scheduled_posts)} posts")
        
        return True
    except Exception as e:
        print(f"✗ Full pipeline test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("LinkedIn Post Automation System - Test Suite")
    print("=" * 50)
    
    setup_logging()
    
    tests = [
        test_configuration,
        test_newsletter_scraper,
        test_content_processor,
        test_post_generator,
        test_scheduler,
        test_full_pipeline
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Configure your LinkedIn API credentials in .env file")
        print("2. Run: python -m src.main --pipeline --max-articles 5 --max-posts 3")
        print("3. Check generated posts in data/ directory")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
