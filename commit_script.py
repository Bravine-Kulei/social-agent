#!/usr/bin/env python3
"""
Script to commit the project in multiple meaningful commits
"""
import subprocess
import time
import random

def run_command(command):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def commit_with_delay(files, message, delay_range=(30, 120)):
    """Make a commit with random delay to simulate natural development"""
    print(f"Adding files: {files}")
    
    # Add files
    for file in files:
        if not run_command(f"git add {file}"):
            print(f"Failed to add {file}")
            return False
    
    # Commit
    print(f"Committing: {message}")
    if not run_command(f'git commit -m "{message}"'):
        print(f"Failed to commit: {message}")
        return False
    
    # Random delay between commits (30-120 seconds)
    delay = random.randint(*delay_range)
    print(f"Waiting {delay} seconds before next commit...\n")
    time.sleep(delay)
    return True

def main():
    """Execute the commit strategy"""

    # Initialize git if not already done
    run_command("git init")

    # Add remote repository
    run_command("git remote add origin https://github.com/Bravine-Kulei/social-agent.git")

    # Fetch to check existing content
    run_command("git fetch origin")
    
    commits = [
        # Phase 1: Project Foundation (skip README as it's already committed)
        ([".gitignore"], "📝 Add comprehensive gitignore for security and clean repository"),
        (["config.py", ".env.example"], "⚙️ Add configuration management and environment template"),
        (["requirements.txt"], "📦 Add project dependencies and requirements"),
        (["agents/__init__.py", "services/__init__.py", "utils/__init__.py"], "🏗️ Create project structure with agent, service, and utility modules"),
        (["main.py"], "🚀 Add main CLI interface and entry point"),
        
        # Phase 2: Core Services
        (["services/instagram_scraper.py"], "📸 Implement Instagram content scraper with video extraction"),
        (["services/content_analyzer.py"], "🧠 Add AI-powered content analysis and video processing"),
        (["services/social_media_poster.py"], "📱 Implement Twitter and LinkedIn posting services"),
        
        # Phase 3: Agent System
        (["agents/instagram_agent.py"], "🤖 Create Instagram extraction agent with CrewAI integration"),
        (["agents/content_transformer_agent.py"], "✨ Add content transformation agent for multi-platform optimization"),
        (["agents/twitter_agent.py"], "🐦 Implement Twitter posting agent with engagement tracking"),
        (["agents/linkedin_agent.py"], "💼 Add LinkedIn publishing agent for professional content"),
        (["agents/orchestrator_agent.py"], "🎯 Create orchestrator agent for workflow coordination"),
        
        # Phase 4: Utilities
        (["utils/video_processor.py"], "🎬 Add comprehensive video processing utilities"),
        (["utils/text_generator.py"], "📝 Implement AI text generation with multiple model support"),
        (["utils/api_clients.py"], "🌐 Add API client management with rate limiting"),
        
        # Phase 5: Web Interface
        (["web_interface.py"], "🖥️ Create web dashboard with FastAPI and real-time monitoring"),
        
        # Phase 6: Final touches
        (["commit_script.py"], "🔧 Add automated commit script for development workflow"),
        (["README.md"], "📚 Enhance documentation with comprehensive usage guide"),
        (["."], "🎉 Production-ready release with full feature set\n\nFeatures:\n- Multi-agent AI system with CrewAI\n- Instagram video extraction and analysis\n- Cross-platform content optimization\n- Automated social media posting\n- Web dashboard and REST API\n- Comprehensive monitoring and analytics")
    ]
    
    print("Starting automated commit process...")
    print(f"Total commits planned: {len(commits)}\n")
    
    for i, (files, message) in enumerate(commits, 1):
        print(f"Commit {i}/{len(commits)}")
        if not commit_with_delay(files, message):
            print(f"Failed at commit {i}. Stopping.")
            break
        
        # Longer delay every 5 commits to simulate work sessions
        if i % 5 == 0 and i < len(commits):
            session_break = random.randint(300, 600)  # 5-10 minutes
            print(f"Taking a work session break: {session_break} seconds...\n")
            time.sleep(session_break)
    
    print("All commits completed! 🎉")
    print("\nPushing to GitHub...")

    # Set main branch and push
    run_command("git branch -M main")
    if run_command("git push -u origin main"):
        print("✅ Successfully pushed to https://github.com/Bravine-Kulei/social-agent")
        print("🌟 Check your GitHub profile for the green contribution squares!")
    else:
        print("❌ Push failed. You may need to push manually:")
        print("git push -u origin main")

if __name__ == "__main__":
    main()
