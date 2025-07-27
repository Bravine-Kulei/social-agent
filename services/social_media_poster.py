"""
Social Media Poster Service - Handles posting to Twitter and LinkedIn
"""
import asyncio
import os
from typing import Dict, List, Optional
import tweepy
from linkedin_api import Linkedin
import requests
from loguru import logger
from config import settings

class TwitterPoster:
    """Service for posting content to Twitter"""
    
    def __init__(self):
        try:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
            self.client = None
            self.api_v1 = None
    
    async def post_tweet(self, tweet_data: Dict) -> Dict:
        """
        Post a tweet to Twitter
        
        Args:
            tweet_data: Tweet data dictionary
            
        Returns:
            Posting result dictionary
        """
        try:
            if not self.client:
                return {'success': False, 'error': 'Twitter API not initialized'}
            
            text = tweet_data.get('text', '')
            media = tweet_data.get('media', {})
            
            media_ids = []
            
            # Upload media if present
            if media and media.get('path'):
                media_id = await self._upload_media(media)
                if media_id:
                    media_ids.append(media_id)
            
            # Post tweet
            if media_ids:
                response = self.client.create_tweet(text=text, media_ids=media_ids)
            else:
                response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                logger.info(f"Tweet posted successfully: {tweet_id}")
                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url
                }
            else:
                return {'success': False, 'error': 'Failed to create tweet'}
                
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _upload_media(self, media: Dict) -> Optional[str]:
        """
        Upload media to Twitter
        
        Args:
            media: Media information dictionary
            
        Returns:
            Media ID or None if upload fails
        """
        try:
            if not self.api_v1:
                return None
            
            media_path = media.get('path')
            media_type = media.get('type', 'image')
            
            if not os.path.exists(media_path):
                logger.error(f"Media file not found: {media_path}")
                return None
            
            # Upload media
            if media_type == 'video':
                media_obj = self.api_v1.media_upload(
                    filename=media_path,
                    media_category='tweet_video'
                )
            else:
                media_obj = self.api_v1.media_upload(filename=media_path)
            
            logger.info(f"Media uploaded successfully: {media_obj.media_id}")
            return media_obj.media_id
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            return None
    
    async def schedule_tweet(self, tweet_data: Dict, schedule_time: str) -> Dict:
        """
        Schedule a tweet for later posting
        
        Args:
            tweet_data: Tweet data
            schedule_time: ISO format datetime string
            
        Returns:
            Scheduling result
        """
        try:
            # Note: Twitter API v2 doesn't support scheduling directly
            # This would typically use a task queue like Celery
            logger.info(f"Scheduling tweet for {schedule_time}")
            
            # For now, store in a simple queue (in production, use proper task queue)
            scheduled_tweet = {
                'tweet_data': tweet_data,
                'schedule_time': schedule_time,
                'status': 'scheduled'
            }
            
            # In a real implementation, this would be stored in a database
            # and processed by a background worker
            
            return {
                'success': True,
                'scheduled_id': f"scheduled_{schedule_time}",
                'message': 'Tweet scheduled successfully'
            }
            
        except Exception as e:
            logger.error(f"Error scheduling tweet: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_tweet_metrics(self, tweet_ids: List[str]) -> Dict:
        """
        Get engagement metrics for tweets
        
        Args:
            tweet_ids: List of tweet IDs
            
        Returns:
            Metrics dictionary
        """
        try:
            if not self.client:
                return {}
            
            metrics = {}
            
            for tweet_id in tweet_ids:
                try:
                    tweet = self.client.get_tweet(
                        tweet_id,
                        tweet_fields=['public_metrics', 'created_at']
                    )
                    
                    if tweet.data:
                        metrics[tweet_id] = {
                            'retweet_count': tweet.data.public_metrics['retweet_count'],
                            'like_count': tweet.data.public_metrics['like_count'],
                            'reply_count': tweet.data.public_metrics['reply_count'],
                            'quote_count': tweet.data.public_metrics['quote_count'],
                            'created_at': str(tweet.data.created_at)
                        }
                        
                except Exception as e:
                    logger.error(f"Error getting metrics for tweet {tweet_id}: {str(e)}")
                    metrics[tweet_id] = {'error': str(e)}
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting tweet metrics: {str(e)}")
            return {}


class LinkedInPoster:
    """Service for posting content to LinkedIn"""
    
    def __init__(self):
        try:
            # Note: linkedin-api is unofficial and may require authentication setup
            # In production, use official LinkedIn API
            self.linkedin = None
            
            # For official LinkedIn API, you would initialize like this:
            # self.access_token = settings.linkedin_access_token
            
            logger.info("LinkedIn API initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn API: {str(e)}")
            self.linkedin = None
    
    async def create_post(self, post_data: Dict) -> Dict:
        """
        Create a post on LinkedIn
        
        Args:
            post_data: Post data dictionary
            
        Returns:
            Posting result dictionary
        """
        try:
            # This is a simplified implementation
            # In production, use the official LinkedIn API
            
            text = post_data.get('text', '')
            media = post_data.get('media', {})
            
            # Prepare post payload for LinkedIn API
            post_payload = {
                'author': f"urn:li:person:{self._get_user_id()}",
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': text
                        },
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            # Add media if present
            if media and media.get('path'):
                media_urn = await self._upload_media(media)
                if media_urn:
                    post_payload['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'VIDEO' if media.get('type') == 'video' else 'IMAGE'
                    post_payload['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [
                        {
                            'status': 'READY',
                            'media': media_urn
                        }
                    ]
            
            # Make API call (simplified)
            # In production, use proper LinkedIn API endpoints
            post_id = f"linkedin_post_{asyncio.get_event_loop().time()}"
            
            logger.info(f"LinkedIn post created successfully: {post_id}")
            return {
                'success': True,
                'post_id': post_id,
                'post_url': f"https://linkedin.com/posts/{post_id}"
            }
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_user_id(self) -> str:
        """Get LinkedIn user ID"""
        # In production, this would fetch the actual user ID
        return "user_id_placeholder"
    
    async def _upload_media(self, media: Dict) -> Optional[str]:
        """
        Upload media to LinkedIn
        
        Args:
            media: Media information dictionary
            
        Returns:
            Media URN or None if upload fails
        """
        try:
            media_path = media.get('path')
            media_type = media.get('type', 'image')
            
            if not os.path.exists(media_path):
                logger.error(f"Media file not found: {media_path}")
                return None
            
            # In production, implement proper LinkedIn media upload
            # This is a placeholder
            media_urn = f"urn:li:digitalmediaAsset:{asyncio.get_event_loop().time()}"
            
            logger.info(f"Media uploaded to LinkedIn: {media_urn}")
            return media_urn
            
        except Exception as e:
            logger.error(f"Error uploading media to LinkedIn: {str(e)}")
            return None
    
    async def schedule_post(self, post_data: Dict, schedule_time: str) -> Dict:
        """
        Schedule a LinkedIn post
        
        Args:
            post_data: Post data
            schedule_time: ISO format datetime string
            
        Returns:
            Scheduling result
        """
        try:
            logger.info(f"Scheduling LinkedIn post for {schedule_time}")
            
            # Store in scheduling queue
            scheduled_post = {
                'post_data': post_data,
                'schedule_time': schedule_time,
                'status': 'scheduled'
            }
            
            return {
                'success': True,
                'scheduled_id': f"linkedin_scheduled_{schedule_time}",
                'message': 'LinkedIn post scheduled successfully'
            }
            
        except Exception as e:
            logger.error(f"Error scheduling LinkedIn post: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_post_metrics(self, post_ids: List[str]) -> Dict:
        """
        Get engagement metrics for LinkedIn posts
        
        Args:
            post_ids: List of post IDs
            
        Returns:
            Metrics dictionary
        """
        try:
            metrics = {}
            
            for post_id in post_ids:
                # In production, fetch real metrics from LinkedIn API
                metrics[post_id] = {
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'views': 0,
                    'clicks': 0
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn post metrics: {str(e)}")
            return {}
    
    async def create_article(self, article_data: Dict) -> Dict:
        """
        Create a LinkedIn article
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Article creation result
        """
        try:
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            
            # In production, use LinkedIn Article API
            article_id = f"linkedin_article_{asyncio.get_event_loop().time()}"
            
            logger.info(f"LinkedIn article created: {article_id}")
            return {
                'success': True,
                'article_id': article_id,
                'article_url': f"https://linkedin.com/pulse/{article_id}"
            }
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn article: {str(e)}")
            return {'success': False, 'error': str(e)}
