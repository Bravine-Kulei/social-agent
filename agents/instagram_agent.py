"""
Instagram Agent - Responsible for extracting content from Instagram
"""
import asyncio
from typing import List, Dict, Optional
from crewai import Agent, Task
from loguru import logger
from services.instagram_scraper import InstagramScraper
from utils.video_processor import VideoProcessor
from config import settings

class InstagramAgent:
    """Agent responsible for Instagram content extraction and processing"""
    
    def __init__(self):
        self.scraper = InstagramScraper()
        self.video_processor = VideoProcessor()
        
        # Define the CrewAI agent
        self.agent = Agent(
            role="Instagram Content Extractor",
            goal="Extract and analyze Instagram videos from target users",
            backstory="""You are an expert at extracting content from Instagram.
            You understand how to navigate Instagram's structure, extract video content,
            and analyze the metadata to understand the context and meaning of posts.""",
            verbose=True,
            allow_delegation=False
        )
    
    async def extract_user_content(self, username: str, max_videos: int = 5) -> List[Dict]:
        """
        Extract recent videos from a specific Instagram user
        
        Args:
            username: Instagram username to extract from
            max_videos: Maximum number of videos to extract
            
        Returns:
            List of video data dictionaries
        """
        try:
            logger.info(f"Extracting content from Instagram user: {username}")
            
            # Get user's recent posts
            posts = await self.scraper.get_user_posts(username, max_videos)
            
            video_data = []
            for post in posts:
                if post.get('is_video', False):
                    # Process video
                    processed_video = await self._process_video_post(post)
                    if processed_video:
                        video_data.append(processed_video)
            
            logger.info(f"Successfully extracted {len(video_data)} videos from {username}")
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting content from {username}: {str(e)}")
            return []
    
    async def _process_video_post(self, post: Dict) -> Optional[Dict]:
        """
        Process a single video post
        
        Args:
            post: Raw post data from Instagram
            
        Returns:
            Processed video data or None if processing fails
        """
        try:
            # Download video
            video_path = await self.scraper.download_video(post['video_url'], post['shortcode'])
            
            if not video_path:
                return None
            
            # Extract video metadata
            video_info = await self.video_processor.analyze_video(video_path)
            
            # Prepare structured data
            processed_data = {
                'id': post['shortcode'],
                'username': post['username'],
                'caption': post.get('caption', ''),
                'hashtags': post.get('hashtags', []),
                'likes': post.get('likes', 0),
                'comments': post.get('comments', 0),
                'timestamp': post.get('timestamp'),
                'video_url': post['video_url'],
                'video_path': video_path,
                'video_info': video_info,
                'thumbnail_url': post.get('thumbnail_url'),
                'location': post.get('location'),
                'mentions': post.get('mentions', [])
            }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing video post {post.get('shortcode', 'unknown')}: {str(e)}")
            return None
    
    def create_extraction_task(self, usernames: List[str]) -> Task:
        """
        Create a CrewAI task for content extraction
        
        Args:
            usernames: List of Instagram usernames to extract from
            
        Returns:
            CrewAI Task object
        """
        return Task(
            description=f"""
            Extract recent video content from the following Instagram users: {', '.join(usernames)}
            
            For each user:
            1. Get their most recent {settings.max_videos_per_user} video posts
            2. Download the videos and extract metadata
            3. Analyze video content for context and themes
            4. Prepare structured data for content transformation
            
            Focus on high-engagement posts and ensure all metadata is captured.
            """,
            agent=self.agent,
            expected_output="List of structured video data with metadata and analysis"
        )
    
    async def execute_extraction(self, usernames: List[str]) -> List[Dict]:
        """
        Execute content extraction for multiple users
        
        Args:
            usernames: List of Instagram usernames
            
        Returns:
            Combined list of all extracted video data
        """
        all_content = []
        
        for username in usernames:
            user_content = await self.extract_user_content(username, settings.max_videos_per_user)
            all_content.extend(user_content)
        
        logger.info(f"Total content extracted: {len(all_content)} videos from {len(usernames)} users")
        return all_content
