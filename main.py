from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from agents.orchestrator import orchestrator
from logger import logger
import uvicorn
import os

app = FastAPI(title="Computer Use Multi-Agent System API")

# Ensure directories exist
os.makedirs("/Users/vartikasrivastava/project/static/css", exist_ok=True)
os.makedirs("/Users/vartikasrivastava/project/templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="/Users/vartikasrivastava/project/static"), name="static")
app.mount("/screenshots", StaticFiles(directory="/Users/vartikasrivastava/project/screenshots"), name="screenshots")

class TaskRequest(BaseModel):
    task_description: str
    steps: Optional[List[Dict[str, Any]]] = None
    webhook_url: Optional[str] = None # For n8n callbacks

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("/Users/vartikasrivastava/project/templates/index.html", "r") as f:
        return f.read()

@app.post("/execute_task")
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Endpoint for n8n or external services to trigger a computer use task.
    """
    try:
        # Run in background to avoid timeout for n8n nodes
        background_tasks.add_task(
            orchestrator.run_task, 
            request.task_description, 
            request.steps,
            request.webhook_url
        )
        return {
            "status": "accepted", 
            "message": "Task queued for execution",
            "task": request.task_description
        }
    except Exception as e:
        logger.log_event("API", "endpoint_failure", {"error": str(e)}, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 10):
    return logger.get_recent_logs(limit)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
