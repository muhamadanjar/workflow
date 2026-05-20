"""
FastAPI Simple Async Task Template
Minimal example for getting started
"""
from celery import Celery

app = Celery("myapp")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/1"

# ============================================================
# Simple Task
# ============================================================

@app.task
def add(x: int, y: int) -> int:
    """Add two numbers"""
    return x + y

@app.task
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send email (simulate)"""
    # Replace with actual email sending
    print(f"Sending email to {recipient}: {subject}")
    return f"Email sent to {recipient}"

# ============================================================
# FastAPI Integration
# ============================================================

from fastapi import FastAPI

app_fast = FastAPI()

# Queue a task (returns immediately)
@app_fast.post("/add")
async def trigger_add(x: int, y: int):
    result = add.delay(x, y)
    return {
        "task_id": result.id,
        "status": "queued"
    }

# Get task status
@app_fast.get("/task/{task_id}")
async def get_task(task_id: str):
    result = app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }

# ============================================================
# Usage
# ============================================================

"""
Terminal 1: Start worker
  celery -A fastapi_async_task worker --loglevel=info

Terminal 2: Start FastAPI
  uvicorn fastapi_async_task:app_fast --reload

Terminal 3: Make requests
  curl http://localhost:8000/add?x=5&y=3

Get status:
  curl http://localhost:8000/task/{task_id}
"""
