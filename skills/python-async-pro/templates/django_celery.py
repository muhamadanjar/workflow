"""
{{PROJECT_NAME}} - Django + Celery Background Tasks Template
Professional async task handling with ORM integration, signals, monitoring
"""
import os
from celery import Celery, Task
from celery.utils.log import get_task_logger
from celery.signals import task_prerun, task_postrun, task_failure
from kombu import Queue, Exchange
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{PROJECT_NAME}}.settings")

app = Celery("{{PROJECT_NAME}}")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = get_task_logger(__name__)

# ============================================================
# Celery Configuration (add to Django settings.py)
# ============================================================

CELERY_CONFIG = {
    # Broker & Results
    "CELERY_BROKER_URL": "redis://localhost:6379/0",
    "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",

    # Task Configuration
    "CELERY_TASK_SERIALIZER": "json",
    "CELERY_ACCEPT_CONTENT": ["json"],
    "CELERY_RESULT_SERIALIZER": "json",
    "CELERY_TIMEZONE": "UTC",
    "CELERY_ENABLE_UTC": True,

    # Routing
    "CELERY_TASK_ROUTES": {
        "{{PROJECT_NAME}}.tasks.high_priority.*": {"queue": "high"},
        "{{PROJECT_NAME}}.tasks.email.*": {"queue": "email"},
        "{{PROJECT_NAME}}.tasks.reports.*": {"queue": "reports"},
    },

    # Queues
    "CELERY_QUEUES": (
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high", Exchange("high"), routing_key="high", priority=10),
        Queue("email", Exchange("email"), routing_key="email"),
        Queue("reports", Exchange("reports"), routing_key="reports"),
    ),

    # Limits & Timeouts
    "CELERY_TASK_TIME_LIMIT": 30 * 60,  # hard limit
    "CELERY_TASK_SOFT_TIME_LIMIT": 25 * 60,  # soft limit
    "CELERY_TASK_ACKS_LATE": True,
    "CELERY_WORKER_PREFETCH_MULTIPLIER": 1,

    # Retry
    "CELERY_TASK_AUTORETRY_FOR": (Exception,),
    "CELERY_TASK_MAX_RETRIES": 3,
    "CELERY_TASK_DEFAULT_RETRY_DELAY": 60,

    # Beat Schedule
    "CELERY_BEAT_SCHEDULE": {
        "health-check-5min": {
            "task": "{{PROJECT_NAME}}.tasks.health_check",
            "schedule": timedelta(minutes=5),
        },
        "send-daily-digest": {
            "task": "{{PROJECT_NAME}}.tasks.send_daily_digest",
            "schedule": timedelta(days=1),
            "options": {"expires": 3600}
        },
    }
}


# ============================================================
# Base Task Class
# ============================================================

class DjangoTask(Task):
    """Base task for Django with ORM access, error handling"""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True

    def before_start(self, task_id, args, kwargs):
        logger.info(f"Task {self.name} starting [ID: {task_id}]")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(
            f"Task {self.name} retrying [ID: {task_id}]",
            exc_info=einfo
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Task {self.name} FAILED [ID: {task_id}]",
            exc_info=einfo,
            extra={"task_id": task_id, "task_name": self.name}
        )

    def on_success(self, result, task_id, args, kwargs):
        logger.info(f"Task {self.name} completed [ID: {task_id}]")


app.Task = DjangoTask


# ============================================================
# Task Signals for Monitoring
# ============================================================

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Pre-execution logging"""
    logger.debug(f"Task {task.name} [ID: {task_id}] starting execution")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, result=None, **kwargs):
    """Post-execution logging"""
    logger.debug(f"Task {task.name} [ID: {task_id}] completed with result: {result}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Failure notification"""
    logger.error(f"Task failed [ID: {task_id}]: {exception}")
    # Send alert email, notify monitoring system, etc.


# ============================================================
# Example Tasks with Django ORM
# ============================================================

