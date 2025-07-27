#!/usr/bin/env python3
"""
Quick commit script to finish the remaining commits
"""
import subprocess
import time

def run_command(command):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Running: {command}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(f"Success: {result.stdout.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def commit_files(files, message):
    """Add files and commit with message"""
    # Add files
    for file in files:
        run_command(f"git add {file}")
    
    # Commit
    run_command(f'git commit -m "{message}"')
    
    # Small delay
    time.sleep(2)

def main():
    """Execute remaining commits"""
    
    remaining_commits = [
        # Services
        (["services/content_analyzer.py"], "🧠 Add AI-powered content analysis and video processing"),
        (["services/social_media_poster.py"], "📱 Implement Twitter and LinkedIn posting services"),
        
        # Agents
        (["agents/instagram_agent.py"], "🤖 Create Instagram extraction agent with CrewAI integration"),
        (["agents/content_transformer_agent.py"], "✨ Add content transformation agent for multi-platform optimization"),
        (["agents/twitter_agent.py"], "🐦 Implement Twitter posting agent with engagement tracking"),
        (["agents/linkedin_agent.py"], "💼 Add LinkedIn publishing agent for professional content"),
        (["agents/orchestrator_agent.py"], "🎯 Create orchestrator agent for workflow coordination"),
        
        # Utilities
        (["utils/video_processor.py"], "🎬 Add comprehensive video processing utilities"),
        (["utils/text_generator.py"], "📝 Implement AI text generation with multiple model support"),
        (["utils/api_clients.py"], "🌐 Add API client management with rate limiting"),
        
        # Web Interface
        (["web_interface.py"], "🖥️ Create web dashboard with FastAPI and real-time monitoring"),
        
        # Final touches
        (["commit_script.py", "quick_commit.py"], "🔧 Add automated commit scripts for development workflow"),
    ]
    
    print(f"Executing {len(remaining_commits)} commits...")
    
    for i, (files, message) in enumerate(remaining_commits, 1):
        print(f"\nCommit {i}/{len(remaining_commits)}: {message}")
        commit_files(files, message)
    
    print("\nPushing all commits to GitHub...")
    if run_command("git push origin main"):
        print("✅ Successfully pushed all commits to GitHub!")
        print("🌟 Check your repository: https://github.com/Bravine-Kulei/social-agent")
        print("🎉 Your contribution graph should now show multiple green squares!")
    else:
        print("❌ Push failed. Try manually: git push origin main")

if __name__ == "__main__":
    main()
