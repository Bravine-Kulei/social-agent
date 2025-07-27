"""
Main entry point for the Instagram-to-Social Media Agent System
"""
import asyncio
import argparse
import sys
from typing import List
from loguru import logger
from agents.orchestrator_agent import OrchestratorAgent
from config import settings

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.log_file,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB"
)

async def run_workflow(target_users: List[str], 
                      platforms: List[str] = ['twitter', 'linkedin'],
                      schedule_posts: bool = False):
    """
    Run the complete Instagram-to-Social Media workflow
    
    Args:
        target_users: List of Instagram usernames to extract from
        platforms: Target platforms for posting
        schedule_posts: Whether to schedule posts or post immediately
    """
    try:
        logger.info("Starting Instagram-to-Social Media Agent System")
        logger.info(f"Target users: {target_users}")
        logger.info(f"Target platforms: {platforms}")
        
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Execute workflow
        results = await orchestrator.execute_full_workflow(
            target_users=target_users,
            platforms=platforms,
            schedule_posts=schedule_posts
        )
        
        # Display results
        print_workflow_results(results)
        
        # Monitor engagement if posts were made
        if not schedule_posts and results.get('posting_results'):
            logger.info("Monitoring engagement metrics...")
            await asyncio.sleep(300)  # Wait 5 minutes
            engagement_data = await orchestrator.monitor_engagement(results)
            print_engagement_results(engagement_data)
        
        logger.info("Workflow completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        return None

def print_workflow_results(results: dict):
    """Print workflow results in a formatted way"""
    print("\n" + "="*60)
    print("WORKFLOW RESULTS")
    print("="*60)
    
    # Summary
    summary = results.get('summary', {})
    print(f"Users Processed: {summary.get('total_users_processed', 0)}")
    print(f"Videos Extracted: {summary.get('total_videos_extracted', 0)}")
    print(f"Content Transformations: {summary.get('total_transformations', 0)}")
    
    # Posting results
    posting_summary = summary.get('posting_summary', {})
    for platform, stats in posting_summary.items():
        success_rate = stats.get('success_rate', 0)
        print(f"{platform.title()} Posts: {stats.get('successful', 0)}/{stats.get('total', 0)} ({success_rate:.1f}%)")
    
    # Errors
    errors = results.get('errors', [])
    if errors:
        print(f"\nErrors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    
    print("="*60)

def print_engagement_results(engagement_data: dict):
    """Print engagement metrics"""
    print("\n" + "="*60)
    print("ENGAGEMENT METRICS")
    print("="*60)
    
    for platform, metrics in engagement_data.items():
        print(f"\n{platform.title()}:")
        for post_id, stats in metrics.items():
            if platform == 'twitter':
                print(f"  Tweet {post_id}: {stats.get('like_count', 0)} likes, {stats.get('retweet_count', 0)} retweets")
            elif platform == 'linkedin':
                print(f"  Post {post_id}: {stats.get('likes', 0)} likes, {stats.get('shares', 0)} shares")
    
    print("="*60)

async def run_single_user(username: str, platforms: List[str] = ['twitter', 'linkedin']):
    """Run workflow for a single Instagram user"""
    return await run_workflow([username], platforms)

async def run_scheduled_workflow():
    """Run workflow with scheduled posting"""
    target_users = settings.target_instagram_users
    return await run_workflow(target_users, schedule_posts=True)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Instagram-to-Social Media Agent System")
    parser.add_argument('--users', nargs='+', help='Instagram usernames to process')
    parser.add_argument('--platforms', nargs='+', default=['twitter', 'linkedin'], 
                       choices=['twitter', 'linkedin'], help='Target platforms')
    parser.add_argument('--schedule', action='store_true', help='Schedule posts instead of posting immediately')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--single-user', help='Process single Instagram user')
    
    args = parser.parse_args()
    
    if args.web:
        # Start web interface
        import uvicorn
        from web_interface import app
        logger.info(f"Starting web interface on {settings.web_host}:{settings.web_port}")
        uvicorn.run(app, host=settings.web_host, port=settings.web_port)
        
    elif args.single_user:
        # Process single user
        asyncio.run(run_single_user(args.single_user, args.platforms))
        
    elif args.users:
        # Process specified users
        asyncio.run(run_workflow(args.users, args.platforms, args.schedule))
        
    else:
        # Use default users from config
        target_users = settings.target_instagram_users
        if not target_users:
            logger.error("No target users specified. Use --users or set TARGET_INSTAGRAM_USERS in config")
            sys.exit(1)
        
        asyncio.run(run_workflow(target_users, args.platforms, args.schedule))

if __name__ == "__main__":
    main()
