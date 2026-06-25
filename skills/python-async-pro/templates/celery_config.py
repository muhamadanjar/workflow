"""
Celery configuration for FastAPI + RabbitMQ + Redis
"""

import os
from kombu import Exchange, Queue

# Broker settings
broker_url = os.getenv(
    "CELERY_BROKER_URL",
    "amqp://guest:guest@localhost:5672//"
)
result_backend = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0"
)

# Serialization
task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True

# Task settings
task_track_started = True
task_send_sent_event = True
task_time_limit = 30 * 60  # 30 minutes hard limit
task_soft_time_limit = 25 * 60  # 25 minutes soft limit

# Worker settings
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Results
result_expires = 3600  # Results expire after 1 hour
result_persistent = True
result_compression = "gzip"

# Queues
default_exchange = Exchange("tasks", type="direct", durable=True)
default_queue = "default"

task_queues = (
    Queue(
        "default",
        exchange=default_exchange,
        routing_key="default",
        queue_arguments={"x-message-ttl": 3600000}  # 1 hour
    ),
    Queue(
        "high_priority",
        exchange=default_exchange,
        routing_key="high",
        priority=10,
        queue_arguments={"x-message-ttl": 1800000}  # 30 minutes
    ),
    Queue(
        "low_priority",
        exchange=default_exchange,
        routing_key="low",
        priority=0,
        queue_arguments={"x-message-ttl": 7200000}  # 2 hours
    ),
    Queue(
        "scheduled",
        exchange=default_exchange,
        routing_key="scheduled",
        queue_arguments={"x-message-ttl": 86400000}  # 24 hours
    ),
)

task_routes = {
    "*.process_data": {"queue": "default"},
    "*.send_email": {"queue": "high_priority"},
    "*.generate_report": {"queue": "low_priority"},
    "*.scheduled_task": {"queue": "scheduled"},
}

# Retry settings
task_autoretry_for = (Exception,)
task_max_retries = 3
task_default_retry_delay = 60  # 1 minute

# Beat schedule (periodic tasks)
from celery.schedules import crontab

beat_schedule = {
    "cleanup-old-results": {
        "task": "tasks.cleanup_old_results",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "generate-daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    "send-digest-email": {
        "task": "tasks.send_digest_email",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Weekly Monday 9 AM
    },
}

# Error handling
task_acks_late = True
task_reject_on_worker_lost = True

# Logging
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] "
    "[%(task_name)s(%(task_id)s)] %(message)s"
)
