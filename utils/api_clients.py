"""
API Client Management Utilities
"""
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from loguru import logger
from config import settings

class APIClientManager:
    """Manages API clients and rate limiting"""
    
    def __init__(self):
        self.session = None
        self.rate_limits = {
            'twitter': {'requests': 0, 'reset_time': 0, 'limit': 300},
            'linkedin': {'requests': 0, 'reset_time': 0, 'limit': 100},
            'instagram': {'requests': 0, 'reset_time': 0, 'limit': 200}
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, 
                          method: str, 
                          url: str, 
                          headers: Optional[Dict] = None,
                          data: Optional[Dict] = None,
                          params: Optional[Dict] = None,
                          platform: str = 'general') -> Optional[Dict]:
        """
        Make HTTP request with rate limiting
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            data: Request data
            params: URL parameters
            platform: Platform for rate limiting
            
        Returns:
            Response data or None if request fails
        """
        try:
            # Check rate limits
            if not await self._check_rate_limit(platform):
                logger.warning(f"Rate limit exceeded for {platform}")
                return None
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Make request
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                
                # Update rate limit tracking
                self._update_rate_limit(platform, response.headers)
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning(f"Rate limited by {platform} API")
                    return None
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making API request: {str(e)}")
            return None
    
    async def _check_rate_limit(self, platform: str) -> bool:
        """
        Check if request is within rate limits
        
        Args:
            platform: Platform to check
            
        Returns:
            True if request is allowed, False otherwise
        """
        import time
        
        if platform not in self.rate_limits:
            return True
        
        rate_info = self.rate_limits[platform]
        current_time = time.time()
        
        # Reset counter if time window has passed
        if current_time > rate_info['reset_time']:
            rate_info['requests'] = 0
            rate_info['reset_time'] = current_time + 3600  # 1 hour window
        
        # Check if under limit
        return rate_info['requests'] < rate_info['limit']
    
    def _update_rate_limit(self, platform: str, headers: Dict):
        """
        Update rate limit tracking from response headers
        
        Args:
            platform: Platform name
            headers: Response headers
        """
        if platform not in self.rate_limits:
            return
        
        # Increment request counter
        self.rate_limits[platform]['requests'] += 1
        
        # Update limits from headers if available
        if 'x-rate-limit-remaining' in headers:
            remaining = int(headers['x-rate-limit-remaining'])
            limit = int(headers.get('x-rate-limit-limit', 300))
            self.rate_limits[platform]['limit'] = limit
            self.rate_limits[platform]['requests'] = limit - remaining
        
        if 'x-rate-limit-reset' in headers:
            reset_time = int(headers['x-rate-limit-reset'])
            self.rate_limits[platform]['reset_time'] = reset_time
    
    async def upload_media(self, 
                          file_path: str, 
                          upload_url: str, 
                          headers: Optional[Dict] = None,
                          platform: str = 'general') -> Optional[Dict]:
        """
        Upload media file to API endpoint
        
        Args:
            file_path: Path to file to upload
            upload_url: Upload endpoint URL
            headers: Request headers
            platform: Platform for rate limiting
            
        Returns:
            Upload response or None if upload fails
        """
        try:
            if not await self._check_rate_limit(platform):
                logger.warning(f"Rate limit exceeded for {platform}")
                return None
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Prepare file upload
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('media', file, filename=file_path)
                
                async with self.session.post(
                    upload_url,
                    data=data,
                    headers=headers
                ) as response:
                    
                    self._update_rate_limit(platform, response.headers)
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Media upload failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            return None
    
    def get_rate_limit_status(self, platform: str) -> Dict:
        """
        Get current rate limit status for platform
        
        Args:
            platform: Platform to check
            
        Returns:
            Rate limit status dictionary
        """
        if platform not in self.rate_limits:
            return {'error': 'Platform not found'}
        
        rate_info = self.rate_limits[platform]
        import time
        
        return {
            'platform': platform,
            'requests_made': rate_info['requests'],
            'limit': rate_info['limit'],
            'remaining': rate_info['limit'] - rate_info['requests'],
            'reset_time': rate_info['reset_time'],
            'time_until_reset': max(0, rate_info['reset_time'] - time.time())
        }
    
    async def wait_for_rate_limit_reset(self, platform: str):
        """
        Wait for rate limit to reset
        
        Args:
            platform: Platform to wait for
        """
        status = self.get_rate_limit_status(platform)
        wait_time = status.get('time_until_reset', 0)
        
        if wait_time > 0:
            logger.info(f"Waiting {wait_time:.0f} seconds for {platform} rate limit reset")
            await asyncio.sleep(wait_time)


class RetryManager:
    """Manages retry logic for API calls"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def retry_with_backoff(self, func, *args, **kwargs):
        """
        Retry function with exponential backoff
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                if result is not None:
                    return result
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
                    return None
        
        return None


class WebhookManager:
    """Manages webhook endpoints for real-time updates"""
    
    def __init__(self):
        self.webhooks = {}
    
    def register_webhook(self, platform: str, url: str, secret: str):
        """
        Register webhook for platform
        
        Args:
            platform: Platform name
            url: Webhook URL
            secret: Webhook secret for verification
        """
        self.webhooks[platform] = {
            'url': url,
            'secret': secret,
            'active': True
        }
        logger.info(f"Webhook registered for {platform}: {url}")
    
    def verify_webhook_signature(self, platform: str, payload: str, signature: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            platform: Platform name
            payload: Webhook payload
            signature: Provided signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        
        if platform not in self.webhooks:
            return False
        
        secret = self.webhooks[platform]['secret']
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def process_webhook(self, platform: str, payload: Dict) -> bool:
        """
        Process incoming webhook
        
        Args:
            platform: Platform name
            payload: Webhook payload
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(f"Processing webhook from {platform}")
            
            # Platform-specific webhook processing
            if platform == 'twitter':
                return await self._process_twitter_webhook(payload)
            elif platform == 'linkedin':
                return await self._process_linkedin_webhook(payload)
            else:
                logger.warning(f"Unknown webhook platform: {platform}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return False
    
    async def _process_twitter_webhook(self, payload: Dict) -> bool:
        """Process Twitter webhook"""
        # Implement Twitter-specific webhook processing
        logger.info("Processing Twitter webhook")
        return True
    
    async def _process_linkedin_webhook(self, payload: Dict) -> bool:
        """Process LinkedIn webhook"""
        # Implement LinkedIn-specific webhook processing
        logger.info("Processing LinkedIn webhook")
        return True
