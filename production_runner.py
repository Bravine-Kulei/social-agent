"""
Production Instagram-to-Social Media Agent System
This version uses real API keys and posts to actual social media accounts
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from loguru import logger
from dotenv import load_dotenv
import tweepy
import requests
import instaloader
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

class InstagramScraper:
    """Real Instagram content scraper"""
    
    def __init__(self):
        self.loader = instaloader.Instaloader()
        
    async def extract_user_content(self, username: str, max_videos: int = 3) -> List[Dict]:
        """Extract recent videos from Instagram user"""
        try:
            logger.info(f"📸 Extracting content from @{username}...")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            videos = []
            count = 0
            
            for post in profile.get_posts():
                if count >= max_videos:
                    break
                    
                if post.is_video:
                    video_data = {
                        'url': post.video_url,
                        'caption': post.caption or "",
                        'likes': post.likes,
                        'comments': post.comments,
                        'date': post.date,
                        'shortcode': post.shortcode
                    }
                    videos.append(video_data)
                    count += 1
                    logger.info(f"✅ Found video: {post.shortcode} ({post.likes} likes)")
            
            logger.success(f"📥 Extracted {len(videos)} videos from @{username}")
            return videos
            
        except Exception as e:
            logger.error(f"❌ Failed to extract from @{username}: {str(e)}")
            return []

class TwitterPoster:
    """Real Twitter API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials")
        
        # Initialize Twitter API v2
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
    async def post_content(self, content: str, video_url: str = None) -> Dict:
        """Post content to Twitter"""
        try:
            logger.info("🐦 Posting to Twitter...")
            
            # Optimize content for Twitter (280 chars)
            optimized_content = self.optimize_for_twitter(content)
            
            # Post tweet
            response = self.client.create_tweet(text=optimized_content)
            
            logger.success(f"✅ Posted to Twitter: {response.data['id']}")
            return {
                'platform': 'twitter',
                'success': True,
                'post_id': response.data['id'],
                'content': optimized_content
            }
            
        except Exception as e:
            logger.error(f"❌ Twitter posting failed: {str(e)}")
            return {
                'platform': 'twitter',
                'success': False,
                'error': str(e)
            }
    
    def optimize_for_twitter(self, content: str) -> str:
        """Optimize content for Twitter's 280 character limit"""
        if len(content) <= 280:
            return content
        
        # Truncate and add ellipsis
        return content[:277] + "..."

