"""
Test the new clean Twitter format
"""
import asyncio
from specific_video_poster import TwitterPublisher

async def test_clean_format():
    """Test the updated clean format"""
    
    # Sample video data (like the one you just posted)
    sample_video = {
        'shortcode': 'DMlkZQuyQzi',
        'caption': 'Every software engineer should be able to talk effectively about prompting, vibe coding, MCP servers, retrieval augmented generation, and supervise fine-tuning. These are the core skills that separate good engineers from great ones in the AI era.',
        'likes': 2527,
        'comments': 20,
        'hashtags': ['#AI', '#Innovation', '#SoftwareEngineering'],
        'owner_username': 'edhonour'
    }
    
    print("🧪 TESTING NEW CLEAN FORMAT")
    print("="*50)
    
    # Initialize publisher
    publisher = TwitterPublisher()
    
    # Test the optimization
    optimized_content = publisher.optimize_for_twitter(
        sample_video['caption'],
        sample_video['likes'],
        sample_video['comments'],
        sample_video['hashtags']
    )
    
    # Add @idxcodehub tag and attribution
    final_content = optimized_content + f"\n\n@idxcodehub 📸 {sample_video['shortcode']}"
    
    print("📝 BEFORE (Old Format):")
    print("Every software engineer should be able to talk effectively about prompting, vibe coding, MCP servers, retrieval augmented generation, and supervise fine-tuning 🔥 (2,527 likes!) #AI #Innovation")
    print("\n📸 DMlkZQuyQzi")
    
    print("\n" + "="*50)
    
    print("✨ AFTER (New Clean Format):")
    print(final_content)
    
    print("\n" + "="*50)
    print("🎯 CHANGES MADE:")
    print("✅ Removed likes count (2,527 likes!)")
    print("✅ Removed hashtags (#AI #Innovation)")
    print("✅ Removed 'From @username:' tag")
    print("✅ Added @idxcodehub tag")
    print("✅ Kept only shortcode for attribution")
    print("✅ More space for actual content")
    
    print(f"\n📊 Character count: {len(final_content)}/280")

if __name__ == "__main__":
    asyncio.run(test_clean_format())
