"""
LinkedIn Agent - Responsible for posting content to LinkedIn
"""
import asyncio
from typing import Dict, List, Optional
from crewai import Agent, Task
from loguru import logger
from services.social_media_poster import LinkedInPoster
from config import settings

class LinkedInAgent:
    """Agent responsible for posting content to LinkedIn"""
    
    def __init__(self):
        self.linkedin_poster = LinkedInPoster()
        
        # Define the CrewAI agent
        self.agent = Agent(
            role="LinkedIn Content Publisher",
            goal="Publish professional, engaging content to LinkedIn that drives business value",
            backstory="""You are a professional content strategist specializing in LinkedIn.
            You understand the professional networking platform's culture, best practices
            for B2B engagement, and how to create content that adds value to professional
            audiences while building thought leadership and brand awareness.""",
            verbose=True,
            allow_delegation=False
        )
    
    async def post_content(self, content_data: Dict) -> Dict:
        """
        Post content to LinkedIn
        
        Args:
            content_data: Transformed content data for LinkedIn
            
        Returns:
            Dictionary with posting results
        """
        try:
            logger.info(f"Posting content to LinkedIn: {content_data.get('original_id', 'unknown')}")
            
            # Validate content
            if not self._validate_content(content_data):
                return {'success': False, 'error': 'Content validation failed'}
            
            # Prepare post data
            post_data = self._prepare_post_data(content_data)
            
            # Post to LinkedIn
            result = await self.linkedin_poster.create_post(post_data)
            
            if result.get('success'):
                logger.info(f"Successfully posted to LinkedIn: {result.get('post_id')}")
                return {
                    'success': True,
                    'post_id': result.get('post_id'),
                    'post_url': result.get('post_url'),
                    'platform': 'linkedin',
                    'original_id': content_data.get('original_id')
                }
            else:
                logger.error(f"Failed to post to LinkedIn: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _validate_content(self, content_data: Dict) -> bool:
        """
        Validate content before posting
        
        Args:
            content_data: Content data to validate
            
        Returns:
            True if content is valid, False otherwise
        """
        try:
            # Check required fields
            if not content_data.get('text'):
                logger.error("No text content provided")
                return False
            
            # Check text length
            text_length = len(content_data['text'])
            if text_length > 3000:
                logger.error(f"Text too long: {text_length} characters")
                return False
            
            # Check media if present
            media = content_data.get('media', {})
            if media and media.get('type') == 'video':
                duration = media.get('duration', 0)
                if duration > 600:  # LinkedIn video limit (10 minutes)
                    logger.error(f"Video too long: {duration} seconds")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return False
    
    def _prepare_post_data(self, content_data: Dict) -> Dict:
        """
        Prepare post data for LinkedIn
        
        Args:
            content_data: Transformed content data
            
        Returns:
            Post data dictionary
        """
        post_data = {
            'text': content_data['text'],
            'hashtags': content_data.get('hashtags', []),
        }
        
        # Add media if present
        media = content_data.get('media', {})
        if media:
            post_data['media'] = {
                'type': media.get('type'),
                'path': media.get('path'),
                'title': f"Content from Instagram: {content_data.get('original_id', 'Unknown')}"
            }
        
        # Add professional context
        topics = content_data.get('topics', [])
        if topics:
            post_data['topics'] = topics
        
        # Add metadata
        post_data['metadata'] = {
            'original_id': content_data.get('original_id'),
            'sentiment': content_data.get('sentiment', 'neutral'),
            'engagement_score': content_data.get('engagement_score', 0),
            'content_type': 'video_transformation'
        }
        
        return post_data
    
    async def schedule_post(self, content_data: Dict, schedule_time: str) -> Dict:
        """
        Schedule a post for later
        
        Args:
            content_data: Content to schedule
            schedule_time: When to post (ISO format)
            
        Returns:
            Scheduling result
        """
        try:
            logger.info(f"Scheduling LinkedIn post for {schedule_time}")
            
            # Validate content first
            if not self._validate_content(content_data):
                return {'success': False, 'error': 'Content validation failed'}
            
            # Schedule with LinkedIn API or internal scheduler
            result = await self.linkedin_poster.schedule_post(
                self._prepare_post_data(content_data),
                schedule_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error scheduling LinkedIn post: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_posting_task(self, content_list: List[Dict]) -> Task:
        """
        Create a CrewAI task for posting content
        
        Args:
            content_list: List of content to post
            
        Returns:
            CrewAI Task object
        """
        return Task(
            description=f"""
            Post {len(content_list)} pieces of professional content to LinkedIn.
            
            For each piece of content:
            1. Validate the content meets LinkedIn requirements
            2. Ensure professional tone and value proposition
            3. Optimize for LinkedIn's algorithm and engagement
            4. Post with appropriate media and hashtags
            5. Monitor initial professional engagement
            6. Log results for business analysis
            
            Focus on building thought leadership and professional brand awareness.
            """,
            agent=self.agent,
            expected_output="List of posting results with post IDs and professional engagement metrics"
        )
    
    async def execute_posting(self, content_list: List[Dict]) -> List[Dict]:
        """
        Execute posting for multiple pieces of content
        
        Args:
            content_list: List of content data to post
            
        Returns:
            List of posting results
        """
        results = []
        
        for content_data in content_list:
            # Add delay between posts to avoid rate limiting
            if results:
                await asyncio.sleep(60)  # 1 minute delay for LinkedIn
            
            result = await self.post_content(content_data)
            results.append(result)
        
        successful_posts = len([r for r in results if r.get('success')])
        logger.info(f"LinkedIn posting complete: {successful_posts}/{len(content_list)} successful")
        
        return results
    
    async def get_engagement_metrics(self, post_ids: List[str]) -> Dict:
        """
        Get engagement metrics for posted content
        
        Args:
            post_ids: List of LinkedIn post IDs to check
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            metrics = await self.linkedin_poster.get_post_metrics(post_ids)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn engagement metrics: {str(e)}")
            return {}
    
    async def post_article(self, content_data: Dict, article_title: str) -> Dict:
        """
        Post content as a LinkedIn article (for longer content)
        
        Args:
            content_data: Content data
            article_title: Title for the article
            
        Returns:
            Article posting result
        """
        try:
            logger.info(f"Creating LinkedIn article: {article_title}")
            
            article_data = {
                'title': article_title,
                'content': content_data['text'],
                'media': content_data.get('media', {}),
                'topics': content_data.get('topics', [])
            }
            
            result = await self.linkedin_poster.create_article(article_data)
            return result
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn article: {str(e)}")
            return {'success': False, 'error': str(e)}
