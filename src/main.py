"""
Main LinkedIn Post Automation Script
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

from .config import config
from .newsletter_scraper import NewsletterScraper
from .content_processor import ContentProcessor
from .post_generator import PostGenerator
from .scheduler import PostScheduler

def setup_logging():
    """Setup logging configuration."""
    log_config = config.get_logging_config()
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('file', 'logs/linkedin_automation.log')
    Path(log_file).parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def fetch_content(max_articles: int = 10):
    """Fetch content from newsletters."""
    logger = logging.getLogger(__name__)
    logger.info("Starting content fetching process...")
    
    scraper = NewsletterScraper()
    
    try:
        # Fetch articles from all sources
        articles = scraper.fetch_all_newsletters(max_articles)
        
        if not articles:
            logger.warning("No articles fetched from newsletters")
            return []
        
        # Save raw articles
        articles_file = scraper.save_articles(articles)
        logger.info(f"Raw articles saved to: {articles_file}")
        
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching content: {e}")
        return []

def process_content(articles):
    """Process and format content for LinkedIn posts."""
    logger = logging.getLogger(__name__)
    logger.info("Starting content processing...")
    
    processor = ContentProcessor()
    
    try:
        # Process articles
        processed_articles = processor.process_articles(articles)
        
        if not processed_articles:
            logger.warning("No articles processed successfully")
            return []
        
        # Filter by quality
        high_quality_articles = processor.filter_by_quality(processed_articles, min_score=0.5)
        
        # Save processed articles
        processed_file = processor.save_processed_articles(high_quality_articles)
        logger.info(f"Processed articles saved to: {processed_file}")
        
        return high_quality_articles
        
    except Exception as e:
        logger.error(f"Error processing content: {e}")
        return []

def generate_posts(processed_articles, max_posts: int = 5):
    """Generate LinkedIn posts from processed content."""
    logger = logging.getLogger(__name__)
    logger.info("Starting post generation...")
    
    generator = PostGenerator()
    
    try:
        # Generate posts
        posts = generator.generate_posts(processed_articles, max_posts)
        
        if not posts:
            logger.warning("No posts generated")
            return []
        
        # Save generated posts
        posts_file = generator.save_posts(posts)
        logger.info(f"Generated posts saved to: {posts_file}")
        
        # Preview posts
        for i, post in enumerate(posts, 1):
            logger.info(f"\n--- Post {i} Preview ---")
            logger.info(generator.preview_post(post))
        
        return posts
        
    except Exception as e:
        logger.error(f"Error generating posts: {e}")
        return []

def schedule_posts(posts, auto_schedule: bool = False):
    """Schedule posts for posting."""
    logger = logging.getLogger(__name__)
    logger.info("Setting up post scheduling...")
    
    scheduler = PostScheduler()
    
    try:
        if auto_schedule:
            # Automatically schedule posts
            scheduled_posts = scheduler.schedule_posts(posts)
            logger.info(f"Scheduled {len(scheduled_posts)} posts automatically")
            
            # Show scheduling status
            status = scheduler.get_queue_status()
            logger.info(f"Scheduling status: {status}")
            
            return scheduled_posts
        else:
            # Add to queue for manual scheduling
            scheduler.add_to_queue(posts)
            status = scheduler.get_queue_status()
            logger.info(f"Added posts to queue. Status: {status}")
            
            return []
            
    except Exception as e:
        logger.error(f"Error scheduling posts: {e}")
        return []

def run_full_pipeline(max_articles: int = 10, max_posts: int = 5, auto_schedule: bool = False):
    """Run the complete LinkedIn post automation pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("Starting LinkedIn Post Automation Pipeline")
    
    try:
        # Step 1: Fetch content
        logger.info("=== Step 1: Fetching Content ===")
        articles = fetch_content(max_articles)
        if not articles:
            logger.error("Pipeline failed: No content fetched")
            return False
        
        # Step 2: Process content
        logger.info("=== Step 2: Processing Content ===")
        processed_articles = process_content(articles)
        if not processed_articles:
            logger.error("Pipeline failed: No content processed")
            return False
        
        # Step 3: Generate posts
        logger.info("=== Step 3: Generating Posts ===")
        posts = generate_posts(processed_articles, max_posts)
        if not posts:
            logger.error("Pipeline failed: No posts generated")
            return False
        
        # Step 4: Schedule posts
        logger.info("=== Step 4: Scheduling Posts ===")
        scheduled_posts = schedule_posts(posts, auto_schedule)
        
        logger.info("=== Pipeline Completed Successfully ===")
        logger.info(f"Summary: {len(articles)} articles → {len(processed_articles)} processed → {len(posts)} posts → {len(scheduled_posts)} scheduled")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return False

