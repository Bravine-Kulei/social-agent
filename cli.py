"""
Enhanced CLI for Instagram-to-Social Media Agent System
Provides a user-friendly command-line interface
"""
import asyncio
import argparse
import sys
from typing import List
from loguru import logger
from config_helper import check_system_ready
from analytics import analytics
from specific_video_poster import post_specific_video
from complete_pipeline import run_complete_pipeline

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Instagram-to-Social Media Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Post specific Instagram video
  python cli.py post --url https://www.instagram.com/reel/ABC123/
  python cli.py post --shortcode ABC123
  
  # Run complete pipeline for user
  python cli.py pipeline --user edhonour --max-videos 3
  
  # Check system configuration
  python cli.py config --check
  
  # View analytics
  python cli.py analytics --days 30
  
  # Start web interface
  python cli.py web
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Post command
    post_parser = subparsers.add_parser('post', help='Post specific Instagram video')
    post_group = post_parser.add_mutually_exclusive_group(required=True)
    post_group.add_argument('--url', help='Instagram URL')
    post_group.add_argument('--shortcode', help='Instagram shortcode')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete pipeline')
    pipeline_parser.add_argument('--user', required=True, help='Instagram username')
    pipeline_parser.add_argument('--max-videos', type=int, default=3, help='Max videos to process')
    pipeline_parser.add_argument('--platforms', nargs='+', default=['twitter'], 
                                choices=['twitter', 'linkedin'], help='Target platforms')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--check', action='store_true', help='Check configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate all settings')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='View analytics')
    analytics_parser.add_argument('--days', type=int, default=30, help='Days to analyze')
    analytics_parser.add_argument('--export', help='Export to file')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--port', type=int, default=8000, help='Port number')
    web_parser.add_argument('--host', default='localhost', help='Host address')
    
    return parser

async def handle_post_command(args):
    """Handle post command"""
    print("🎯 POSTING SPECIFIC INSTAGRAM VIDEO")
    print("="*50)
    
    if args.url:
        result = await post_specific_video(args.url)
    else:
        result = await post_specific_video(args.shortcode)
    
    if result and result.get('success'):
        print(f"✅ Successfully posted to Twitter!")
        print(f"🔗 URL: {result['url']}")
    else:
        print(f"❌ Failed to post")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")

async def handle_pipeline_command(args):
    """Handle pipeline command"""
    print(f"🚀 RUNNING COMPLETE PIPELINE FOR @{args.user}")
    print("="*50)
    
    results = await run_complete_pipeline(args.user, args.max_videos)
    
    if results['successful_posts'] > 0:
        print(f"✅ Pipeline completed! {results['successful_posts']} posts published")
    else:
        print(f"⚠️ Pipeline completed but no posts were published")

def handle_config_command(args):
    """Handle config command"""
    if args.check or args.validate:
        print("🔧 CHECKING SYSTEM CONFIGURATION")
        print("="*50)
        
        if check_system_ready():
            print("✅ System is ready to run!")
        else:
            print("❌ System configuration needs attention")
            sys.exit(1)

def handle_analytics_command(args):
    """Handle analytics command"""
    print(f"📊 ANALYTICS REPORT - LAST {args.days} DAYS")
    print("="*50)
    
    analytics.print_analytics_report(args.days)
    
    if args.export:
        # Export analytics data
        import json
        metrics = analytics.get_system_metrics(args.days)
        
        export_data = {
            'metrics': {
                'total_posts': metrics.total_posts,
                'successful_posts': metrics.successful_posts,
                'failed_posts': metrics.failed_posts,
                'success_rate': metrics.success_rate,
                'avg_processing_time': metrics.avg_processing_time
            },
            'posts': [
                {
                    'timestamp': post.timestamp,
                    'instagram_user': post.instagram_user,
                    'platform': post.platform,
                    'success': post.success,
                    'instagram_likes': post.instagram_likes
                }
                for post in analytics.posts[-100:]  # Last 100 posts
            ]
        }
        
        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Analytics exported to: {args.export}")

def handle_web_command(args):
    """Handle web command"""
    print(f"🌐 STARTING WEB INTERFACE")
    print("="*50)
    print(f"🔗 Access at: http://{args.host}:{args.port}")
    
    try:
        import uvicorn
        from simple_web import app
        
        uvicorn.run(app, host=args.host, port=args.port)
    except ImportError:
        print("❌ Web interface dependencies not installed")
        print("💡 Install with: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🤖 INSTAGRAM-TO-SOCIAL MEDIA AGENT SYSTEM                ║
║                                                              ║
║    Transform Instagram videos into engaging social posts    ║
║    AI-powered • Multi-platform • Automated                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    print_banner()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'post':
            await handle_post_command(args)
        elif args.command == 'pipeline':
            await handle_pipeline_command(args)
        elif args.command == 'config':
            handle_config_command(args)
        elif args.command == 'analytics':
            handle_analytics_command(args)
        elif args.command == 'web':
            handle_web_command(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
