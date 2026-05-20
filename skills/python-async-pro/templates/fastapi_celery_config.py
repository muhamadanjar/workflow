"""
FastAPI Celery Configuration with Pika (RabbitMQ)
Production-ready config for FastAPI projects using RabbitMQ as broker
"""
from celery import Celery
from kombu import Queue, Exchange
from datetime import timedelta
import os

# ============================================================
# Celery Configuration (RabbitMQ + Pika + Redis Results)
# ============================================================

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "amqp://guest:guest@localhost:5672//"
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0"
)

app = Celery("fastapi_app")

app.conf.update(
    # ========================================================
    # Broker Configuration (RabbitMQ with Pika)
    # ========================================================
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,

    # Pika-specific settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_heartbeat=30,  # Heartbeat interval (seconds)
    broker_pool_limit=10,  # Max connections to broker
    broker_login_method="PLAIN",  # RabbitMQ auth method

    # ========================================================
    # Task Serialization
    # ========================================================
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # ========================================================
    # Queue & Exchange Configuration
    # ========================================================
    task_queues=(
        # High-priority queue (user-facing operations)
        Queue(
            "high",
            Exchange("high", type="direct", durable=True),
            routing_key="high",
            priority=10,
            durable=True,
            queue_arguments={"x-max-priority": 10}
        ),
        # Default queue (standard operations)
        Queue(
            "default",
            Exchange("default", type="direct", durable=True),
            routing_key="default",
            priority=5,
            durable=True
        ),
        # Email queue (notifications)
        Queue(
            "email",
            Exchange("email", type="direct", durable=True),
            routing_key="email",
            priority=3,
            durable=True
        ),
        # Processing queue (long-running jobs)
        Queue(
            "processing",
            Exchange("processing", type="direct", durable=True),
            routing_key="processing",
            priority=1,
            durable=True
        ),
    ),

    # Task routing to appropriate queues
    task_routes={
        "app.tasks.high_priority.*": {"queue": "high"},
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.processing.*": {"queue": "processing"},
    },

    # ========================================================
    # Task Execution
    # ========================================================
    task_time_limit=30 * 60,  # Hard limit: 30 minutes
    task_soft_time_limit=25 * 60,  # Soft limit: 25 minutes
    task_acks_late=True,  # Ack after task completion (prevents loss)
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_always_eager=False,  # Async execution (set True for testing)

    # ========================================================
    # Retry Configuration
    # ========================================================
    task_autoretry_for=(Exception,),
    task_max_retries=3,
    task_default_retry_delay=60,
    task_eager_propagates=True,

    # ========================================================
    # Beat Schedule (Periodic Tasks)
    # ========================================================
    beat_schedule={
        "health-check-every-5-minutes": {
            "task": "app.tasks.monitoring.health_check",
            "schedule": timedelta(minutes=5),
        },
        "cleanup-sessions-daily": {
            "task": "app.tasks.maintenance.cleanup_sessions",
            "schedule": timedelta(hours=24),
            "options": {"expires": 3600}
        },
    },

    # ========================================================
    # Worker Configuration
    # ========================================================
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",

    # ========================================================
    # Result Backend Configuration
    # ========================================================
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,  # Persist results to disk
    result_compression="gzip",  # Compress large results
)


# ============================================================
# Environment-Specific Configuration
# ============================================================

class CeleryConfig:
    """Base Celery config (development)"""
    broker_url = CELERY_BROKER_URL
    result_backend = CELERY_RESULT_BACKEND


class CeleryConfigProduction(CeleryConfig):
    """Production Celery config"""
    # More aggressive timeouts in production
    task_time_limit = 20 * 60  # 20 minutes
    task_soft_time_limit = 15 * 60  # 15 minutes

    # Disable retries for critical tasks
    task_autoretry_for = ()
    task_max_retries = 1


class CeleryConfigTesting(CeleryConfig):
    """Testing Celery config"""
    task_always_eager = True  # Run tasks synchronously in tests
    task_eager_propagates = True
    result_backend = "cache+memory://"


# ============================================================
# Setup by Environment
# ============================================================

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    app.config_from_object(CeleryConfigProduction())
elif ENV == "testing":
    app.config_from_object(CeleryConfigTesting())
else:
    app.config_from_object(CeleryConfig())


# ============================================================
# Quick Reference
# ============================================================

"""
STARTUP COMMANDS:

Development Worker:
  celery -A celery_config worker --loglevel=info

Multi-queue Worker:
  celery -A celery_config worker -Q high,default,email,processing \\
    --concurrency=4 --loglevel=info

Beat Scheduler (periodic tasks):
  celery -A celery_config beat --loglevel=info

Flower Monitoring UI:
  celery -A celery_config flower --port=5555
  → http://localhost:5555

Combined Worker + Beat:
  celery -A celery_config worker --beat --loglevel=info

DOCKER COMPOSE:
  docker-compose up
  → API: http://localhost:8000
  → Flower: http://localhost:5555
  → RabbitMQ UI: http://localhost:15672 (guest/guest)

TESTING:
  Set ENVIRONMENT=testing
  Tasks run synchronously in process
  No RabbitMQ/Redis needed
"""
