"""
{{PROJECT_NAME}} - FastAPI + Celery Background Tasks Template
Professional async task handling with retry logic, error tracking, monitoring
"""
from celery import Celery, Task
from celery.utils.log import get_task_logger
from kombu import Queue, Exchange
from datetime import timedelta
from functools import wraps
import logging
import pika

logger = get_task_logger(__name__)

# ============================================================
# Celery Configuration (RabbitMQ with Pika)
# ============================================================

app = Celery("{{PROJECT_NAME}}")

app.conf.update(
    # Broker & Results (RabbitMQ + Redis)
    broker_url="amqp://guest:guest@localhost:5672//",
    result_backend="redis://localhost:6379/0",

    # Task Configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Pika Connection Settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_heartbeat=30,
    broker_pool_limit=10,

    # Routing
    task_routes={
        "{{PROJECT_NAME}}.tasks.high_priority.*": {"queue": "high"},
        "{{PROJECT_NAME}}.tasks.data_processing.*": {"queue": "processing"},
        "{{PROJECT_NAME}}.tasks.email.*": {"queue": "email"},
    },

    # Queue Configuration (RabbitMQ)
    task_queues=(
        Queue("default", Exchange("default", type="direct"), routing_key="default", durable=True),
        Queue("high", Exchange("high", type="direct"), routing_key="high", priority=10, durable=True),
        Queue("processing", Exchange("processing", type="direct"), routing_key="processing", durable=True),
        Queue("email", Exchange("email", type="direct"), routing_key="email", durable=True),
    ),

    # Limits & Timeouts
    task_time_limit=30 * 60,  # hard limit: 30 min
    task_soft_time_limit=25 * 60,  # soft limit: 25 min (allow graceful shutdown)
    task_acks_late=True,  # task acked after completion (prevent loss on worker crash)
    worker_prefetch_multiplier=1,  # process one task at a time

    # Retry Configuration
    task_autoretry_for=(Exception,),
    task_max_retries=3,
    task_default_retry_delay=60,  # retry after 60 seconds

    # Beat Schedule (Periodic Tasks)
    beat_schedule={
        "health-check-every-5min": {
            "task": "{{PROJECT_NAME}}.tasks.health_check",
            "schedule": timedelta(minutes=5),
        },
        "cleanup-old-records-daily": {
            "task": "{{PROJECT_NAME}}.tasks.cleanup_old_records",
            "schedule": timedelta(days=1),
            "options": {"expires": 3600}
        },
    }
)


# ============================================================
# Base Task Class with Error Handling & Monitoring
# ============================================================

class CallbackTask(Task):
    """Base task with monitoring, logging, error tracking"""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True

    def before_start(self, task_id, args, kwargs):
        """Called before task execution"""
        logger.info(f"Task {self.name} starting [ID: {task_id}]")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called on task retry"""
        logger.warning(
            f"Task {self.name} retrying [ID: {task_id}] - Error: {exc}",
            exc_info=einfo
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure after all retries exhausted"""
        logger.error(
            f"Task {self.name} FAILED [ID: {task_id}] - Error: {exc}",
            exc_info=einfo,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "args": args,
                "kwargs": kwargs,
            }
        )

    def on_success(self, result, task_id, args, kwargs):
        """Called on successful task completion"""
        logger.info(f"Task {self.name} completed [ID: {task_id}]")


app.Task = CallbackTask


# ============================================================
# FastAPI Integration
# ============================================================

from fastapi import FastAPI, BackgroundTasks
from typing import Any

fastapi_app = FastAPI(title="{{PROJECT_NAME}}")


def enqueue_task(task_name: str, *args, **kwargs):
    """Safely enqueue Celery task from FastAPI endpoint"""
    try:
        result = app.send_task(task_name, args=args, kwargs=kwargs)
        return {"task_id": result.id, "status": "queued"}
    except Exception as e:
        logger.error(f"Failed to enqueue task {task_name}: {e}")
        raise


@fastapi_app.post("/api/v1/tasks/{task_name}")
async def trigger_task(task_name: str, payload: dict = None):
    """Generic endpoint to trigger any registered task"""
    try:
        result = enqueue_task(task_name, **(payload or {}))
        return result
    except Exception as e:
        return {"error": str(e)}, 400


@fastapi_app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task execution status and result"""
    result = app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None
    }


# ============================================================
# Example Tasks
# ============================================================

@app.task(bind=True, queue="default")
def send_email(self, recipient: str, subject: str, body: str):
    """Send email - retryable task"""
    try:
        logger.info(f"Sending email to {recipient}")
        # Email sending logic here
        return f"Email sent to {recipient}"
    except Exception as e:
        logger.error(f"Email failed: {e}")
        raise self.retry(exc=e, countdown=60)


@app.task(bind=True, queue="processing")
def process_large_file(self, file_path: str):
    """Process large file - long-running task"""
    try:
        logger.info(f"Processing file: {file_path}")
        # File processing logic with progress tracking
        return f"Processed: {file_path}"
    except Exception as e:
        raise self.retry(exc=e, countdown=120)


@app.task(queue="high")
def sync_external_api():
    """High-priority API sync - no retry on specific errors"""
    logger.info("Syncing external API")
    # API sync logic
    return "Sync completed"


@app.task
def health_check():
    """Periodic health check - verify worker is alive"""
    logger.debug("Worker health check OK")
    return "OK"


@app.task
def cleanup_old_records():
    """Periodic cleanup - runs daily"""
    logger.info("Cleaning up old records")
    # Cleanup logic
    return "Cleanup completed"


# ============================================================
# Monitoring & Management
# ============================================================

@app.task
def get_worker_stats():
    """Get worker statistics for monitoring"""
    from celery import current_app

    stats = current_app.control.inspect().stats()
    active = current_app.control.inspect().active()
    reserved = current_app.control.inspect().reserved()

    return {
        "stats": stats,
        "active_tasks": active,
        "reserved_tasks": reserved
    }


# ============================================================
# Deployment Notes
# ============================================================

"""
Broker Setup (RabbitMQ with Pika):
  RabbitMQ with native pika driver (lightweight, efficient)
  - Broker: amqp://guest:guest@localhost:5672//
  - Result Backend: redis://localhost:6379/0

Development Worker:
  celery -A {{PROJECT_NAME}}.celery_config worker --loglevel=info

Production Worker (multi-queue):
  celery -A {{PROJECT_NAME}}.celery_config worker -Q default,high,processing --concurrency=4 --loglevel=info

Beat Scheduler (periodic tasks):
  celery -A {{PROJECT_NAME}}.celery_config beat --loglevel=info

Monitoring (Flower):
  celery -A {{PROJECT_NAME}}.celery_config flower

Docker:
  See Dockerfile.fastapi_worker

Requirements:
  celery==5.3.x
  pika==1.3.x (RabbitMQ driver)
  redis==5.x (result backend)
  fastapi==0.x
  uvicorn==0.x

Start RabbitMQ (Docker):
  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
  Management UI: http://localhost:15672 (guest/guest)
"""