@app.task(bind=True, queue="email")
def send_welcome_email(self, user_id: int):
    """Send welcome email to user (Django ORM access)"""
    from django.contrib.auth.models import User
    from django.core.mail import send_mail

    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject="Welcome!",
            message=f"Welcome {user.first_name}!",
            from_email="noreply@example.com",
            recipient_list=[user.email],
        )
        logger.info(f"Welcome email sent to {user.email}")
        return f"Email sent to {user.email}"
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise
    except Exception as e:
        logger.error(f"Email failed: {e}")
        raise self.retry(exc=e, countdown=60)


@app.task(queue="reports")
def generate_monthly_report():
    """Generate report - accesses multiple models"""
    from django.db.models import Count
    from myapp.models import Order, User

    try:
        logger.info("Generating monthly report")

        # Query data
        total_orders = Order.objects.filter(
            created_at__month=now().month
        ).count()
        total_users = User.objects.filter(is_active=True).count()

        report_data = {
            "period": "monthly",
            "total_orders": total_orders,
            "total_users": total_users,
        }

        logger.info(f"Report generated: {report_data}")
        return report_data
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise


@app.task(bind=True, queue="high")
def bulk_update_user_status(self, user_ids: list, status: str):
    """Bulk update with progress tracking"""
    from django.contrib.auth.models import User

    try:
        total = len(user_ids)
        updated = 0

        for i, user_id in enumerate(user_ids):
            user = User.objects.get(id=user_id)
            user.is_active = (status == "active")
            user.save()
            updated += 1

            # Update task state for progress
            self.update_state(
                state="PROGRESS",
                meta={"current": updated, "total": total}
            )

        logger.info(f"Updated {updated} users to status: {status}")
        return f"Updated {total} users"
    except Exception as e:
        raise self.retry(exc=e, countdown=120)


@app.task
def health_check():
    """Periodic health check"""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.debug("Health check passed")
        return "OK"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise


# ============================================================
# Model Signals Integration
# ============================================================

from django.db.models.signals import post_save
from django.dispatch import receiver

# Example: trigger task on model save
@receiver(post_save, sender="auth.User")
def user_post_save(sender, instance, created, **kwargs):
    """Automatically send welcome email when new user created"""
    if created:
        send_welcome_email.delay(instance.id)
        logger.info(f"Queued welcome email for new user {instance.id}")


# ============================================================
# Celery Tasks Management Command (Django)
# ============================================================

"""
Create: {{PROJECT_NAME}}/management/commands/celery_worker.py

from django.core.management.base import BaseCommand
from celery.bin import worker

class Command(BaseCommand):
    help = 'Start Celery worker'

    def add_arguments(self, parser):
        parser.add_argument('--queues', default='default,high,email')
        parser.add_argument('--concurrency', default='4', type=int)

    def handle(self, *args, **options):
        w = worker.worker(app=app)
        w.start(
            queues=options['queues'].split(','),
            concurrency=options['concurrency']
        )

Usage:
  python manage.py celery_worker --queues default,high --concurrency 4
"""


# ============================================================
# Deployment Notes
# ============================================================

"""
Development:
  celery -A {{PROJECT_NAME}} worker --loglevel=info
  celery -A {{PROJECT_NAME}} beat --loglevel=info

Production (Supervisor config):
  [program:celery_worker]
  command=celery -A {{PROJECT_NAME}} worker -Q default,high,email --concurrency=4
  directory=/app
  user=app
  numprocs=1
  autostart=true
  autorestart=true
  startsecs=10
  stopwaitsecs=600

  [program:celery_beat]
  command=celery -A {{PROJECT_NAME}} beat
  directory=/app
  user=app
  numprocs=1
  autostart=true
  autorestart=true

Monitoring:
  celery -A {{PROJECT_NAME}} flower

Requirements:
  celery[redis]==5.3.x
  django-celery-beat==2.5.x
  django-celery-results==2.5.x
  redis==5.x
"""
