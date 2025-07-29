"""
Demo Full Pipeline: Simulated Instagram Content → Real Twitter Posts
Demonstrates the complete workflow using sample Instagram-style content
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from loguru import logger
from dotenv import load_dotenv
import tweepy
from datetime import datetime
import openai

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

class MockInstagramExtractor:
    """Simulates Instagram content extraction with realistic data"""
    
    def __init__(self):
        # Sample Instagram-style video content
        self.sample_videos = [
            {
                'shortcode': 'ABC123XYZ',
                'caption': '🚀 Just launched my new AI project! This system automatically transforms content across social media platforms using advanced machine learning. The future of content creation is here! What do you think about AI-powered automation? #AI #MachineLearning #Innovation #TechStartup #Automation',
                'video_url': 'https://example.com/video1.mp4',
                'likes': 2847,
                'comments': 156,
                'date': '2025-01-29 10:30:00',
                'hashtags': ['#AI', '#MachineLearning', '#Innovation', '#TechStartup', '#Automation'],
                'mentions': []
            },
            {
                'shortcode': 'DEF456UVW',
                'caption': '💡 Building something incredible with CrewAI and OpenAI! My latest project uses multiple AI agents working together to create content for different social media platforms. Each agent has a specific role - one extracts content, another transforms it, and the third publishes it. The coordination between agents is mind-blowing! 🤖✨ #CrewAI #OpenAI #MultiAgent #SocialMedia #ContentCreation',
                'video_url': 'https://example.com/video2.mp4',
                'likes': 1923,
                'comments': 89,
                'date': '2025-01-28 15:45:00',
                'hashtags': ['#CrewAI', '#OpenAI', '#MultiAgent', '#SocialMedia', '#ContentCreation'],
                'mentions': []
            },
            {
                'shortcode': 'GHI789RST',
                'caption': '🎯 Demo time! Watch my Instagram-to-Twitter agent in action. It automatically finds trending videos, analyzes the content, and creates platform-specific posts. The AI understands context, audience, and platform requirements. This is the future of social media management! Who else is excited about AI automation? 🔥 #AIAgent #SocialMediaAutomation #TwitterBot #InstagramAPI #TechDemo',
                'video_url': 'https://example.com/video3.mp4',
                'likes': 3156,
                'comments': 234,
                'date': '2025-01-27 09:15:00',
                'hashtags': ['#AIAgent', '#SocialMediaAutomation', '#TwitterBot', '#InstagramAPI', '#TechDemo'],
                'mentions': []
            }
        ]
    
    async def get_user_videos(self, username: str, max_videos: int = 2) -> List[Dict]:
        """Simulate extracting videos from Instagram user"""
        logger.info(f"📸 Simulating extraction from @{username}...")
        logger.info(f"👤 Found profile: {username} (simulated data)")
        
        # Return sample videos (limited by max_videos)
        videos = self.sample_videos[:max_videos]
        
        for i, video in enumerate(videos, 1):
            logger.success(f"✅ Found video {i}: {video['shortcode']} ({video['likes']} likes, {video['comments']} comments)")
        
        logger.success(f"📥 Extracted {len(videos)} videos from @{username}")
        return videos

class ContentTransformer:
    """Transform Instagram content for Twitter using AI"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if self.openai_key:
            openai.api_key = self.openai_key
            logger.info("✅ OpenAI API initialized")
        else:
            logger.warning("⚠️ No OpenAI API key found - using simple transformation")
    
    async def transform_for_twitter(self, instagram_content: Dict) -> str:
        """Transform Instagram video content for Twitter"""
        try:
            original_caption = instagram_content['caption']
            video_stats = f"{instagram_content['likes']} likes, {instagram_content['comments']} comments"
            
            logger.info(f"🧠 Transforming content for Twitter...")
            logger.info(f"📝 Original caption: {original_caption[:100]}...")
            
            if self.openai_key:
                # Use AI transformation
                transformed = await self._ai_transform(original_caption, video_stats)
            else:
                # Use simple transformation
                transformed = self._simple_transform(original_caption, instagram_content)
            
            logger.success(f"✨ Transformed content: {transformed[:100]}...")
            return transformed
            
        except Exception as e:
            logger.error(f"❌ Content transformation failed: {e}")
            return self._simple_transform(instagram_content['caption'], instagram_content)
    
    async def _ai_transform(self, caption: str, stats: str) -> str:
        """AI-powered content transformation"""
        try:
            prompt = f"""
Transform this Instagram video caption into an engaging Twitter post:

Original Caption: "{caption}"
Video Stats: {stats}

Requirements:
- Keep it under 280 characters
- Make it engaging and Twitter-friendly
- Add relevant emojis
- Include a call to action or question
- Maintain the original meaning
- Make it more conversational
- Remove excessive hashtags (max 2-3)

Twitter Post:"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            transformed = response.choices[0].message.content.strip()
            
            # Ensure it's under 280 characters
            if len(transformed) > 280:
                transformed = transformed[:277] + "..."
            
            return transformed
            
        except Exception as e:
            logger.error(f"❌ AI transformation failed: {e}")
            return self._simple_transform(caption, {'likes': 0, 'comments': 0})
    
    def _simple_transform(self, caption: str, content: Dict) -> str:
        """Simple rule-based transformation"""
        # Extract main content (remove excessive hashtags)
        lines = caption.split('\n')
        main_content = lines[0] if lines else caption
        
        # Limit words and clean up
        words = main_content.split()[:30]
        transformed = " ".join(words)
        
        # Remove excessive hashtags, keep only 2-3
        hashtags = content.get('hashtags', [])[:2]
        
        # Add engagement elements
        if not any(emoji in transformed for emoji in ['🔥', '💯', '✨', '🚀']):
            transformed += " 🚀"
        
        # Add stats if impressive
        likes = content.get('likes', 0)
        if likes > 1000:
            transformed += f" ({likes} likes!)"
        
        # Add hashtags
        if hashtags:
            transformed += " " + " ".join(hashtags)
        
        # Ensure Twitter length
        if len(transformed) > 280:
            transformed = transformed[:277] + "..."
        
        return transformed

class TwitterPoster:
    """Post content to Twitter"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials")
        
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        logger.info("✅ Twitter API initialized")
    
    async def post_tweet(self, content: str, source_info: Dict = None) -> Dict:
        """Post content to Twitter"""
        try:
            logger.info("🐦 Posting to Twitter...")
            
            # Add source attribution
            if source_info:
                shortcode = source_info.get('shortcode', 'unknown')
                content += f"\n\n📸 From Instagram video: {shortcode}"
            
            # Ensure final length check
            if len(content) > 280:
                content = content[:277] + "..."
            
            response = self.client.create_tweet(text=content)
            
            post_url = f"https://twitter.com/user/status/{response.data['id']}"
            logger.success(f"✅ Posted to Twitter: {response.data['id']}")
            logger.info(f"🔗 View post: {post_url}")
            
            return {
                'success': True,
                'post_id': response.data['id'],
                'url': post_url,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"❌ Twitter posting failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

async def run_demo_pipeline(instagram_username: str, max_videos: int = 2):
    """Run the complete demo pipeline"""
    
    logger.info("🚀 Starting Demo Pipeline: Instagram-style Content → Twitter")
    logger.info(f"📸 Simulating content from @{instagram_username}")
    
    results = {
        'instagram_user': instagram_username,
        'videos_found': 0,
        'posts_created': 0,
        'successful_posts': 0,
        'failed_posts': 0,
        'post_details': []
    }
    
    try:
        # Step 1: Extract Instagram content (simulated)
        logger.info("📥 Step 1: Extracting Instagram videos (simulated)...")
        extractor = MockInstagramExtractor()
        videos = await extractor.get_user_videos(instagram_username, max_videos)
        
        results['videos_found'] = len(videos)
        
        # Step 2: Initialize content transformer and Twitter poster
        logger.info("🧠 Step 2: Initializing AI transformer...")
        transformer = ContentTransformer()
        
        logger.info("🐦 Step 3: Initializing Twitter poster...")
        twitter = TwitterPoster()
        
        # Step 3: Process each video
        for i, video in enumerate(videos, 1):
            logger.info(f"🎬 Processing video {i}/{len(videos)}: {video['shortcode']}")
            
            # Transform content
            transformed_content = await transformer.transform_for_twitter(video)
            
            # Post to Twitter
            post_result = await twitter.post_tweet(transformed_content, video)
            
            results['posts_created'] += 1
            
            if post_result['success']:
                results['successful_posts'] += 1
                logger.success(f"✅ Successfully posted video {i} to Twitter")
            else:
                results['failed_posts'] += 1
                logger.error(f"❌ Failed to post video {i} to Twitter")
            
            results['post_details'].append({
                'video_shortcode': video['shortcode'],
                'original_caption': video['caption'][:150] + "..." if len(video['caption']) > 150 else video['caption'],
                'transformed_content': transformed_content,
                'post_result': post_result,
                'video_stats': f"{video['likes']} likes, {video['comments']} comments"
            })
            
            # Rate limiting delay
            await asyncio.sleep(5)
        
        # Print results
        print_pipeline_results(results)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return results

def print_pipeline_results(results: Dict[str, Any]):
    """Print pipeline results"""
    print("\n" + "="*80)
    print("🎯 DEMO PIPELINE RESULTS: INSTAGRAM-STYLE CONTENT → TWITTER")
    print("="*80)
    
    print(f"📸 Instagram User: @{results['instagram_user']} (simulated)")
    print(f"🎬 Videos Found: {results['videos_found']}")
    print(f"📤 Posts Created: {results['posts_created']}")
    print(f"✅ Successful Posts: {results['successful_posts']}")
    print(f"❌ Failed Posts: {results['failed_posts']}")
    
    if results['posts_created'] > 0:
        success_rate = (results['successful_posts'] / results['posts_created']) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n📱 Transformation Details:")
    for i, detail in enumerate(results['post_details'], 1):
        print(f"\n   🎬 Video {i}: {detail['video_shortcode']} ({detail['video_stats']})")
        print(f"   📝 Original: {detail['original_caption']}")
        print(f"   ✨ Transformed: {detail['transformed_content']}")
        
        if detail['post_result']['success']:
            print(f"   ✅ Posted: {detail['post_result']['url']}")
        else:
            print(f"   ❌ Failed: {detail['post_result']['error']}")
    
    if results['successful_posts'] > 0:
        print(f"\n🎉 SUCCESS! {results['successful_posts']} Instagram-style videos transformed and posted to Twitter!")
        print("🔗 Check your Twitter account to see the real posts!")
        print("📸 This demonstrates the complete pipeline working end-to-end!")
    
    print("="*80)

async def main():
    """Main entry point"""
    
    print("\n" + "="*80)
    print("🤖 INSTAGRAM-TO-TWITTER DEMO PIPELINE")
    print("="*80)
    print("📸 Simulated Instagram Content → 🧠 AI Transform → 🐦 Real Twitter Posts")
    print("💡 This demo shows the complete workflow with realistic Instagram-style content")
    print("="*80)
    
    username = "edhonour"  # Demo username
    
    print(f"\n📸 Using simulated Instagram content from @{username}")
    print("🐦 Will post REAL tweets to your Twitter account!")
    confirm = input("🔥 Continue with demo pipeline? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Demo cancelled.")
        return
    
    logger.info("🚀 Starting demo pipeline...")
    
    try:
        results = await run_demo_pipeline(username, max_videos=2)
        
        if results['successful_posts'] > 0:
            logger.success(f"🎉 Demo completed! {results['successful_posts']} real posts published!")
        else:
            logger.warning("⚠️ Demo completed but no posts were published successfully.")
            
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
