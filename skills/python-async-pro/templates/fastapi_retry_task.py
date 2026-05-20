"""
FastAPI Task with Retry Logic Template
Handles failures gracefully with exponential backoff
"""
from celery import Celery, Task
from celery.utils.log import get_task_logger
import requests

app = Celery("myapp")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/1"

logger = get_task_logger(__name__)

# ============================================================
# Base Task with Retry Support
# ============================================================

class RetryableTask(Task):
    """Task with automatic retry on failure"""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 min between retries

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {self.name} retrying: {exc}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} failed: {exc}")

app.Task = RetryableTask

# ============================================================
# Retryable Tasks
# ============================================================

@app.task(bind=True, queue='default')
def call_external_api(self, url: str, max_retries=3):
    """Call external API with retry on failure"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError as e:
        # Retry on connection error
        logger.error(f"Connection error: {e}")
        raise self.retry(exc=e, countdown=60)
    except requests.Timeout as e:
        # Retry on timeout
        logger.error(f"Timeout: {e}")
        raise self.retry(exc=e, countdown=120)
    except requests.HTTPError as e:
        if response.status_code == 429:  # Rate limited
            logger.warning(f"Rate limited, retrying in 5 minutes")
            raise self.retry(exc=e, countdown=300)
        elif response.status_code >= 500:  # Server error
            logger.warning(f"Server error {response.status_code}, retrying")
            raise self.retry(exc=e, countdown=60)
        else:  # Client error - don't retry
            logger.error(f"Client error {response.status_code}: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

# ============================================================
# Retry with Custom Logic
# ============================================================

@app.task(bind=True, queue='email')
def send_email_with_retry(self, recipient: str, subject: str, body: str):
    """Send email with selective retry"""
    try:
        # Replace with actual email sending
        print(f"Sending email to {recipient}")
        # Simulate API call
        response = requests.post(
            "https://api.example.com/send",
            json={"to": recipient, "subject": subject, "body": body},
            timeout=10
        )
        response.raise_for_status()
        return f"Email sent to {recipient}"
    except requests.ConnectionError as e:
        if self.request.retries < 3:
            logger.warning(f"Connection error, retry {self.request.retries+1}/3")
            raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))
        else:
            logger.error(f"Failed to send email after 3 retries: {e}")
            raise
    except Exception as e:
        logger.error(f"Email failed: {e}")
        raise

# ============================================================
# FastAPI Integration
# ============================================================

from fastapi import FastAPI

app_fast = FastAPI()

@app_fast.post("/api/webhook")
async def trigger_webhook(url: str):
    """Call webhook with automatic retry"""
    task = call_external_api.delay(url)
    return {"task_id": task.id, "status": "queued"}

@app_fast.post("/api/email")
async def trigger_email(recipient: str, subject: str):
    """Send email with retry"""
    task = send_email_with_retry.delay(recipient, subject, "Welcome!")
    return {"task_id": task.id, "status": "queued"}

@app_fast.get("/task/{task_id}")
async def get_status(task_id: str):
    result = app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "retries": result.request.retries if hasattr(result, 'request') else 0,
        "result": result.result if result.ready() else None
    }

# ============================================================
# Retry Strategies
# ============================================================

"""
1. Fixed Delay (simple)
   @app.task(bind=True, autoretry_for=(Exception,))
   def task(self):
       raise self.retry(exc=e, countdown=60)  # Retry after 60s

2. Exponential Backoff (most common)
   retry_backoff = True
   retry_backoff_max = 600

   Retry delays:
   - 1st retry: 2^1 = 2 seconds
   - 2nd retry: 2^2 = 4 seconds
   - 3rd retry: 2^3 = 8 seconds
   - ... capped at 600 seconds

3. With Jitter (prevent thundering herd)
   retry_jitter = True

   Adds randomness to prevent all workers from retrying at same time

4. Custom Logic (selective retry)
   - Retry on 5xx errors (server error)
   - Retry on connection timeout
   - Don't retry on 4xx errors (client error)
"""