def show_status():
    """Show current system status."""
    logger = logging.getLogger(__name__)
    
    scheduler = PostScheduler()
    status = scheduler.get_queue_status()
    analytics = scheduler.get_posting_analytics()
    
    logger.info("=== System Status ===")
    logger.info(f"Queue size: {status['queue_size']}")
    logger.info(f"Scheduled posts: {status['scheduled_posts']}")
    logger.info(f"Posted today: {status['posted_today']}")
    logger.info(f"Failed posts: {status['failed_posts']}")
    
    if analytics:
        logger.info("=== Analytics ===")
        logger.info(f"Total posts: {analytics['total_posts']}")
        logger.info(f"Success rate: {analytics['success_rate']:.2%}")
        logger.info(f"Average engagement: {analytics['average_engagement_score']:.2f}")

def start_scheduler():
    """Start the scheduler daemon."""
    logger = logging.getLogger(__name__)
    logger.info("Starting scheduler daemon...")
    
    scheduler = PostScheduler()
    scheduler.start_scheduler()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Post Automation')
    parser.add_argument('--fetch', action='store_true', help='Fetch content from newsletters')
    parser.add_argument('--process', action='store_true', help='Process fetched content')
    parser.add_argument('--generate', action='store_true', help='Generate LinkedIn posts')
    parser.add_argument('--schedule', action='store_true', help='Schedule posts for posting')
    parser.add_argument('--auto-schedule', action='store_true', help='Automatically schedule posts')
    parser.add_argument('--pipeline', action='store_true', help='Run complete pipeline')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--start-scheduler', action='store_true', help='Start scheduler daemon')
    parser.add_argument('--max-articles', type=int, default=10, help='Maximum articles to fetch')
    parser.add_argument('--max-posts', type=int, default=5, help='Maximum posts to generate')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        if args.pipeline:
            # Run complete pipeline
            success = run_full_pipeline(args.max_articles, args.max_posts, args.auto_schedule)
            sys.exit(0 if success else 1)
        
        elif args.fetch:
            # Fetch content only
            articles = fetch_content(args.max_articles)
            sys.exit(0 if articles else 1)
        
        elif args.process:
            # Process content only (requires existing articles file)
            articles_file = "data/articles_latest.json"
            if not Path(articles_file).exists():
                logger.error(f"Articles file not found: {articles_file}")
                sys.exit(1)
            
            with open(articles_file, 'r') as f:
                articles = json.load(f)
            
            processed_articles = process_content(articles)
            sys.exit(0 if processed_articles else 1)
        
        elif args.generate:
            # Generate posts only (requires existing processed articles file)
            processed_file = "data/processed_articles_latest.json"
            if not Path(processed_file).exists():
                logger.error(f"Processed articles file not found: {processed_file}")
                sys.exit(1)
            
            with open(processed_file, 'r') as f:
                processed_articles = json.load(f)
            
            posts = generate_posts(processed_articles, args.max_posts)
            sys.exit(0 if posts else 1)
        
        elif args.schedule or args.auto_schedule:
            # Schedule posts only (requires existing posts file)
            posts_file = "data/generated_posts_latest.json"
            if not Path(posts_file).exists():
                logger.error(f"Posts file not found: {posts_file}")
                sys.exit(1)
            
            with open(posts_file, 'r') as f:
                posts = json.load(f)
            
            scheduled_posts = schedule_posts(posts, args.auto_schedule)
            sys.exit(0 if scheduled_posts or not args.auto_schedule else 1)
        
        elif args.status:
            # Show status
            show_status()
            sys.exit(0)
        
        elif args.start_scheduler:
            # Start scheduler daemon
            start_scheduler()
            sys.exit(0)
        
        else:
            # No arguments provided, show help
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
