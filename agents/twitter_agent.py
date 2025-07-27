"""
Twitter Agent - Responsible for posting content to Twitter
"""
import asyncio
from typing import Dict, List, Optional
from crewai import Agent, Task
from loguru import logger
from services.social_media_poster import TwitterPoster
from config import settings

class TwitterAgent:
    """Agent responsible for posting content to Twitter"""
    
    def __init__(self):
        self.twitter_poster = TwitterPoster()
        
        # Define the CrewAI agent
        self.agent = Agent(
            role="Twitter Content Publisher",
            goal="Publish optimized content to Twitter with maximum engagement potential",
            backstory="""You are a social media expert specializing in Twitter engagement.
            You understand Twitter's algorithm, best posting times, and how to maximize
            reach and engagement. You ensure all posts comply with Twitter's guidelines
            and optimize for virality while maintaining authenticity.""",
            verbose=True,
            allow_delegation=False
        )
    
    async def post_content(self, content_data: Dict) -> Dict:
        """
        Post content to Twitter
        
        Args:
            content_data: Transformed content data for Twitter
            
        Returns:
            Dictionary with posting results
        """
        try:
            logger.info(f"Posting content to Twitter: {content_data.get('original_id', 'unknown')}")
            
            # Validate content
            if not self._validate_content(content_data):
                return {'success': False, 'error': 'Content validation failed'}
            
            # Prepare tweet data
            tweet_data = self._prepare_tweet_data(content_data)
            
            # Post to Twitter
            result = await self.twitter_poster.post_tweet(tweet_data)
            
            if result.get('success'):
                logger.info(f"Successfully posted to Twitter: {result.get('tweet_id')}")
                return {
                    'success': True,
                    'tweet_id': result.get('tweet_id'),
                    'tweet_url': result.get('tweet_url'),
                    'platform': 'twitter',
                    'original_id': content_data.get('original_id')
                }
            else:
                logger.error(f"Failed to post to Twitter: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
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
            if text_length > 280:
                logger.error(f"Text too long: {text_length} characters")
                return False
            
            # Check media if present
            media = content_data.get('media', {})
            if media and media.get('type') == 'video':
                duration = media.get('duration', 0)
                if duration > 140:  # Twitter video limit
                    logger.error(f"Video too long: {duration} seconds")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return False
    
    def _prepare_tweet_data(self, content_data: Dict) -> Dict:
        """
        Prepare tweet data for posting
        
        Args:
            content_data: Transformed content data
            
        Returns:
            Tweet data dictionary
        """
        tweet_data = {
            'text': content_data['text'],
            'hashtags': content_data.get('hashtags', []),
        }
        
        # Add media if present
        media = content_data.get('media', {})
        if media:
            tweet_data['media'] = {
                'type': media.get('type'),
                'path': media.get('path')
            }
        
        # Add metadata
        tweet_data['metadata'] = {
            'original_id': content_data.get('original_id'),
            'topics': content_data.get('topics', []),
            'sentiment': content_data.get('sentiment', 'neutral'),
            'engagement_score': content_data.get('engagement_score', 0)
        }
        
        return tweet_data
    
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
            logger.info(f"Scheduling Twitter post for {schedule_time}")
            
            # Validate content first
            if not self._validate_content(content_data):
                return {'success': False, 'error': 'Content validation failed'}
            
            # Schedule with Twitter API or internal scheduler
            result = await self.twitter_poster.schedule_tweet(
                self._prepare_tweet_data(content_data),
                schedule_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error scheduling Twitter post: {str(e)}")
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
            Post {len(content_list)} pieces of content to Twitter.
            
            For each piece of content:
            1. Validate the content meets Twitter requirements
            2. Optimize posting time for maximum engagement
            3. Post the content with appropriate media
            4. Monitor initial engagement
            5. Log results for analysis
            
            Ensure all posts comply with Twitter's terms of service and community guidelines.
            """,
            agent=self.agent,
            expected_output="List of posting results with tweet IDs and engagement metrics"
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
                await asyncio.sleep(30)  # 30 second delay
            
            result = await self.post_content(content_data)
            results.append(result)
        
        successful_posts = len([r for r in results if r.get('success')])
        logger.info(f"Twitter posting complete: {successful_posts}/{len(content_list)} successful")
        
        return results
    
    async def get_engagement_metrics(self, tweet_ids: List[str]) -> Dict:
        """
        Get engagement metrics for posted tweets
        
        Args:
            tweet_ids: List of tweet IDs to check
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            metrics = await self.twitter_poster.get_tweet_metrics(tweet_ids)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting Twitter engagement metrics: {str(e)}")
            return {}