class LinkedInPoster:
    """Real LinkedIn API integration"""
    
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        
        if not self.access_token:
            raise ValueError("Missing LinkedIn access token")
    
    async def post_content(self, content: str, video_url: str = None) -> Dict:
        """Post content to LinkedIn"""
        try:
            logger.info("💼 Posting to LinkedIn...")
            
            # Get user profile ID
            profile_url = "https://api.linkedin.com/v2/people/~"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            profile_response = requests.get(profile_url, headers=headers)
            if profile_response.status_code != 200:
                raise Exception(f"Failed to get LinkedIn profile: {profile_response.text}")
            
            profile_id = profile_response.json()['id']
            
            # Optimize content for LinkedIn
            optimized_content = self.optimize_for_linkedin(content)
            
            # Create post
            post_data = {
                "author": f"urn:li:person:{profile_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": optimized_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            post_url = "https://api.linkedin.com/v2/ugcPosts"
            response = requests.post(post_url, headers=headers, json=post_data)
            
            if response.status_code == 201:
                post_id = response.json()['id']
                logger.success(f"✅ Posted to LinkedIn: {post_id}")
                return {
                    'platform': 'linkedin',
                    'success': True,
                    'post_id': post_id,
                    'content': optimized_content
                }
            else:
                raise Exception(f"LinkedIn API error: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ LinkedIn posting failed: {str(e)}")
            return {
                'platform': 'linkedin',
                'success': False,
                'error': str(e)
            }
    
    def optimize_for_linkedin(self, content: str) -> str:
        """Optimize content for LinkedIn (professional tone)"""
        # Add professional context if needed
        if not any(word in content.lower() for word in ['professional', 'business', 'career', 'industry']):
            content = f"Professional insight: {content}"
        
        return content[:3000]  # LinkedIn limit

class ContentTransformer:
    """AI-powered content transformation"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
    async def transform_for_platform(self, original_content: str, platform: str) -> str:
        """Transform content for specific platform using AI"""
        try:
            if platform == 'twitter':
                return self.transform_for_twitter(original_content)
            elif platform == 'linkedin':
                return self.transform_for_linkedin(original_content)
            else:
                return original_content
                
        except Exception as e:
            logger.error(f"❌ Content transformation failed: {str(e)}")
            return original_content
    
    def transform_for_twitter(self, content: str) -> str:
        """Transform content for Twitter (casual, engaging)"""
        # Simple transformation for demo
        words = content.split()[:30]  # Limit words
        transformed = " ".join(words)
        
        # Add engaging elements
        if not any(char in transformed for char in ['!', '?', '🔥', '💯']):
            transformed += " 🔥"
        
        return transformed
    
    def transform_for_linkedin(self, content: str) -> str:
        """Transform content for LinkedIn (professional)"""
        # Add professional framing
        if not content.startswith(('Excited to share', 'Thrilled to announce', 'Proud to present')):
            content = f"Excited to share: {content}"
        
        # Add call to action
        if not content.endswith(('thoughts?', 'agree?', 'experience?')):
            content += "\n\nWhat are your thoughts?"
        
        return content

async def run_production_workflow(target_users: List[str], 
                                platforms: List[str] = ['twitter', 'linkedin']) -> Dict[str, Any]:
    """Run the production workflow with real API calls"""
    
    logger.info("🚀 Starting PRODUCTION Instagram-to-Social Media Agent System")
    logger.info(f"📸 Target users: {target_users}")
    logger.info(f"📱 Target platforms: {platforms}")
    
    # Initialize components
    scraper = InstagramScraper()
    transformer = ContentTransformer()
    
    # Initialize platform posters
    posters = {}
    if 'twitter' in platforms:
        try:
            posters['twitter'] = TwitterPoster()
            logger.info("✅ Twitter API initialized")
        except Exception as e:
            logger.error(f"❌ Twitter API failed: {e}")
    
    if 'linkedin' in platforms:
        try:
            posters['linkedin'] = LinkedInPoster()
            logger.info("✅ LinkedIn API initialized")
        except Exception as e:
            logger.error(f"❌ LinkedIn API failed: {e}")
    
    results = {
        'users_processed': 0,
        'videos_extracted': 0,
        'posts_created': 0,
        'successful_posts': 0,
        'failed_posts': 0,
        'details': []
    }
    
    # Process each user
    for username in target_users:
        logger.info(f"👤 Processing user: @{username}")
        
        # Extract Instagram content
        videos = await scraper.extract_user_content(username, max_videos=3)
        results['videos_extracted'] += len(videos)
        
        if not videos:
            logger.warning(f"⚠️ No videos found for @{username}")
            continue
        
        # Process each video
        for video in videos:
            original_content = video['caption'][:500]  # Limit content length
            
            logger.info(f"🎬 Processing video: {video['shortcode']}")
            
            # Transform and post to each platform
            for platform in platforms:
                if platform not in posters:
                    continue
                
                try:
                    # Transform content for platform
                    transformed_content = await transformer.transform_for_platform(
                        original_content, platform
                    )
                    
                    # Post to platform
                    post_result = await posters[platform].post_content(
                        transformed_content, video['url']
                    )
                    
                    results['posts_created'] += 1
                    
                    if post_result['success']:
                        results['successful_posts'] += 1
                        logger.success(f"✅ Successfully posted to {platform}")
                    else:
                        results['failed_posts'] += 1
                        logger.error(f"❌ Failed to post to {platform}")
                    
                    results['details'].append(post_result)
                    
                    # Rate limiting delay
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error posting to {platform}: {e}")
                    results['failed_posts'] += 1
        
        results['users_processed'] += 1
        
        # Delay between users
        await asyncio.sleep(5)
    
    # Print final results
    print_production_results(results)
    
    return results

def print_production_results(results: Dict[str, Any]):
    """Print production workflow results"""
    print("\n" + "="*60)
    print("🎯 PRODUCTION WORKFLOW RESULTS")
    print("="*60)
    
    print(f"👥 Users Processed: {results['users_processed']}")
    print(f"🎬 Videos Extracted: {results['videos_extracted']}")
    print(f"📤 Posts Created: {results['posts_created']}")
    print(f"✅ Successful Posts: {results['successful_posts']}")
    print(f"❌ Failed Posts: {results['failed_posts']}")
    
    if results['posts_created'] > 0:
        success_rate = (results['successful_posts'] / results['posts_created']) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n📱 Platform Breakdown:")
    platform_stats = {}
    for detail in results['details']:
        platform = detail['platform']
        if platform not in platform_stats:
            platform_stats[platform] = {'success': 0, 'failed': 0}
        
        if detail['success']:
            platform_stats[platform]['success'] += 1
        else:
            platform_stats[platform]['failed'] += 1
    
    for platform, stats in platform_stats.items():
        total = stats['success'] + stats['failed']
        rate = (stats['success'] / total * 100) if total > 0 else 0
        print(f"   • {platform.title()}: {stats['success']}/{total} ({rate:.1f}%)")
    
    print("="*60)

async def main():
    """Main entry point for production system"""
    
    # Get target users from environment or use default
    target_users_env = os.getenv('TARGET_INSTAGRAM_USERS', 'edhonour')
    target_users = [user.strip() for user in target_users_env.split(',')]
    
    platforms = ['twitter', 'linkedin']
    
    print("\n" + "="*60)
    print("🤖 INSTAGRAM-TO-SOCIAL MEDIA AGENT SYSTEM")
    print("🚀 PRODUCTION MODE - REAL API CALLS")
    print("="*60)
    print("⚠️  WARNING: This will make real posts to your social media accounts!")
    print("="*60)
    
    # Confirm before proceeding
    confirm = input("\n🔥 Continue with REAL posting? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return
    
    logger.info("🚀 Starting production workflow...")
    
    try:
        results = await run_production_workflow(target_users, platforms)
        
        if results['successful_posts'] > 0:
            logger.success(f"🎉 Workflow completed! {results['successful_posts']} posts published successfully!")
        else:
            logger.warning("⚠️ Workflow completed but no posts were published successfully.")
            
    except Exception as e:
        logger.error(f"❌ Production workflow failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
