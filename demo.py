#!/usr/bin/env python3
"""
LinkedIn Post Automation - Demonstration Script
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.newsletter_scraper import NewsletterScraper
from src.content_processor import ContentProcessor
from src.post_generator import PostGenerator
from src.scheduler import PostScheduler

def main():
    """Run a demonstration of the LinkedIn post automation system."""
    print("🚀 LinkedIn Post Automation System - Demonstration")
    print("=" * 60)
    
    # Sample newsletter articles (simulating fetched content)
    sample_articles = [
        {
            'title': 'Revolutionary AI Breakthrough in Healthcare',
            'summary': 'Researchers at Stanford have developed a new AI system that can diagnose rare diseases with 95% accuracy, potentially saving thousands of lives annually. The system uses advanced machine learning algorithms to analyze medical imaging and patient data.',
            'insights': [
                '95% accuracy in rare disease diagnosis',
                'Uses advanced ML algorithms',
                'Analyzes medical imaging and patient data',
                'Potential to save thousands of lives'
            ],
            'link': 'https://example.com/ai-healthcare-breakthrough',
            'source': 'deeplearning_ai',
            'date': '2024-01-15'
        },
        {
            'title': 'The Future of Machine Learning: AutoML Takes Center Stage',
            'summary': 'Automated Machine Learning (AutoML) is revolutionizing how businesses implement AI solutions. Companies are seeing 40% faster deployment times and 30% cost reductions when using AutoML platforms.',
            'insights': [
                '40% faster AI deployment times',
                '30% cost reduction with AutoML',
                'Revolutionizing business AI implementation',
                'AutoML platforms gaining popularity'
            ],
            'link': 'https://example.com/automl-future',
            'source': 'deeplearning_ai',
            'date': '2024-01-14'
        },
        {
            'title': 'Data Science Trends That Will Dominate 2024',
            'summary': 'From edge computing to federated learning, 2024 is set to be a transformative year for data science. Organizations are increasingly adopting these technologies to improve efficiency and maintain data privacy.',
            'insights': [
                'Edge computing gaining traction',
                'Federated learning for privacy',
                'Transformative year for data science',
                'Focus on efficiency and privacy'
            ],
            'link': 'https://example.com/data-science-trends-2024',
            'source': 'deeplearning_ai',
            'date': '2024-01-13'
        }
    ]
    
    print("📰 Step 1: Processing Newsletter Articles")
    print("-" * 40)
    
    # Process articles
    processor = ContentProcessor()
    processed_articles = processor.process_articles(sample_articles)
    
    print(f"✓ Processed {len(processed_articles)} articles")
    for i, article in enumerate(processed_articles, 1):
        print(f"  {i}. {article['title']}")
        print(f"     Score: {article['content_score']:.2f} | Hashtags: {len(article['hashtags'])}")
    
    print("\n📝 Step 2: Generating LinkedIn Posts")
    print("-" * 40)
    
    # Generate posts
    generator = PostGenerator()
    posts = generator.generate_posts(processed_articles, max_posts=3)
    
    print(f"✓ Generated {len(posts)} LinkedIn posts")
    
    # Show post previews
    for i, post in enumerate(posts, 1):
        print(f"\n--- Post {i} ---")
        print(f"Length: {post['post_length']} characters")
        print(f"Engagement Score: {post['engagement_score']:.2f}")
        print(f"Hashtags: {len(post['article']['hashtags'])}")
        print("\nContent Preview:")
        print(post['content'][:200] + "..." if len(post['content']) > 200 else post['content'])
    
    print("\n⏰ Step 3: Scheduling Posts")
    print("-" * 40)
    
    # Schedule posts
    scheduler = PostScheduler()
    scheduled_posts = scheduler.schedule_posts(posts)
    
    print(f"✓ Scheduled {len(scheduled_posts)} posts")
    for i, scheduled in enumerate(scheduled_posts, 1):
        print(f"  {i}. Post ID: {scheduled['post_id']}")
        print(f"     Scheduled for: {scheduled['scheduled_time']}")
        print(f"     Status: {scheduled['status']}")
    
    print("\n📊 Step 4: System Analytics")
    print("-" * 40)
    
    # Show analytics
    status = scheduler.get_queue_status()
    analytics = scheduler.get_posting_analytics()
    
    print(f"Queue Status:")
    print(f"  - Queue size: {status['queue_size']}")
    print(f"  - Scheduled posts: {status['scheduled_posts']}")
    print(f"  - Posted today: {status['posted_today']}")
    print(f"  - Failed posts: {status['failed_posts']}")
    
    if analytics:
        print(f"\nAnalytics:")
        print(f"  - Total posts: {analytics['total_posts']}")
        print(f"  - Success rate: {analytics['success_rate']:.1%}")
        print(f"  - Average engagement: {analytics['average_engagement_score']:.2f}")
    
    print("\n" + "=" * 60)
    print("🎉 Demonstration Completed Successfully!")
    print("\nNext Steps:")
    print("1. Configure LinkedIn API credentials in .env file")
    print("2. Run: python -m src.main --pipeline --max-articles 10 --max-posts 5")
    print("3. Check generated files in data/ directory")
    print("4. Monitor logs in logs/ directory")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
