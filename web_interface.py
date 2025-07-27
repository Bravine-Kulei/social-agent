"""
Web Interface for the Instagram-to-Social Media Agent System
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger

from agents.orchestrator_agent import OrchestratorAgent
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Instagram-to-Social Media Agent System",
    description="AI-powered system for transforming Instagram content to Twitter and LinkedIn",
    version="1.0.0"
)

# Global orchestrator instance
orchestrator = OrchestratorAgent()

# Pydantic models for API
class WorkflowRequest(BaseModel):
    target_users: List[str]
    platforms: List[str] = ['twitter', 'linkedin']
    schedule_posts: bool = False

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    progress: Dict
    results: Optional[Dict] = None
    errors: List[str] = []

# In-memory storage for workflow status (use database in production)
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
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 40px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .workflow-list { margin-top: 30px; }
            .workflow-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Instagram-to-Social Media Agent</h1>
                <p>Transform Instagram videos into engaging Twitter and LinkedIn content</p>
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
                
                <button type="submit">🚀 Start Workflow</button>
            </form>
            
            <div id="status"></div>
            
            <div class="workflow-list">
                <h3>Recent Workflows</h3>
                <div id="workflows"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('workflowForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const users = document.getElementById('users').value.split(',').map(u => u.trim());
                const platforms = Array.from(document.getElementById('platforms').selectedOptions).map(o => o.value);
                const schedule = document.getElementById('schedule').checked;
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '<div class="status info">Starting workflow...</div>';
                
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
                        statusDiv.innerHTML = `<div class="status success">Workflow started! ID: ${result.workflow_id}</div>`;
                        pollWorkflowStatus(result.workflow_id);
                    } else {
                        statusDiv.innerHTML = `<div class="status error">Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
                }
            });
            
            async function pollWorkflowStatus(workflowId) {
                const statusDiv = document.getElementById('status');
                
                const poll = async () => {
                    try {
                        const response = await fetch(`/api/workflow/${workflowId}/status`);
                        const status = await response.json();
                        
                        if (status.status === 'completed') {
                            statusDiv.innerHTML = `<div class="status success">Workflow completed successfully!</div>`;
                            loadWorkflows();
                        } else if (status.status === 'failed') {
                            statusDiv.innerHTML = `<div class="status error">Workflow failed: ${status.errors.join(', ')}</div>`;
                        } else {
                            statusDiv.innerHTML = `<div class="status info">Status: ${status.status}</div>`;
                            setTimeout(poll, 5000); // Poll every 5 seconds
                        }
                    } catch (error) {
                        console.error('Polling error:', error);
                    }
                };
                
                poll();
            }
            
            async function loadWorkflows() {
                try {
                    const response = await fetch('/api/workflows');
                    const workflows = await response.json();
                    
                    const workflowsDiv = document.getElementById('workflows');
                    workflowsDiv.innerHTML = workflows.map(w => `
                        <div class="workflow-item">
                            <strong>ID:</strong> ${w.workflow_id}<br>
                            <strong>Status:</strong> ${w.status}<br>
                            <strong>Users:</strong> ${w.target_users ? w.target_users.join(', ') : 'N/A'}<br>
                            <strong>Platforms:</strong> ${w.platforms ? w.platforms.join(', ') : 'N/A'}
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading workflows:', error);
                }
            }
            
            // Load workflows on page load
            loadWorkflows();
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new workflow"""
    try:
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store initial workflow status
        workflow_storage[workflow_id] = {
            'workflow_id': workflow_id,
            'status': 'starting',
            'progress': {'step': 'initialization'},
            'target_users': request.target_users,
            'platforms': request.platforms,
            'schedule_posts': request.schedule_posts,
            'results': None,
            'errors': []
        }
        
        # Start workflow in background
        background_tasks.add_task(
            execute_workflow_background,
            workflow_id,
            request.target_users,
            request.platforms,
            request.schedule_posts
        )
        
        logger.info(f"Started workflow {workflow_id}")
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message="Workflow started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    if workflow_id not in workflow_storage:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowStatus(**workflow_storage[workflow_id])

@app.get("/api/workflows")
async def list_workflows():
    """List all workflows"""
    return list(workflow_storage.values())

@app.delete("/api/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    if workflow_id not in workflow_storage:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    del workflow_storage[workflow_id]
    return {"message": "Workflow deleted successfully"}

async def execute_workflow_background(workflow_id: str, 
                                    target_users: List[str], 
                                    platforms: List[str],
                                    schedule_posts: bool):
    """Execute workflow in background"""
    try:
        # Update status
        workflow_storage[workflow_id]['status'] = 'running'
        workflow_storage[workflow_id]['progress'] = {'step': 'extracting_content'}
        
        # Execute workflow
        results = await orchestrator.execute_full_workflow(
            target_users=target_users,
            platforms=platforms,
            schedule_posts=schedule_posts
        )
        
        # Update final status
        if results and not results.get('errors'):
            workflow_storage[workflow_id]['status'] = 'completed'
        else:
            workflow_storage[workflow_id]['status'] = 'failed'
            workflow_storage[workflow_id]['errors'] = results.get('errors', ['Unknown error'])
        
        workflow_storage[workflow_id]['results'] = results
        workflow_storage[workflow_id]['progress'] = {'step': 'completed'}
        
        logger.info(f"Workflow {workflow_id} completed")
        
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {str(e)}")
        workflow_storage[workflow_id]['status'] = 'failed'
        workflow_storage[workflow_id]['errors'] = [str(e)]

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/config")
async def get_config():
    """Get system configuration"""
    return {
        "max_videos_per_user": settings.max_videos_per_user,
        "supported_platforms": ["twitter", "linkedin"],
        "storage_path": settings.storage_path
    }

if __name__ == "__main__":
    uvicorn.run(app, host=settings.web_host, port=settings.web_port)
