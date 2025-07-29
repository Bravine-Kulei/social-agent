"""
Simplified runner for the Instagram-to-Social Media Agent System
This version works with the currently installed dependencies
"""
import asyncio
import argparse
import sys
from typing import List
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

async def run_demo_workflow(target_users: List[str], 
                           platforms: List[str] = ['twitter', 'linkedin'],
                           schedule_posts: bool = False):
    """
    Run a demo version of the Instagram-to-Social Media workflow
    """
    try:
        logger.info("🚀 Starting Instagram-to-Social Media Agent System")
        logger.info(f"📸 Target users: {target_users}")
        logger.info(f"📱 Target platforms: {platforms}")
        
        # Simulate workflow steps
        logger.info("📥 Step 1: Extracting Instagram content...")
        await asyncio.sleep(2)  # Simulate processing time
        
        logger.info("🧠 Step 2: Analyzing content with AI...")
        await asyncio.sleep(3)
        
        logger.info("✨ Step 3: Transforming content for platforms...")
        await asyncio.sleep(2)
        
        if schedule_posts:
            logger.info("📅 Step 4: Scheduling posts...")
            await asyncio.sleep(1)
            logger.success("✅ Posts scheduled successfully!")
        else:
            logger.info("📤 Step 4: Publishing to social media...")
            await asyncio.sleep(2)
            logger.success("✅ Content published successfully!")
        
        # Display demo results
        print_demo_results(target_users, platforms, schedule_posts)
        
        logger.success("🎉 Workflow completed successfully!")
        return {
            'status': 'success',
            'users_processed': len(target_users),
            'platforms': platforms,
            'scheduled': schedule_posts
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}")
        return None

def print_demo_results(users: List[str], platforms: List[str], scheduled: bool):
    """Print demo workflow results"""
    print("\n" + "="*60)
    print("🎯 DEMO WORKFLOW RESULTS")
    print("="*60)
    
    print(f"📸 Users Processed: {len(users)}")
    for user in users:
        print(f"   • @{user}")
    
    print(f"📱 Target Platforms: {', '.join(platforms)}")
    print(f"📅 Scheduling: {'Enabled' if scheduled else 'Immediate posting'}")
    
    # Simulate metrics
    print(f"🎬 Videos Extracted: {len(users) * 3}")  # 3 videos per user
    print(f"✨ Content Transformations: {len(users) * len(platforms) * 3}")
    
    if not scheduled:
        print(f"📤 Posts Published:")
        for platform in platforms:
            success_rate = 95  # Demo success rate
            total_posts = len(users) * 3
            successful = int(total_posts * success_rate / 100)
            print(f"   • {platform.title()}: {successful}/{total_posts} ({success_rate}%)")
    
    print("\n💡 This is a demo. Install full dependencies for actual processing:")
    print("   pip install -r requirements.txt")
    print("="*60)

async def run_single_user_demo(username: str, platforms: List[str] = ['twitter', 'linkedin']):
    """Run demo workflow for a single Instagram user"""
    return await run_demo_workflow([username], platforms)

def start_web_interface():
    """Start the web interface"""
    try:
        import uvicorn
        from simple_web import app
        
        logger.info("🌐 Starting web interface...")
        logger.info("📱 Access your dashboard at: http://localhost:8000")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError as e:
        logger.error(f"❌ Missing dependencies for web interface: {e}")
        logger.info("💡 Install with: pip install fastapi uvicorn")
    except Exception as e:
        logger.error(f"❌ Failed to start web interface: {e}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Instagram-to-Social Media Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_system.py --users username1 username2
  python run_system.py --single-user username --platforms twitter
  python run_system.py --web
  python run_system.py --demo
        """
    )
    
    parser.add_argument('--users', nargs='+', help='Instagram usernames to process')
    parser.add_argument('--platforms', nargs='+', default=['twitter', 'linkedin'], 
                       choices=['twitter', 'linkedin'], help='Target platforms')
    parser.add_argument('--schedule', action='store_true', help='Schedule posts instead of posting immediately')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--single-user', help='Process single Instagram user')
    parser.add_argument('--demo', action='store_true', help='Run demo with sample users')
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*60)
    print("🤖 INSTAGRAM-TO-SOCIAL MEDIA AGENT SYSTEM")
    print("="*60)
    print("🎯 Transform Instagram videos into engaging social media content")
    print("🚀 AI-powered multi-agent system with CrewAI")
    print("📱 Supports Twitter and LinkedIn optimization")
    print("="*60)
    
    if args.web:
        # Start web interface
        start_web_interface()
        
    elif args.demo:
        # Run demo with sample users
        sample_users = ['tech_creator', 'lifestyle_blogger', 'fitness_guru']
        logger.info("🎭 Running demo with sample users...")
        asyncio.run(run_demo_workflow(sample_users, args.platforms, args.schedule))
        
    elif args.single_user:
        # Process single user
        logger.info(f"👤 Processing single user: @{args.single_user}")
        asyncio.run(run_single_user_demo(args.single_user, args.platforms))
        
    elif args.users:
        # Process specified users
        logger.info(f"👥 Processing {len(args.users)} users...")
        asyncio.run(run_demo_workflow(args.users, args.platforms, args.schedule))
        
    else:
        # Show help and run demo
        parser.print_help()
        print("\n💡 No arguments provided. Running demo...")
        sample_users = ['demo_user1', 'demo_user2']
        asyncio.run(run_demo_workflow(sample_users, args.platforms, args.schedule))

if __name__ == "__main__":
    main()
