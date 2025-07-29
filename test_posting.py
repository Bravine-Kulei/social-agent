"""
Test Real Social Media Posting
This version uses sample content to test actual posting to Twitter and LinkedIn
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from loguru import logger
from dotenv import load_dotenv
import tweepy
import requests
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
        
    async def post_content(self, content: str) -> Dict:
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
                'content': optimized_content,
                'url': f"https://twitter.com/user/status/{response.data['id']}"
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
    
    async def post_content(self, content: str) -> Dict:
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

async def test_real_posting():
    """Test real posting to social media platforms"""
    
    # Sample content to post (simulating Instagram video content)
    sample_contents = [
        "🚀 Just tested my new AI-powered Instagram-to-Social Media Agent System! It automatically transforms Instagram videos into optimized content for Twitter and LinkedIn. The future of social media automation is here! #AI #SocialMedia #Automation",
        
        "💡 Excited to share my latest project: an intelligent agent system that extracts Instagram content and creates platform-specific posts. Using CrewAI, OpenAI, and multi-platform APIs for seamless content distribution. #TechInnovation #AI #ContentCreation",
        
        "🎯 Building the future of content marketing with AI agents! My new system automatically processes Instagram videos and creates engaging posts for multiple platforms. What do you think about AI-powered content transformation? #AIAgents #Marketing #Innovation"
    ]
    
    logger.info("🚀 Starting REAL Social Media Posting Test")
    logger.info("📱 Testing Twitter and LinkedIn APIs with sample content")
    
    # Initialize platform posters
    posters = {}
    platforms = ['twitter', 'linkedin']
    
    try:
        posters['twitter'] = TwitterPoster()
        logger.info("✅ Twitter API initialized")
    except Exception as e:
        logger.error(f"❌ Twitter API failed: {e}")
        return
    
    try:
        posters['linkedin'] = LinkedInPoster()
        logger.info("✅ LinkedIn API initialized")
    except Exception as e:
        logger.error(f"❌ LinkedIn API failed: {e}")
        return
    
    results = {
        'posts_created': 0,
        'successful_posts': 0,
        'failed_posts': 0,
        'details': []
    }
    
    # Post sample content to test APIs
    for i, content in enumerate(sample_contents[:1], 1):  # Start with just 1 post for testing
        logger.info(f"📝 Testing post {i}: {content[:50]}...")
        
        for platform in platforms:
            if platform not in posters:
                continue
            
            try:
                # Post to platform
                post_result = await posters[platform].post_content(content)
                
                results['posts_created'] += 1
                
                if post_result['success']:
                    results['successful_posts'] += 1
                    logger.success(f"✅ Successfully posted to {platform}")
                    if 'url' in post_result:
                        logger.info(f"🔗 View post: {post_result['url']}")
                else:
                    results['failed_posts'] += 1
                    logger.error(f"❌ Failed to post to {platform}")
                
                results['details'].append(post_result)
                
                # Rate limiting delay
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error posting to {platform}: {e}")
                results['failed_posts'] += 1
        
        # Delay between posts
        await asyncio.sleep(5)
    
    # Print results
    print_test_results(results)
    
    return results

def print_test_results(results: Dict[str, Any]):
    """Print test results"""
    print("\n" + "="*60)
    print("🎯 REAL POSTING TEST RESULTS")
    print("="*60)
    
    print(f"📤 Posts Created: {results['posts_created']}")
    print(f"✅ Successful Posts: {results['successful_posts']}")
    print(f"❌ Failed Posts: {results['failed_posts']}")
    
    if results['posts_created'] > 0:
        success_rate = (results['successful_posts'] / results['posts_created']) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n📱 Platform Results:")
    for detail in results['details']:
        status = "✅ SUCCESS" if detail['success'] else "❌ FAILED"
        platform = detail['platform'].title()
        print(f"   • {platform}: {status}")
        
        if detail['success'] and 'post_id' in detail:
            print(f"     Post ID: {detail['post_id']}")
        elif not detail['success'] and 'error' in detail:
            print(f"     Error: {detail['error']}")
    
    if results['successful_posts'] > 0:
        print(f"\n🎉 SUCCESS! {results['successful_posts']} real posts published!")
        print("🔗 Check your Twitter and LinkedIn accounts to see the posts!")
    
    print("="*60)

async def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("🤖 INSTAGRAM-TO-SOCIAL MEDIA AGENT SYSTEM")
    print("🧪 REAL POSTING TEST")
    print("="*60)
    print("⚠️  WARNING: This will make REAL posts to your social media accounts!")
    print("📝 Using sample content to test the posting functionality")
    print("="*60)
    
    # Confirm before proceeding
    confirm = input("\n🔥 Continue with REAL posting test? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Test cancelled.")
        return
    
    logger.info("🧪 Starting real posting test...")
    
    try:
        results = await test_real_posting()
        
        if results['successful_posts'] > 0:
            logger.success(f"🎉 Test completed! {results['successful_posts']} real posts published!")
            print("\n🔗 Check your social media accounts:")
            print("   • Twitter: https://twitter.com/home")
            print("   • LinkedIn: https://www.linkedin.com/feed/")
        else:
            logger.warning("⚠️ Test completed but no posts were published successfully.")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
