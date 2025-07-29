"""
Full Pipeline Test: Instagram Video → Twitter Post
Tests the complete workflow from Instagram extraction to Twitter posting
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from loguru import logger
from dotenv import load_dotenv
import tweepy
import instaloader
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

class InstagramExtractor:
    """Extract content from Instagram users"""
    
    def __init__(self):
        self.loader = instaloader.Instaloader()
        # Optional: Login for better access
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if username and password:
            try:
                self.loader.login(username, password)
                logger.info("✅ Logged into Instagram")
            except Exception as e:
                logger.warning(f"⚠️ Instagram login failed: {e}")
                logger.info("📝 Continuing without login (public posts only)")
    
    async def get_user_videos(self, username: str, max_videos: int = 2) -> List[Dict]:
        """Extract recent videos from Instagram user"""
        try:
            logger.info(f"📸 Extracting videos from @{username}...")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            logger.info(f"👤 Found profile: {profile.full_name} ({profile.followers} followers)")
            
            videos = []
            count = 0
            
            for post in profile.get_posts():
                if count >= max_videos:
                    break
                
                # Look for video posts
                if post.is_video:
                    video_data = {
                        'shortcode': post.shortcode,
                        'caption': post.caption or "",
                        'video_url': post.video_url,
                        'likes': post.likes,
                        'comments': post.comments,
                        'date': post.date.strftime("%Y-%m-%d %H:%M:%S"),
                        'hashtags': post.caption_hashtags if post.caption else [],
                        'mentions': post.caption_mentions if post.caption else []
                    }
                    videos.append(video_data)
                    count += 1
                    logger.success(f"✅ Found video: {post.shortcode} ({post.likes} likes, {post.comments} comments)")
            
            logger.success(f"📥 Extracted {len(videos)} videos from @{username}")
            return videos
            
        except Exception as e:
            logger.error(f"❌ Failed to extract from @{username}: {str(e)}")
            return []

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
        # Clean up caption
        words = caption.split()[:25]  # Limit words
        transformed = " ".join(words)
        
        # Add engagement elements
        if not any(emoji in transformed for emoji in ['🔥', '💯', '✨', '🚀']):
            transformed += " 🔥"
        
        # Add stats if impressive
        likes = content.get('likes', 0)
        if likes > 1000:
            transformed += f" ({likes} likes!)"
        
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
            
            # Add source attribution if provided
            if source_info:
                content += f"\n\n📸 Inspired by Instagram content"
            
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

async def run_full_pipeline(instagram_username: str, max_videos: int = 2):
    """Run the complete Instagram → Twitter pipeline"""
    
    logger.info("🚀 Starting Full Pipeline: Instagram → Twitter")
    logger.info(f"📸 Target Instagram user: @{instagram_username}")
    
    results = {
        'instagram_user': instagram_username,
        'videos_found': 0,
        'posts_created': 0,
        'successful_posts': 0,
        'failed_posts': 0,
        'post_details': []
    }
    
    try:
        # Step 1: Extract Instagram content
        logger.info("📥 Step 1: Extracting Instagram videos...")
        extractor = InstagramExtractor()
        videos = await extractor.get_user_videos(instagram_username, max_videos)
        
        if not videos:
            logger.warning(f"⚠️ No videos found for @{instagram_username}")
            return results
        
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
                'original_caption': video['caption'][:100] + "..." if len(video['caption']) > 100 else video['caption'],
                'transformed_content': transformed_content,
                'post_result': post_result
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
    print("\n" + "="*70)
    print("🎯 FULL PIPELINE RESULTS: INSTAGRAM → TWITTER")
    print("="*70)
    
    print(f"📸 Instagram User: @{results['instagram_user']}")
    print(f"🎬 Videos Found: {results['videos_found']}")
    print(f"📤 Posts Created: {results['posts_created']}")
    print(f"✅ Successful Posts: {results['successful_posts']}")
    print(f"❌ Failed Posts: {results['failed_posts']}")
    
    if results['posts_created'] > 0:
        success_rate = (results['successful_posts'] / results['posts_created']) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n📱 Post Details:")
    for i, detail in enumerate(results['post_details'], 1):
        print(f"\n   🎬 Video {i}: {detail['video_shortcode']}")
        print(f"   📝 Original: {detail['original_caption']}")
        print(f"   ✨ Transformed: {detail['transformed_content']}")
        
        if detail['post_result']['success']:
            print(f"   ✅ Posted: {detail['post_result']['url']}")
        else:
            print(f"   ❌ Failed: {detail['post_result']['error']}")
    
    if results['successful_posts'] > 0:
        print(f"\n🎉 SUCCESS! {results['successful_posts']} Instagram videos transformed and posted to Twitter!")
        print("🔗 Check your Twitter account to see the posts!")
    
    print("="*70)

async def main():
    """Main entry point"""
    
    print("\n" + "="*70)
    print("🤖 INSTAGRAM-TO-TWITTER FULL PIPELINE TEST")
    print("="*70)
    print("📸 Extract Instagram videos → 🧠 AI Transform → 🐦 Post to Twitter")
    print("="*70)
    
    # Get Instagram username
    default_user = "edhonour"  # From your .env file
    username = input(f"📸 Enter Instagram username (default: {default_user}): ").strip()
    if not username:
        username = default_user
    
    print(f"\n⚠️  This will extract videos from @{username} and post to your Twitter!")
    confirm = input("🔥 Continue with full pipeline test? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Test cancelled.")
        return
    
    logger.info("🚀 Starting full pipeline test...")
    
    try:
        results = await run_full_pipeline(username, max_videos=2)
        
        if results['successful_posts'] > 0:
            logger.success(f"🎉 Pipeline completed! {results['successful_posts']} posts published!")
        else:
            logger.warning("⚠️ Pipeline completed but no posts were published successfully.")
            
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
