"""
LinkedIn Post Scheduler
"""

import schedule
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from .config import config

class PostScheduler:
    """Schedule and manage LinkedIn posts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scheduling_config = config.get_scheduling()
        self.linkedin_config = config.get_linkedin_config()
        self.scheduled_posts = []
        self.post_queue = []
        self.is_running = False
        
        # Load existing scheduled posts
        self._load_scheduled_posts()
    
    def schedule_posts(self, posts: List[Dict[str, Any]], 
                      posting_times: List[str] = None) -> List[Dict[str, Any]]:
        """Schedule posts for automatic posting."""
        if not posting_times:
            posting_times = self.scheduling_config.get('posting_times', ['09:00', '12:00', '17:00'])
        
        max_posts_per_day = self.scheduling_config.get('max_posts_per_day', 3)
        min_interval_hours = self.scheduling_config.get('min_interval_hours', 4)
        
        scheduled_posts = []
        current_time = datetime.now()
        
        for i, post in enumerate(posts[:max_posts_per_day]):
            try:
                # Calculate posting time
                posting_time = self._calculate_posting_time(
                    current_time, posting_times, i, min_interval_hours
                )
                
                # Create scheduled post
                scheduled_post = {
                    'post': post,
                    'scheduled_time': posting_time.isoformat(),
                    'status': 'scheduled',
                    'created_at': current_time.isoformat(),
                    'post_id': f"post_{current_time.strftime('%Y%m%d_%H%M%S')}_{i}"
                }
                
                scheduled_posts.append(scheduled_post)
                
                # Schedule the post
                self._schedule_single_post(scheduled_post)
                
            except Exception as e:
                self.logger.error(f"Error scheduling post {i}: {e}")
                continue
        
        # Add to scheduled posts list
        self.scheduled_posts.extend(scheduled_posts)
        self._save_scheduled_posts()
        
        self.logger.info(f"Scheduled {len(scheduled_posts)} posts")
        return scheduled_posts
    
    def _calculate_posting_time(self, current_time: datetime, posting_times: List[str], 
                               post_index: int, min_interval_hours: int) -> datetime:
        """Calculate the optimal posting time for a post."""
        # Start with today
        target_date = current_time.date()
        
        # If we've already passed today's posting times, move to tomorrow
        for time_str in posting_times:
            hour, minute = map(int, time_str.split(':'))
            posting_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            
            if posting_time > current_time:
                # Found a valid time today
                return posting_time
        
        # Move to tomorrow and use the first posting time
        target_date += timedelta(days=1)
        hour, minute = map(int, posting_times[0].split(':'))
        return datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def _schedule_single_post(self, scheduled_post: Dict[str, Any]) -> None:
        """Schedule a single post using the schedule library."""
        try:
            scheduled_time = datetime.fromisoformat(scheduled_post['scheduled_time'])
            
            # Schedule the post
            schedule.every().day.at(scheduled_time.strftime('%H:%M')).do(
                self._post_to_linkedin, scheduled_post
            )
            
            self.logger.info(f"Scheduled post '{scheduled_post['post_id']}' for {scheduled_time}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling post: {e}")
    
    def _post_to_linkedin(self, scheduled_post: Dict[str, Any]) -> None:
        """Post content to LinkedIn (placeholder for actual LinkedIn API integration)."""
        try:
            self.logger.info(f"Posting to LinkedIn: {scheduled_post['post_id']}")
            
            # Update post status
            scheduled_post['status'] = 'posted'
            scheduled_post['posted_at'] = datetime.now().isoformat()
            
            # Here you would integrate with LinkedIn API
            # For now, we'll just log the post content
            post_content = scheduled_post['post']['content']
            self.logger.info(f"Post content:\n{post_content}")
            
            # Save updated status
            self._save_scheduled_posts()
            
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            scheduled_post['status'] = 'failed'
            scheduled_post['error'] = str(e)
            self._save_scheduled_posts()
    
    def add_to_queue(self, posts: List[Dict[str, Any]]) -> None:
        """Add posts to the posting queue."""
        self.post_queue.extend(posts)
        self.logger.info(f"Added {len(posts)} posts to queue. Queue size: {len(self.post_queue)}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of the posting queue."""
        return {
            'queue_size': len(self.post_queue),
            'scheduled_posts': len(self.scheduled_posts),
            'posted_today': len([p for p in self.scheduled_posts if p.get('status') == 'posted']),
            'failed_posts': len([p for p in self.scheduled_posts if p.get('status') == 'failed'])
        }
    
    def clear_queue(self) -> None:
        """Clear the posting queue."""
        self.post_queue.clear()
        self.logger.info("Posting queue cleared")
    
    def get_scheduled_posts(self, status: str = None) -> List[Dict[str, Any]]:
        """Get scheduled posts, optionally filtered by status."""
        if status:
            return [post for post in self.scheduled_posts if post.get('status') == status]
        return self.scheduled_posts.copy()
    
    def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post."""
        for post in self.scheduled_posts:
            if post.get('post_id') == post_id and post.get('status') == 'scheduled':
                post['status'] = 'cancelled'
                post['cancelled_at'] = datetime.now().isoformat()
                self._save_scheduled_posts()
                self.logger.info(f"Cancelled post: {post_id}")
                return True
        
        self.logger.warning(f"Post not found or already processed: {post_id}")
        return False
    
    def start_scheduler(self) -> None:
        """Start the scheduler daemon."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.logger.info("Starting LinkedIn post scheduler...")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
            self.is_running = False
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
            self.is_running = False
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler daemon."""
        self.is_running = False
        self.logger.info("Scheduler stopped")
    
    def _load_scheduled_posts(self) -> None:
        """Load scheduled posts from file."""
        try:
            file_path = Path("data/scheduled_posts.json")
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.scheduled_posts = json.load(f)
                self.logger.info(f"Loaded {len(self.scheduled_posts)} scheduled posts")
        except Exception as e:
            self.logger.warning(f"Could not load scheduled posts: {e}")
            self.scheduled_posts = []
    
    def _save_scheduled_posts(self) -> None:
        """Save scheduled posts to file."""
        try:
            file_path = Path("data/scheduled_posts.json")
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.scheduled_posts, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error saving scheduled posts: {e}")
    
    def get_posting_analytics(self) -> Dict[str, Any]:
        """Get analytics about posting performance."""
        if not self.scheduled_posts:
            return {}
        
        total_posts = len(self.scheduled_posts)
        posted_posts = [p for p in self.scheduled_posts if p.get('status') == 'posted']
        failed_posts = [p for p in self.scheduled_posts if p.get('status') == 'failed']
        
        # Calculate engagement scores
        engagement_scores = [p['post'].get('engagement_score', 0) for p in posted_posts]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        return {
            'total_posts': total_posts,
            'posted_posts': len(posted_posts),
            'failed_posts': len(failed_posts),
            'success_rate': len(posted_posts) / total_posts if total_posts > 0 else 0,
            'average_engagement_score': avg_engagement,
            'posts_today': len([p for p in posted_posts if 
                              datetime.fromisoformat(p.get('posted_at', '')).date() == datetime.now().date()])
        }
    
    def reschedule_failed_posts(self) -> List[Dict[str, Any]]:
        """Reschedule posts that failed to post."""
        failed_posts = [p for p in self.scheduled_posts if p.get('status') == 'failed']
        rescheduled = []
        
        for post in failed_posts:
            try:
                # Reset status
                post['status'] = 'scheduled'
                post['rescheduled_at'] = datetime.now().isoformat()
                
                # Reschedule for next available time
                posting_times = self.scheduling_config.get('posting_times', ['09:00', '12:00', '17:00'])
                new_time = self._calculate_posting_time(
                    datetime.now(), posting_times, 0, 1
                )
                post['scheduled_time'] = new_time.isoformat()
                
                # Schedule the post
                self._schedule_single_post(post)
                rescheduled.append(post)
                
            except Exception as e:
                self.logger.error(f"Error rescheduling post {post.get('post_id')}: {e}")
        
        if rescheduled:
            self._save_scheduled_posts()
            self.logger.info(f"Rescheduled {len(rescheduled)} failed posts")
        
        return rescheduled
