"""
Analytics and Monitoring for Instagram-to-Social Media Agent System
Track performance, success rates, and system metrics
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class PostMetrics:
    """Metrics for a single post"""
    timestamp: str
    instagram_user: str
    instagram_shortcode: str
    instagram_likes: int
    instagram_comments: int
    platform: str
    success: bool
    twitter_post_id: str = ""
    error_message: str = ""
    content_length: int = 0
    processing_time: float = 0.0

@dataclass
class SystemMetrics:
    """Overall system metrics"""
    total_posts: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    total_instagram_users: int = 0
    total_videos_processed: int = 0
    last_run: str = ""

class AnalyticsTracker:
    """Track and analyze system performance"""
    
    def __init__(self, data_file: str = "analytics_data.json"):
        self.data_file = data_file
        self.posts: List[PostMetrics] = []
        self.load_data()
    
    def load_data(self):
        """Load existing analytics data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.posts = [PostMetrics(**post) for post in data.get('posts', [])]
                logger.info(f"📊 Loaded {len(self.posts)} historical posts")
            except Exception as e:
                logger.warning(f"⚠️ Could not load analytics data: {e}")
                self.posts = []
        else:
            logger.info("📊 Starting fresh analytics tracking")
    
    def save_data(self):
        """Save analytics data to file"""
        try:
            data = {
                'posts': [asdict(post) for post in self.posts],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved analytics data ({len(self.posts)} posts)")
        except Exception as e:
            logger.error(f"❌ Could not save analytics data: {e}")
    
    def track_post(self, 
                   instagram_user: str,
                   instagram_shortcode: str,
                   instagram_likes: int,
                   instagram_comments: int,
                   platform: str,
                   success: bool,
                   twitter_post_id: str = "",
                   error_message: str = "",
                   content_length: int = 0,
                   processing_time: float = 0.0):
        """Track a single post"""
        
        post = PostMetrics(
            timestamp=datetime.now().isoformat(),
            instagram_user=instagram_user,
            instagram_shortcode=instagram_shortcode,
            instagram_likes=instagram_likes,
            instagram_comments=instagram_comments,
            platform=platform,
            success=success,
            twitter_post_id=twitter_post_id,
            error_message=error_message,
            content_length=content_length,
            processing_time=processing_time
        )
        
        self.posts.append(post)
        self.save_data()
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"📊 Tracked post: {instagram_shortcode} → {platform} ({status})")
    
    def get_system_metrics(self, days: int = 30) -> SystemMetrics:
        """Get system metrics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_posts = [
            post for post in self.posts 
            if datetime.fromisoformat(post.timestamp) > cutoff_date
        ]
        
        if not recent_posts:
            return SystemMetrics()
        
        successful = [post for post in recent_posts if post.success]
        failed = [post for post in recent_posts if not post.success]
        
        success_rate = (len(successful) / len(recent_posts)) * 100 if recent_posts else 0
        avg_time = sum(post.processing_time for post in recent_posts) / len(recent_posts)
        
        unique_users = len(set(post.instagram_user for post in recent_posts))
        
        return SystemMetrics(
            total_posts=len(recent_posts),
            successful_posts=len(successful),
            failed_posts=len(failed),
            success_rate=success_rate,
            avg_processing_time=avg_time,
            total_instagram_users=unique_users,
            total_videos_processed=len(recent_posts),
            last_run=recent_posts[-1].timestamp if recent_posts else ""
        )
    
    def print_analytics_report(self, days: int = 30):
        """Print comprehensive analytics report"""
        metrics = self.get_system_metrics(days)
        
        print("\n" + "="*70)
        print(f"📊 ANALYTICS REPORT - LAST {days} DAYS")
        print("="*70)
        
        print(f"📤 Total Posts: {metrics.total_posts}")
        print(f"✅ Successful: {metrics.successful_posts}")
        print(f"❌ Failed: {metrics.failed_posts}")
        print(f"📊 Success Rate: {metrics.success_rate:.1f}%")
        print(f"⏱️ Avg Processing Time: {metrics.avg_processing_time:.2f}s")
        print(f"👥 Instagram Users: {metrics.total_instagram_users}")
        print(f"🎬 Videos Processed: {metrics.total_videos_processed}")
        
        if metrics.last_run:
            last_run = datetime.fromisoformat(metrics.last_run)
            print(f"🕐 Last Run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Platform breakdown
        platform_stats = self._get_platform_stats(days)
        if platform_stats:
            print(f"\n📱 Platform Breakdown:")
            for platform, stats in platform_stats.items():
                print(f"   • {platform.title()}: {stats['success']}/{stats['total']} ({stats['rate']:.1f}%)")
        
        # Top performing content
        top_content = self._get_top_content(days)
        if top_content:
            print(f"\n🏆 Top Performing Content:")
            for i, post in enumerate(top_content[:3], 1):
                print(f"   {i}. {post.instagram_shortcode} - {post.instagram_likes:,} likes")
        
        # Error analysis
        error_analysis = self._get_error_analysis(days)
        if error_analysis:
            print(f"\n🔍 Common Errors:")
            for error, count in error_analysis.items():
                print(f"   • {error}: {count} occurrences")
        
        print("="*70)
    
    def _get_platform_stats(self, days: int) -> Dict[str, Dict]:
        """Get platform-specific statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_posts = [
            post for post in self.posts 
            if datetime.fromisoformat(post.timestamp) > cutoff_date
        ]
        
        platform_stats = {}
        for post in recent_posts:
            platform = post.platform
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'success': 0}
            
            platform_stats[platform]['total'] += 1
            if post.success:
                platform_stats[platform]['success'] += 1
        
        # Calculate rates
        for platform, stats in platform_stats.items():
            stats['rate'] = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        return platform_stats
    
    def _get_top_content(self, days: int) -> List[PostMetrics]:
        """Get top performing content by engagement"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_posts = [
            post for post in self.posts 
            if datetime.fromisoformat(post.timestamp) > cutoff_date and post.success
        ]
        
        return sorted(recent_posts, key=lambda x: x.instagram_likes, reverse=True)
    
    def _get_error_analysis(self, days: int) -> Dict[str, int]:
        """Analyze common errors"""
        cutoff_date = datetime.now() - timedelta(days=days)
        failed_posts = [
            post for post in self.posts 
            if datetime.fromisoformat(post.timestamp) > cutoff_date and not post.success
        ]
        
        error_counts = {}
        for post in failed_posts:
            error = post.error_message or "Unknown error"
            # Simplify error messages
            if "rate limit" in error.lower():
                error = "Rate limiting"
            elif "unauthorized" in error.lower():
                error = "Authentication error"
            elif "forbidden" in error.lower():
                error = "Permission error"
            
            error_counts[error] = error_counts.get(error, 0) + 1
        
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# Global analytics instance
analytics = AnalyticsTracker()

def track_post_success(instagram_user: str, 
                      instagram_shortcode: str,
                      instagram_likes: int,
                      instagram_comments: int,
                      platform: str,
                      twitter_post_id: str,
                      content_length: int = 0,
                      processing_time: float = 0.0):
    """Track a successful post"""
    analytics.track_post(
        instagram_user=instagram_user,
        instagram_shortcode=instagram_shortcode,
        instagram_likes=instagram_likes,
        instagram_comments=instagram_comments,
        platform=platform,
        success=True,
        twitter_post_id=twitter_post_id,
        content_length=content_length,
        processing_time=processing_time
    )

def track_post_failure(instagram_user: str,
                      instagram_shortcode: str,
                      instagram_likes: int,
                      instagram_comments: int,
                      platform: str,
                      error_message: str,
                      processing_time: float = 0.0):
    """Track a failed post"""
    analytics.track_post(
        instagram_user=instagram_user,
        instagram_shortcode=instagram_shortcode,
        instagram_likes=instagram_likes,
        instagram_comments=instagram_comments,
        platform=platform,
        success=False,
        error_message=error_message,
        processing_time=processing_time
    )

if __name__ == "__main__":
    analytics.print_analytics_report()
