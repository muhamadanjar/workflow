# Celery - Python Task Queue

## Setup

```python
from celery import Celery
from kombu import Exchange, Queue

# Create Celery app
app = Celery('myapp')

# Configure
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure queues
app.conf.task_queues = (
    Queue('default', Exchange('tasks'), routing_key='task.#'),
    Queue('high_priority', Exchange('high'), routing_key='high.#'),
    Queue('low_priority', Exchange('low'), routing_key='low.#'),
)
```

## Define Tasks

```python
@app.task
def send_email(to, subject, body):
    """Send email task"""
    # Do work
    return f"Email sent to {to}"

@app.task(bind=True, max_retries=3)
def process_image(self, image_path):
    """Task with retry"""
    try:
        # Process image
        return f"Processed {image_path}"
    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@app.task(queue='high_priority', rate_limit='100/m')
def critical_task():
    """High priority, rate limited"""
    return "Critical work done"
```

## Execute Tasks

```python
# Asynchronous (fire and forget)
send_email.delay(to='user@example.com', subject='Test', body='Hello')

# Get result
result = send_email.delay(to='user@example.com', subject='Test', body='Hello')
print(result.get(timeout=30))  # Wait for result

# Schedule execution
send_email.apply_async(
    (to, subject, body),
    countdown=60  # Execute in 60 seconds
)

# Send to specific queue
send_email.apply_async(
    args=(to, subject, body),
    queue='high_priority'
)

# Chain tasks
from celery import chain
workflow = chain(
    process_image.s('image.jpg'),
    send_email.s('user@example.com', 'Ready')
)
workflow.apply_async()

# Group (parallel)
from celery import group
job = group(
    send_email.s(to, subject, body)
    for to in recipient_list
)
job.apply_async()
```

## Monitor Tasks

```python
from celery.result import AsyncResult

# Get task result
result = AsyncResult('task-id')
print(result.state)        # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE'
print(result.result)       # Task return value
print(result.info)         # Progress info
print(result.traceback)    # Error traceback

# Check if ready
if result.ready():
    print(result.get())

# Wait with timeout
try:
    result.get(timeout=30)
except Exception as e:
    print(f"Task failed: {e}")
```

## Worker

```bash
# Start worker
celery -A myapp worker --loglevel=info

# Multiple workers
celery -A myapp worker --concurrency=4

# Specific queue
celery -A myapp worker -Q high_priority,default

# With autoscale
celery -A myapp worker --autoscale=10,3  # Max 10, min 3
```

## Error Handling

```python
@app.task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5})
def robust_task():
    """Auto-retry on exception"""
    # Work
    pass

@app.task(bind=True)
def task_with_fallback(self):
    try:
        # Primary work
        pass
    except Exception as exc:
        if self.request.retries < 3:
            self.retry(exc=exc, countdown=60)
        else:
            # Fallback logic
            handle_failure()
```

## Periodic Tasks

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-email-every-hour': {
        'task': 'myapp.tasks.send_email',
        'schedule': crontab(minute=0),  # Every hour
        'args': (to, subject, body)
    },
    'cleanup-daily': {
        'task': 'myapp.tasks.cleanup',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    }
}
```

## Best Practices

- ✅ Use result backend for long tasks
- ✅ Set task timeouts
- ✅ Handle retries with exponential backoff
- ✅ Use multiple queues for prioritization
- ✅ Monitor task metrics
- ✅ Set task rate limits
- ✅ Use task signatures for chaining
