"""
Simple Web Interface for the Instagram-to-Social Media Agent System
This is a lightweight version that runs without heavy dependencies
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Initialize FastAPI app
app = FastAPI(
    title="Instagram-to-Social Media Agent System",
    description="AI-powered system for transforming Instagram content to Twitter and LinkedIn",
    version="1.0.0"
)

# Pydantic models for API
class WorkflowRequest(BaseModel):
    target_users: List[str]
    platforms: List[str] = ['twitter', 'linkedin']
    schedule_posts: bool = False

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str

# In-memory storage for demo
workflow_storage = {}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instagram-to-Social Media Agent</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { 
                text-align: center; 
                margin-bottom: 40px; 
                color: #333;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .form-group { 
                margin-bottom: 25px; 
            }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #555;
            }
            input, select, textarea { 
                width: 100%; 
                padding: 15px; 
                border: 2px solid #e1e5e9; 
                border-radius: 10px; 
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            button { 
                background: linear-gradient(45deg, #667eea, #764ba2); 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 10px; 
                cursor: pointer; 
                font-size: 18px;
                font-weight: 600;
                transition: transform 0.2s ease;
            }
            button:hover { 
                transform: translateY(-2px);
            }
            .status { 
                margin-top: 25px; 
                padding: 20px; 
                border-radius: 10px; 
                font-weight: 500;
            }
            .success { 
                background: #d4edda; 
                color: #155724; 
                border: 2px solid #c3e6cb; 
            }
            .error { 
                background: #f8d7da; 
                color: #721c24; 
                border: 2px solid #f5c6cb; 
            }
            .info { 
                background: #d1ecf1; 
                color: #0c5460; 
                border: 2px solid #bee5eb; 
            }
            .warning {
                background: #fff3cd;
                color: #856404;
                border: 2px solid #ffeaa7;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature-card h3 {
                margin-top: 0;
                color: #333;
            }
            .demo-note {
                background: #fff3cd;
                border: 2px solid #ffeaa7;
                color: #856404;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Instagram-to-Social Media Agent</h1>
                <p>Transform Instagram videos into engaging Twitter and LinkedIn content</p>
            </div>
            
            <div class="demo-note">
                <strong>⚠️ Demo Mode:</strong> This is a demonstration interface. To run the full system, install all dependencies with <code>pip install -r requirements.txt</code>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🎯 Multi-Agent System</h3>
                    <p>Coordinated AI agents using CrewAI for intelligent workflow management</p>
                </div>
                <div class="feature-card">
                    <h3>📸 Instagram Extraction</h3>
                    <p>Automatically scrape videos from target Instagram users</p>
                </div>
                <div class="feature-card">
                    <h3>🧠 AI Transformation</h3>
                    <p>Convert content for different platforms using OpenAI/Anthropic</p>
                </div>
                <div class="feature-card">
                    <h3>📱 Multi-Platform</h3>
                    <p>Post to Twitter and LinkedIn with platform-specific optimizations</p>
                </div>
            </div>
            
            <form id="workflowForm">
                <div class="form-group">
                    <label for="users">Instagram Users (comma-separated):</label>
                    <input type="text" id="users" placeholder="username1, username2, username3" required>
                </div>
                
                <div class="form-group">
                    <label for="platforms">Target Platforms:</label>
                    <select id="platforms" multiple>
                        <option value="twitter" selected>Twitter</option>
                        <option value="linkedin" selected>LinkedIn</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="schedule"> Schedule posts instead of posting immediately
                    </label>
                </div>
                
                <button type="submit">🚀 Start Workflow (Demo)</button>
            </form>
            
            <div id="status"></div>
            
            <div style="margin-top: 40px;">
                <h3>🔧 Setup Instructions</h3>
                <ol>
                    <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
                    <li>Configure API keys in <code>.env</code> file</li>
                    <li>Run: <code>python main.py --web</code></li>
                </ol>
            </div>
        </div>
        
        <script>
            document.getElementById('workflowForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const users = document.getElementById('users').value.split(',').map(u => u.trim());
                const platforms = Array.from(document.getElementById('platforms').selectedOptions).map(o => o.value);
                const schedule = document.getElementById('schedule').checked;
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">🚀 Starting demo workflow...</div>';
                
                try {
                    const response = await fetch('/api/workflow/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            target_users: users,
                            platforms: platforms,
                            schedule_posts: schedule
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        statusDiv.innerHTML = `
                            <div class="status success">
                                ✅ Demo workflow started successfully!<br>
                                <strong>Workflow ID:</strong> ${result.workflow_id}<br>
                                <strong>Users:</strong> ${users.join(', ')}<br>
                                <strong>Platforms:</strong> ${platforms.join(', ')}<br>
                                <em>Note: This is a demo. Install full dependencies for actual processing.</em>
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest):
    """Start a demo workflow"""
    try:
        workflow_id = f"demo_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store demo workflow
        workflow_storage[workflow_id] = {
            'workflow_id': workflow_id,
            'status': 'demo_completed',
            'target_users': request.target_users,
            'platforms': request.platforms,
            'schedule_posts': request.schedule_posts,
            'created_at': datetime.now().isoformat(),
            'message': 'Demo workflow - install full dependencies for actual processing'
        }
        
        logger.info(f"Demo workflow started: {workflow_id}")
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="demo_started",
            message="Demo workflow started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting demo workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows")
async def list_workflows():
    """List all demo workflows"""
    return list(workflow_storage.values())

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "demo",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "Demo mode - install full dependencies for complete functionality"
    }

@app.get("/api/status")
async def system_status():
    """Get system status"""
    return {
        "mode": "demo",
        "dependencies_installed": False,
        "features_available": [
            "Web Interface",
            "API Endpoints", 
            "Demo Workflows"
        ],
        "features_requires_full_install": [
            "Instagram Scraping",
            "AI Content Transformation",
            "Social Media Posting",
            "Video Processing",
            "Multi-Agent Coordination"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Instagram-to-Social Media Agent System (Demo Mode)")
    print("📝 Install full dependencies with: pip install -r requirements.txt")
    print("🌐 Web interface will be available at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
