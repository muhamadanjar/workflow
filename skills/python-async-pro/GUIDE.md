# Professional Python Async/Background Tasks Guide

Complete guide to production-grade async task handling in FastAPI and Django with Celery.

## Table of Contents

1. [Architecture Patterns](#architecture-patterns)
2. [FastAPI + Celery](#fastapi--celery)
3. [Django + Celery](#django--celery)
4. [Task Design](#task-design)
5. [Error Handling & Retry](#error-handling--retry)
6. [Monitoring & Observability](#monitoring--observability)
7. [Deployment](#deployment)
8. [Best Practices](#best-practices)

---

## Architecture Patterns

### Event-Driven Architecture

```
User Action
    ↓
FastAPI/Django Endpoint (returns immediately)
    ↓
Queue Task to Celery
    ↓
Worker Process (handles async)
    ↓
Update Database/Cache/External Systems
```

**Benefits:**
- Fast API response (user doesn't wait)
- Decoupled systems (worker failure ≠ API failure)
- Scalable (add workers as needed)
- Observable (track task status/progress)

### Queue Strategies

**Single Queue (simple projects)**
```python
CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default"),
)
```

**Multi-Queue (recommended for production)**
```python
CELERY_TASK_ROUTES = {
    "app.tasks.high_priority.*": {"queue": "high"},     # SLA: fast
    "app.tasks.email.*": {"queue": "email"},            # SLA: within minutes
    "app.tasks.reports.*": {"queue": "reports"},        # SLA: best-effort
}

CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default", priority=5),
    Queue("high", Exchange("high"), routing_key="high", priority=10),
    Queue("email", Exchange("email"), routing_key="email", priority=3),
    Queue("reports", Exchange("reports"), routing_key="reports", priority=1),
)
```

Queue priorities:
- **High (10)**: User-facing, <5 min SLA (password reset, 2FA)
- **Default (5)**: Standard operations (emails, notifications)
- **Email (3)**: Marketing emails, digests
- **Reports (1)**: Long-running, can wait (analytics, exports)

---

## FastAPI + Celery

### Minimal Setup

```python
# celery_app.py
from celery import Celery

app = Celery("myapp")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/1"
app.conf.accept_content = ["json"]
app.conf.task_serializer = "json"

# tasks.py
from celery_app import app

@app.task
def send_email(recipient: str):
    # Task body
    return f"Email sent to {recipient}"

# main.py (FastAPI)
from fastapi import FastAPI
from celery_app import app as celery_app
from tasks import send_email

app = FastAPI()

@app.post("/send-email")
async def trigger_email(recipient: str):
    # Queue task (returns immediately)
    result = send_email.delay(recipient)
    return {"task_id": result.id, "status": "queued"}

@app.get("/task/{task_id}/status")
async def get_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

### Running

```bash
# Terminal 1: FastAPI
uvicorn main:app --reload

# Terminal 2: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Monitor
celery -A celery_app flower
```

Access Flower at http://localhost:5555

---

## Django + Celery

### Project Setup

```python
# myproject/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# myproject/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# myapp/tasks.py
from celery import shared_task
from django.contrib.auth.models import User

@shared_task
def send_welcome_email(user_id: int):
    user = User.objects.get(id=user_id)
    # Send email
    return f"Email sent to {user.email}"

# myapp/views.py
from django.http import JsonResponse
from .tasks import send_welcome_email

def register(request):
    user = User.objects.create_user(...)
    
    # Queue task
    task = send_welcome_email.delay(user.id)
    
    return JsonResponse({
        "task_id": task.id,
        "status": "User registered, welcome email queued"
    })
```

### Signal Integration (Auto-Queue on Model Save)

```python
# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .tasks import process_order_payment

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        # Auto-queue when order created
        process_order_payment.delay(instance.id)

# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    
    def ready(self):
        import myapp.signals  # Register signals
```

---

## Task Design

### Basic Task

```python
from celery import app

@app.task
def simple_task(x: int, y: int) -> int:
    return x + y

# Call
simple_task.delay(5, 3)  # Async
simple_task(5, 3)         # Sync (same process)
```

### Task with Retry

```python
@app.task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 min between retries
    retry_jitter=True
)
def api_call_task(url: str):
    response = requests.get(url, timeout=30)
    return response.json()
```

Retry delay sequence:
- Attempt 1: immediate
- Attempt 2: 2^1 = 2 seconds
- Attempt 3: 2^2 = 4 seconds
- Attempt 4: 2^3 = 8 seconds (capped at 600)

### Long-Running Task with Progress

```python
from celery import current_task

@app.task(bind=True)
def process_large_file(self, file_path: str):
    with open(file_path) as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Process line
        process_line(line)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': i+1, 'total': len(lines)}
        )
    
    return "Complete"

# Frontend polls for progress
# GET /task/{task_id}/status → {"state": "PROGRESS", "current": 50, "total": 100}
```

### Task Callback (chain tasks)

```python
from celery import chain, group

# Sequential execution
task_chain = chain(
    task1.s(10),
    task2.s(),  # receives output of task1
    task3.s()
)
result = task_chain()

# Parallel execution
task_group = group(
    task1.s(10),
    task2.s(20),
    task3.s(30)
)
results = task_group()

# Mixed
workflow = chain(
    task1.s(10),
    group(task2.s(), task3.s()),
    task4.s()
)
```

---

## Error Handling & Retry

### Base Task Class with Error Tracking

```python
from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class ErrorTrackingTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(
            f"Task {self.name} retrying",
            exc_info=einfo,
            extra={'task_id': task_id}
        )
        # Send alert to monitoring
        send_alert(f"Task {self.name} retrying: {exc}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Task {self.name} FAILED after retries",
            exc_info=einfo,
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'args': args
            }
        )
        # Notify ops team
        send_email(
            subject=f"ALERT: Task {self.name} failed",
            body=str(einfo)
        )
    
    def on_success(self, result, task_id, args, kwargs):
        logger.info(f"Task {self.name} completed")

app.Task = ErrorTrackingTask
```

### Selective Retry

```python
@app.task(bind=True, max_retries=3)
def task_with_selective_retry(self, user_id: int):
    try:
        # Call external API
        response = requests.get(f"https://api.example.com/user/{user_id}")
        return response.json()
    except requests.ConnectionError as e:
        # Retry on connection error
        raise self.retry(exc=e, countdown=60)
    except requests.HTTPError as e:
        if response.status_code == 429:  # Rate limited
            raise self.retry(exc=e, countdown=300)
        else:  # Other HTTP errors - don't retry
            logger.error(f"HTTP error {response.status_code}: {e}")
            raise
```

### Dead Letter Queue Pattern

```python
@app.task(bind=True, max_retries=3, queue='default')
def critical_task(self, data: dict):
    try:
        # Process
        return process_data(data)
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        else:
            # Move to DLQ after retries exhausted
            logger.error(f"Moving to DLQ: {data}")
            dead_letter_queue.push(data)
            raise
```

---

## Monitoring & Observability

### Flower (Web UI)

```bash
celery -A celery_app flower --port=5555
```

Access: http://localhost:5555
- Active tasks
- Worker stats
- Task history
- Real-time monitoring

### Programmatic Monitoring

```python
from celery import current_app

def get_worker_stats():
    inspector = current_app.control.inspect()
    
    return {
        'stats': inspector.stats(),
        'active_tasks': inspector.active(),
        'reserved_tasks': inspector.reserved(),
        'registered_tasks': inspector.registered()
    }

# In FastAPI
@app.get("/admin/celery/stats")
async def celery_stats():
    return get_worker_stats()
```

### Custom Metrics

```python
from prometheus_client import Counter, Histogram
import time

task_counter = Counter(
    'celery_task_total',
    'Total tasks',
    ['task_name', 'status']
)

task_duration = Histogram(
    'celery_task_duration_seconds',
    'Task duration',
    ['task_name']
)

class MetricsTask(Task):
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        task_counter.labels(
            task_name=self.name,
            status='retry'
        ).inc()
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_counter.labels(
            task_name=self.name,
            status='failure'
        ).inc()
    
    def on_success(self, result, task_id, args, kwargs):
        task_counter.labels(
            task_name=self.name,
            status='success'
        ).inc()

app.Task = MetricsTask
```

---

## Deployment

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    depends_on:
      - redis
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0

  celery_beat:
    build: .
    command: celery -A app.tasks beat --loglevel=info
    depends_on:
      - redis
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0

  flower:
    build: .
    command: celery -A app.tasks flower
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

### Production Deployment (Supervisor)

```ini
[program:celery_worker]
command=celery -A myproject worker -Q default,high,email --concurrency=4
directory=/app
user=app
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker-error.log

[program:celery_beat]
command=celery -A myproject beat
directory=/app
user=app
numprocs=1
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat-error.log
```

### Kubernetes (Production)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: worker
        image: myapp:latest
        command: ["celery", "-A", "app.tasks", "worker", "-Q", "default,high", "--concurrency=4"]
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: CELERY_BROKER_URL
          valueFrom:
            secretKeyRef:
              name: celery-secrets
              key: broker-url
        - name: CELERY_RESULT_BACKEND
          valueFrom:
            secretKeyRef:
              name: celery-secrets
              key: result-backend
```

---

## Best Practices

### 1. Task Idempotency

Tasks should be safe to run multiple times:

```python
@app.task
def update_user_profile(user_id: int, data: dict):
    # BAD: Increments counter each time
    # user.counter += 1
    
    # GOOD: Sets to exact value (idempotent)
    user = User.objects.get(id=user_id)
    user.profile_data = data
    user.save()
```

### 2. Store Minimal Data

Only store IDs in tasks, fetch fresh data inside:

```python
# BAD: Entire user object (stale)
@app.task
def send_email(user_dict):
    send(user_dict['email'])

# GOOD: Just ID, fetch fresh
@app.task
def send_email(user_id: int):
    user = User.objects.get(id=user_id)
    send(user.email)
```

### 3. Task Timeouts

Always set soft + hard timeouts:

```python
@app.task(
    time_limit=1800,  # hard: 30 min
    soft_time_limit=1500  # soft: 25 min
)
def long_running_task():
    # Task gets SoftTimeLimitExceeded at 25 min
    # to clean up gracefully
    try:
        result = do_work()
    except SoftTimeLimitExceeded:
        logger.info("Task time limit reached, saving progress...")
        save_progress()
        raise
```

### 4. Use Task Routing

Never mix high-priority with background tasks:

```python
# BAD: All tasks in one queue
@app.task
def send_password_reset(user_id):
    pass

@app.task
def generate_monthly_report():
    pass

# GOOD: Separate queues by SLA
@app.task(queue='high')
def send_password_reset(user_id):
    pass

@app.task(queue='reports')
def generate_monthly_report():
    pass
```

### 5. Visibility & Logging

Always log task entry/exit:

```python
@app.task(bind=True)
def process_payment(self, payment_id: int):
    logger.info(f"Processing payment {payment_id} [task_id: {self.request.id}]")
    
    try:
        payment = Payment.objects.get(id=payment_id)
        result = charge_card(payment)
        logger.info(f"Payment {payment_id} succeeded")
        return result
    except Exception as e:
        logger.error(f"Payment {payment_id} failed: {e}")
        raise
```

### 6. Monitor Queue Depth

Alert if queues pile up:

```python
from celery import current_app

@app.task
def check_queue_depth():
    inspector = current_app.control.inspect()
    reserved = inspector.reserved()
    
    for worker, tasks in (reserved or {}).items():
        depth = len(tasks)
        if depth > 1000:
            send_alert(f"Queue depth high on {worker}: {depth}")
```

### 7. Test Both Sync & Async

```python
def test_send_email():
    # Test synchronously in tests
    result = send_email.apply(args=["test@example.com"])
    assert result.successful()
    assert "sent" in result.result.lower()

@pytest.fixture
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,  # Run sync in tests
    }
```

---

## Troubleshooting

### Tasks Not Running

```bash
# Check worker is running
celery -A myapp inspect active

# Check tasks are registered
celery -A myapp inspect registered

# Check queue has messages
redis-cli KEYS 'celery*'
```

### Memory Leaks in Worker

```python
# Set max tasks before restart
@app.task
def task():
    pass

# In worker config
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart after 1000 tasks
```

### Duplicate Task Execution

```python
# Prevent with idempotency key
@app.task(bind=True)
def process_order(self, order_id: int):
    # Check if already processed
    if Order.objects.filter(id=order_id, processed=True).exists():
        return "Already processed"
    
    # Process
    order = Order.objects.get(id=order_id)
    order.process()
    order.processed = True
    order.save()
```

---

## CLI Usage

```bash
# Scaffold new project
python cli.py scaffold --name myproject --framework fastapi --broker redis

# Validate config
python cli.py validate --config celery.conf.json

# Initialize config template
python cli.py init-config --broker redis --output celery.conf.json

# Start worker
python cli.py worker --queues default,high --concurrency 4

# Start scheduler
python cli.py beat

# Start monitoring
python cli.py flower

# Generate Docker
python cli.py docker --framework fastapi --output Dockerfile.worker
```

---

## Resources

- [Celery Docs](https://docs.celeryproject.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Django Celery Docs](https://docs.celeryproject.io/en/stable/django/)
- [Flower Docs](https://flower.readthedocs.io/)
