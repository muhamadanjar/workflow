"""
FastAPI + Celery + RabbitMQ base template.
Complete working example with task queue integration.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from celery import Celery, Task
from celery.result import AsyncResult
from kombu import Exchange, Queue
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Async Tasks API")

# Celery configuration
class CeleryConfig:
    broker_url = "amqp://guest:guest@rabbitmq:5672//"
    result_backend = "redis://redis:6379/0"
    task_serializer = "json"
    accept_content = ["json"]
    result_serializer = "json"
    timezone = "UTC"
    enable_utc = True
    task_track_started = True
    task_time_limit = 30 * 60  # 30 minutes
    task_soft_time_limit = 25 * 60  # 25 minutes

# Initialize Celery
celery_app = Celery(__name__)
celery_app.config_from_object(CeleryConfig)

# Define queues
default_exchange = Exchange("tasks", type="direct")
celery_app.conf.task_queues = (
    Queue("default", exchange=default_exchange, routing_key="default"),
    Queue("high_priority", exchange=default_exchange, routing_key="high"),
    Queue("low_priority", exchange=default_exchange, routing_key="low"),
)

# ============================================
# Request/Response Models
# ============================================

class TaskRequest(BaseModel):
    data: str
    priority: str = "default"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None

# ============================================
# Celery Tasks
# ============================================

@celery_app.task(
    name="process_data",
    queue="default",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    time_limit=600
)
def process_data_task(self: Task, data: str):
    """
    Process data asynchronously.
    Retries up to 3 times with 5 second delay on failure.
    """
    try:
        logger.info(f"Processing: {data}")

        # Simulate processing
        result = {
            "original": data,
            "processed": data.upper(),
            "length": len(data),
            "task_id": self.request.id
        }

        logger.info(f"Completed: {self.request.id}")
        return result
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(
    name="send_email",
    queue="high_priority",
    bind=True,
    soft_time_limit=30
)
def send_email_task(self: Task, email: str, subject: str, body: str):
    """Send email via background task."""
    try:
        logger.info(f"Sending email to {email}")

        # Simulated email sending
        # In production: use celery-email or sendgrid

        result = {
            "email": email,
            "subject": subject,
            "status": "sent",
            "task_id": self.request.id
        }

        logger.info(f"Email sent: {self.request.id}")
        return result
    except Exception as exc:
        logger.error(f"Email send failed: {exc}")
        raise

@celery_app.task(
    name="generate_report",
    queue="low_priority",
    bind=True,
    time_limit=1800  # 30 minutes
)
def generate_report_task(self: Task, report_type: str, filters: dict):
    """Generate report asynchronously (long-running)."""
    try:
        logger.info(f"Generating {report_type} report")

        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting..."}
        )

        # Simulate long processing
        for i in range(0, 100, 10):
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i,
                    "total": 100,
                    "status": f"Processing {i}%"
                }
            )

        result = {
            "report_type": report_type,
            "filters": filters,
            "total_rows": 1000,
            "status": "completed",
            "file_path": "/reports/report_123.pdf",
            "task_id": self.request.id
        }

        logger.info(f"Report generated: {self.request.id}")
        return result
    except Exception as exc:
        logger.error(f"Report generation failed: {exc}")
        raise

# ============================================
# FastAPI Routes
# ============================================

@app.post("/tasks/process", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Enqueue a new task."""
    try:
        # Queue task with priority
        task = process_data_task.apply_async(
            args=[request.data],
            queue=request.priority,
            countdown=0,  # Execute immediately
            expires=3600  # Task expires in 1 hour
        )

        return TaskResponse(
            task_id=task.id,
            status="queued",
            message=f"Task {task.id} queued for processing"
        )
    except Exception as e:
        logger.error(f"Failed to queue task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/send-email")
async def send_email(email: str, subject: str, body: str):
    """Send email via background task."""
    task = send_email_task.apply_async(
        args=[email, subject, body],
        queue="high_priority"
    )

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Email task {task.id} queued"
    )

@app.post("/tasks/generate-report")
async def generate_report(report_type: str, filters: dict = {}):
    """Generate report asynchronously."""
    task = generate_report_task.apply_async(
        args=[report_type, filters],
        queue="low_priority"
    )

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Report generation task {task.id} queued"
    )

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get task status and result."""
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        return TaskStatus(
            task_id=task_id,
            status="pending",
            result=None
        )
    elif task_result.state == "PROGRESS":
        return TaskStatus(
            task_id=task_id,
            status="in_progress",
            result=task_result.info
        )
    elif task_result.state == "SUCCESS":
        return TaskStatus(
            task_id=task_id,
            status="completed",
            result=task_result.result
        )
    elif task_result.state == "FAILURE":
        return TaskStatus(
            task_id=task_id,
            status="failed",
            error=str(task_result.info)
        )
    elif task_result.state == "RETRY":
        return TaskStatus(
            task_id=task_id,
            status="retrying",
            result=task_result.info
        )
    else:
        return TaskStatus(
            task_id=task_id,
            status=task_result.state,
            result=task_result.result
        )

@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a task."""
    task_result = AsyncResult(task_id, app=celery_app)
    task_result.revoke(terminate=True)

    return {"task_id": task_id, "message": "Task cancelled"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "celery_workers": celery_app.control.inspect().active()
    }

# ============================================
# Startup/Shutdown
# ============================================

@app.on_event("startup")
async def startup():
    logger.info("FastAPI app starting")

@app.on_event("shutdown")
async def shutdown():
    logger.info("FastAPI app shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
