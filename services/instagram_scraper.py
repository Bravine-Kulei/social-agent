"""
Instagram Scraper Service - Handles Instagram content extraction
"""
import asyncio
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
import instaloader
import requests
from loguru import logger
from config import settings

class InstagramScraper:
    """Service for scraping Instagram content"""
    
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=True,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False
        )
        
        # Create storage directories
        os.makedirs(settings.storage_path, exist_ok=True)
        os.makedirs(settings.temp_path, exist_ok=True)
        
        # Login if credentials provided
        if settings.instagram_username and settings.instagram_password:
            try:
                self.loader.login(settings.instagram_username, settings.instagram_password)
                logger.info("Successfully logged into Instagram")
            except Exception as e:
                logger.warning(f"Failed to login to Instagram: {str(e)}")
    
    async def get_user_posts(self, username: str, max_posts: int = 5) -> List[Dict]:
        """
        Get recent posts from an Instagram user
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of post data dictionaries
        """
        try:
            logger.info(f"Fetching posts from @{username}")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            posts_data = []
            post_count = 0
            
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                
                # Only process video posts
                if post.is_video:
                    post_data = await self._extract_post_data(post)
                    if post_data:
                        posts_data.append(post_data)
                        post_count += 1
            
            logger.info(f"Successfully extracted {len(posts_data)} video posts from @{username}")
            return posts_data
            
        except Exception as e:
            logger.error(f"Error fetching posts from @{username}: {str(e)}")
            return []
    
    async def _extract_post_data(self, post) -> Optional[Dict]:
        """
        Extract data from a single Instagram post
        
        Args:
            post: Instaloader Post object
            
        Returns:
            Post data dictionary or None if extraction fails
        """
        try:
            # Extract basic post information
            post_data = {
                'shortcode': post.shortcode,
                'username': post.owner_username,
                'caption': post.caption or '',
                'likes': post.likes,
                'comments': post.comments,
                'timestamp': post.date_utc.isoformat(),
                'is_video': post.is_video,
                'video_url': post.video_url if post.is_video else None,
                'thumbnail_url': post.url,
                'location': post.location.name if post.location else None,
                'hashtags': self._extract_hashtags(post.caption or ''),
                'mentions': self._extract_mentions(post.caption or ''),
                'video_duration': post.video_duration if post.is_video else None
            }
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error extracting post data: {str(e)}")
            return None
    
    def _extract_hashtags(self, caption: str) -> List[str]:
        """Extract hashtags from caption"""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, caption)
        return hashtags
    
    def _extract_mentions(self, caption: str) -> List[str]:
        """Extract mentions from caption"""
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, caption)
        return mentions
    
    async def download_video(self, video_url: str, shortcode: str) -> Optional[str]:
        """
        Download video from Instagram
        
        Args:
            video_url: Direct video URL
            shortcode: Post shortcode for filename
            
        Returns:
            Local file path or None if download fails
        """
        try:
            logger.info(f"Downloading video: {shortcode}")
            
            # Create filename
            filename = f"{shortcode}.mp4"
            file_path = os.path.join(settings.storage_path, filename)
            
            # Download video
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Video downloaded successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading video {shortcode}: {str(e)}")
            return None
    
    async def get_post_by_shortcode(self, shortcode: str) -> Optional[Dict]:
        """
        Get a specific post by its shortcode
        
        Args:
            shortcode: Instagram post shortcode
            
        Returns:
            Post data dictionary or None
        """
        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            if post.is_video:
                return await self._extract_post_data(post)
            else:
                logger.warning(f"Post {shortcode} is not a video")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching post {shortcode}: {str(e)}")
            return None
    
    async def search_hashtag_posts(self, hashtag: str, max_posts: int = 10) -> List[Dict]:
        """
        Search for posts by hashtag
        
        Args:
            hashtag: Hashtag to search for (without #)
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of post data dictionaries
        """
        try:
            logger.info(f"Searching posts with hashtag: #{hashtag}")
            
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            posts_data = []
            post_count = 0
            
            for post in hashtag_obj.get_posts():
                if post_count >= max_posts:
                    break
                
                if post.is_video:
                    post_data = await self._extract_post_data(post)
                    if post_data:
                        posts_data.append(post_data)
                        post_count += 1
            
            logger.info(f"Found {len(posts_data)} video posts with hashtag #{hashtag}")
            return posts_data
            
        except Exception as e:
            logger.error(f"Error searching hashtag #{hashtag}: {str(e)}")
            return []
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get basic information about an Instagram user
        
        Args:
            username: Instagram username
            
        Returns:
            User information dictionary or None
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            user_info = {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'profile_pic_url': profile.profile_pic_url
            }
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting user info for @{username}: {str(e)}")
            return None
    
    async def cleanup_old_files(self, days_old: int = 7):
        """
        Clean up old downloaded files
        
        Args:
            days_old: Delete files older than this many days
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for filename in os.listdir(settings.storage_path):
                file_path = os.path.join(settings.storage_path, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {filename}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
