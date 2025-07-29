"""
Complete Instagram-to-Twitter Pipeline
Real Instagram extraction → AI transformation → Twitter posting
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

# Import our custom extractors
from real_instagram_extractor import RealInstagramExtractor

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

class AIContentTransformer:
    """Transform Instagram content for Twitter using AI"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if self.openai_key:
            openai.api_key = self.openai_key
            logger.info("✅ OpenAI API initialized for content transformation")
        else:
            logger.warning("⚠️ No OpenAI API key - using rule-based transformation")
    
    async def transform_for_twitter(self, instagram_post: Dict) -> str:
        """Transform Instagram content for Twitter"""
        try:
            original_caption = instagram_post.get('caption', '')
            likes = instagram_post.get('likes', 0)
            comments = instagram_post.get('comments', 0)
            hashtags = instagram_post.get('hashtags', [])
            
            logger.info(f"🧠 Transforming content for Twitter...")
            logger.info(f"📝 Original: {original_caption[:80]}...")
            
            if self.openai_key and len(original_caption) > 20:
                # Use AI transformation
                transformed = await self._ai_transform(original_caption, likes, comments, hashtags)
            else:
                # Use rule-based transformation
                transformed = self._rule_based_transform(original_caption, likes, comments, hashtags)
            
            logger.success(f"✨ Transformed: {transformed[:80]}...")
            return transformed
            
        except Exception as e:
            logger.error(f"❌ Content transformation failed: {e}")
            return self._fallback_transform(instagram_post)
    
    async def _ai_transform(self, caption: str, likes: int, comments: int, hashtags: List[str]) -> str:
        """AI-powered content transformation using OpenAI"""
        try:
            prompt = f"""
Transform this Instagram video caption into an engaging Twitter post:

Original Caption: "{caption}"
Engagement: {likes} likes, {comments} comments
Original Hashtags: {', '.join(hashtags)}

Requirements:
- Keep it under 280 characters
- Make it Twitter-friendly and engaging
- Add 1-2 relevant emojis
- Include a call to action or question
- Maintain the core message
- Make it more conversational
- Add 1-2 relevant hashtags (not more)
- If the content has high engagement, mention it

Twitter Post:"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            transformed = response.choices[0].message.content.strip()
            
            # Remove quotes if AI added them
            if transformed.startswith('"') and transformed.endswith('"'):
                transformed = transformed[1:-1]
            
            # Ensure it's under 280 characters
            if len(transformed) > 280:
                transformed = transformed[:277] + "..."
            
            return transformed
            
        except Exception as e:
            logger.error(f"❌ AI transformation failed: {e}")
            return self._rule_based_transform(caption, likes, comments, hashtags)
    
    def _rule_based_transform(self, caption: str, likes: int, comments: int, hashtags: List[str]) -> str:
        """Rule-based content transformation"""
        # Extract main content (first sentence or first 100 chars)
        sentences = caption.split('.')
        main_content = sentences[0] if sentences else caption
        
        # Limit words
        words = main_content.split()[:25]
        transformed = " ".join(words)
        
        # Add engagement boost if high engagement
        if likes > 1000:
            transformed += f" 🔥 ({likes:,} likes!)"
        elif likes > 500:
            transformed += " 🚀"
        
        # Add 1-2 hashtags
        relevant_hashtags = hashtags[:2] if hashtags else ['#AI', '#Innovation']
        transformed += " " + " ".join(relevant_hashtags)
        
        # Ensure Twitter length
        if len(transformed) > 280:
            transformed = transformed[:277] + "..."
        
        return transformed
    
    def _fallback_transform(self, post: Dict) -> str:
        """Fallback transformation when everything else fails"""
        caption = post.get('caption', 'Check out this amazing content!')
        likes = post.get('likes', 0)
        
        # Simple fallback
        words = caption.split()[:20]
        content = " ".join(words)
        
        if likes > 1000:
            content += f" 🔥 ({likes:,} likes!)"
        
        content += " #AI #SocialMedia"
        
        return content[:280]

class TwitterPublisher:
    """Publish content to Twitter"""
    
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
    
    async def publish_tweet(self, content: str, source_post: Dict = None) -> Dict:
        """Publish content to Twitter"""
        try:
            logger.info("🐦 Publishing to Twitter...")
            
            # Add source attribution
            if source_post:
                shortcode = source_post.get('shortcode', 'unknown')
                content += f"\n\n📸 From IG: {shortcode}"
            
            # Final length check
            if len(content) > 280:
                content = content[:277] + "..."
            
            response = self.client.create_tweet(text=content)
            
            post_url = f"https://twitter.com/user/status/{response.data['id']}"
            logger.success(f"✅ Published to Twitter: {response.data['id']}")
            logger.info(f"🔗 View tweet: {post_url}")
            
            return {
                'success': True,
                'post_id': response.data['id'],
                'url': post_url,
                'content': content,
                'platform': 'twitter'
            }
            
        except Exception as e:
            logger.error(f"❌ Twitter publishing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'twitter'
            }

async def run_complete_pipeline(instagram_username: str, max_videos: int = 2):
    """Run the complete Instagram-to-Twitter pipeline"""
    
    print("\n" + "="*80)
    print("🚀 COMPLETE INSTAGRAM-TO-TWITTER PIPELINE")
    print("="*80)
    print("📸 Real Instagram Extraction → 🧠 AI Transformation → 🐦 Twitter Publishing")
    print("="*80)
    
    logger.info(f"🎯 Starting complete pipeline for @{instagram_username}")
    
    results = {
        'instagram_user': instagram_username,
        'videos_extracted': 0,
        'posts_created': 0,
        'successful_posts': 0,
        'failed_posts': 0,
        'post_details': []
    }
    
    try:
        # Step 1: Extract Instagram content
        logger.info("📥 Step 1: Extracting Instagram videos...")
        extractor = RealInstagramExtractor()
        videos = await extractor.extract_user_videos(instagram_username, max_videos)
        
        if not videos:
            logger.warning(f"⚠️ No videos found for @{instagram_username}")
            return results
        
        results['videos_extracted'] = len(videos)
        
        # Step 2: Initialize AI transformer and Twitter publisher
        logger.info("🧠 Step 2: Initializing AI content transformer...")
        transformer = AIContentTransformer()
        
        logger.info("🐦 Step 3: Initializing Twitter publisher...")
        publisher = TwitterPublisher()
        
        # Step 4: Process each video
        for i, video in enumerate(videos, 1):
            logger.info(f"🎬 Processing video {i}/{len(videos)}: {video['shortcode']}")
            
            # Transform content for Twitter
            transformed_content = await transformer.transform_for_twitter(video)
            
            # Publish to Twitter
            publish_result = await publisher.publish_tweet(transformed_content, video)
            
            results['posts_created'] += 1
            
            if publish_result['success']:
                results['successful_posts'] += 1
                logger.success(f"✅ Successfully published video {i} to Twitter")
            else:
                results['failed_posts'] += 1
                logger.error(f"❌ Failed to publish video {i} to Twitter")
            
            # Store details
            results['post_details'].append({
                'video_shortcode': video['shortcode'],
                'original_caption': video['caption'][:150] + "..." if len(video['caption']) > 150 else video['caption'],
                'original_stats': f"{video['likes']:,} likes, {video['comments']:,} comments",
                'transformed_content': transformed_content,
                'publish_result': publish_result
            })
            
            # Rate limiting delay
            if i < len(videos):  # Don't wait after the last video
                logger.info("⏳ Waiting 5 seconds for rate limiting...")
                await asyncio.sleep(5)
        
        # Print final results
        print_pipeline_results(results)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Complete pipeline failed: {e}")
        return results

def print_pipeline_results(results: Dict[str, Any]):
    """Print complete pipeline results"""
    print("\n" + "="*80)
    print("🎯 COMPLETE PIPELINE RESULTS")
    print("="*80)
    
    print(f"📸 Instagram User: @{results['instagram_user']}")
    print(f"🎬 Videos Extracted: {results['videos_extracted']}")
    print(f"📤 Posts Created: {results['posts_created']}")
    print(f"✅ Successful Posts: {results['successful_posts']}")
    print(f"❌ Failed Posts: {results['failed_posts']}")
    
    if results['posts_created'] > 0:
        success_rate = (results['successful_posts'] / results['posts_created']) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n📱 Content Transformation & Publishing Details:")
    for i, detail in enumerate(results['post_details'], 1):
        print(f"\n   🎬 Video {i}: {detail['video_shortcode']} ({detail['original_stats']})")
        print(f"   📝 Original: {detail['original_caption']}")
        print(f"   ✨ Transformed: {detail['transformed_content']}")
        
        if detail['publish_result']['success']:
            print(f"   ✅ Published: {detail['publish_result']['url']}")
        else:
            print(f"   ❌ Failed: {detail['publish_result']['error']}")
    
    if results['successful_posts'] > 0:
        print(f"\n🎉 SUCCESS! {results['successful_posts']} Instagram videos transformed and published to Twitter!")
        print("🔗 Check your Twitter account to see the posts!")
        print("\n💡 Complete Pipeline Features Demonstrated:")
        print("   • Real Instagram content extraction")
        print("   • AI-powered content transformation")
        print("   • Platform-specific optimization")
        print("   • Real Twitter publishing")
        print("   • Comprehensive error handling")
        print("   • Rate limiting compliance")
        print("   • Detailed logging and monitoring")
    
    print("="*80)

async def main():
    """Main entry point"""
    
    # Get target username
    target_username = "edhonour"  # Default from your .env
    
    print(f"\n🎯 Target Instagram User: @{target_username}")
    print("⚠️  This will extract real Instagram content and post to your Twitter!")
    
    confirm = input("🔥 Continue with complete pipeline? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("❌ Pipeline cancelled.")
        return
    
    logger.info("🚀 Starting complete Instagram-to-Twitter pipeline...")
    
    try:
        results = await run_complete_pipeline(target_username, max_videos=2)
        
        if results['successful_posts'] > 0:
            logger.success(f"🎉 Pipeline completed! {results['successful_posts']} posts published successfully!")
        else:
            logger.warning("⚠️ Pipeline completed but no posts were published successfully.")
            
    except Exception as e:
        logger.error(f"❌ Complete pipeline failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
