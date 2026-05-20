# FastAPI + RabbitMQ + Pika Guide

FastAPI projects use **RabbitMQ with Pika** as default broker (lightweight, efficient, battle-tested).

## Architecture

```
FastAPI API
    ↓
Pika Client (AMQP 0.9.1)
    ↓
RabbitMQ Broker
    ↓
Celery Worker (consumes messages)
    ↓
Task Execution
```

## Setup

### 1. Install Dependencies

```bash
pip install celery==5.3.4 pika==1.3.2 redis==5.0.1 fastapi uvicorn
```

### 2. Start RabbitMQ

**Docker (recommended):**
```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management-alpine
```

Access Management UI: http://localhost:15672 (guest/guest)

**Local:**
```bash
# macOS
brew install rabbitmq
brew services start rabbitmq

# Linux (Ubuntu)
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server

# Check status
rabbitmqctl status
```

### 3. Configure Celery (Pika + Redis Results)

```python
from celery import Celery
from kombu import Queue, Exchange

app = Celery("myapp")

app.conf.update(
    # RabbitMQ Broker (Pika driver)
    broker_url="amqp://guest:guest@localhost:5672//",
    
    # Redis for Results (faster than RabbitMQ RPC)
    result_backend="redis://localhost:6379/0",
    
    # Pika Settings
    broker_connection_retry_on_startup=True,
    broker_heartbeat=30,  # Keep connection alive
    broker_pool_limit=10,
    
    # Queues
    task_queues=(
        Queue("high", Exchange("high"), routing_key="high", priority=10),
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("email", Exchange("email"), routing_key="email"),
    ),
    
    # Timeouts
    task_time_limit=30 * 60,    # Hard: 30 min
    task_soft_time_limit=25 * 60,  # Soft: 25 min
)
```

### 4. Define Tasks

```python
@app.task(queue="high")
def send_password_reset(user_id: int):
    """Critical task - high priority"""
    user = User.objects.get(id=user_id)
    send_reset_email(user.email)

@app.task(queue="email")
def send_newsletter(newsletter_id: int):
    """Background task - lower priority"""
    newsletter = Newsletter.objects.get(id=newsletter_id)
    send_to_subscribers(newsletter)
```

### 5. FastAPI Integration

```python
from fastapi import FastAPI
from celery_config import app as celery_app

app = FastAPI()

@app.post("/reset-password")
async def reset_password(user_id: int):
    # Queue high-priority task
    task = send_password_reset.delay(user_id)
    return {"task_id": task.id, "status": "queued"}

@app.get("/task/{task_id}/status")
async def get_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

## Running

### Terminal 1: FastAPI
```bash
uvicorn main:app --reload
```

### Terminal 2: Celery Worker
```bash
# Single queue (development)
celery -A celery_config worker --loglevel=info

# Multi-queue (production)
celery -A celery_config worker -Q high,default,email --concurrency=4 --loglevel=info
```

### Terminal 3: Beat (Periodic Tasks)
```bash
celery -A celery_config beat --loglevel=info
```

### Terminal 4: Flower (Monitor)
```bash
celery -A celery_config flower --port=5555
```

Access: http://localhost:5555

## Pika Configuration Options

### Connection Settings

```python
app.conf.update(
    # Automatic retry on startup failure
    broker_connection_retry_on_startup=True,
    
    # Max retries before giving up
    broker_connection_max_retries=10,
    
    # Heartbeat to detect dead connections
    broker_heartbeat=30,  # seconds
    
    # Max connections in pool
    broker_pool_limit=10,
    
    # Authentication method
    broker_login_method="PLAIN",
)
```

### Queue Durability (Survives Broker Restart)

```python
from kombu import Queue, Exchange

Queue(
    "important_queue",
    Exchange("important", type="direct", durable=True),
    routing_key="important",
    durable=True,  # Queue survives broker restart
    queue_arguments={"x-max-priority": 10}  # Enable priorities
)
```

### Task Routing

```python
# Routes tasks to specific queues based on task name
task_routes = {
    "app.tasks.send_password_reset": {"queue": "high"},
    "app.tasks.send_email": {"queue": "email"},
    "app.tasks.generate_report": {"queue": "processing"},
}
```

## RabbitMQ Management

### Queue Monitoring

```bash
# List all queues
rabbitmqctl list_queues name messages consumers

# Purge queue (delete all messages)
rabbitmqctl purge_queue queue_name

# Delete queue
rabbitmqctl delete_queue queue_name
```

### User Management

```bash
# Add user
rabbitmqctl add_user myuser mypassword

# Set permissions
rabbitmqctl set_permissions -p "/" myuser ".*" ".*" ".*"

# List users
rabbitmqctl list_users
```

### Management UI

Access: http://localhost:15672
- Default: guest/guest
- View queues, messages, connections
- Manage users and permissions

## Comparison: Pika vs Alternatives

### Pika (RabbitMQ) ✅ **FASTAPI DEFAULT**
- **Pros:**
  - Lightweight (minimal overhead)
  - Fast message delivery
  - Durable queues (survives restarts)
  - Priority queues
  - AMQP standard
- **Cons:**
  - Requires separate RabbitMQ server
  - More infrastructure

### Redis (Celery Default)
- **Pros:**
  - Simple setup
  - One less service (if already used for caching)
- **Cons:**
  - Not designed for messaging (can lose messages)
  - No native durability
  - Less reliable for critical tasks

### Kombu (Generic)
- **Pros:**
  - Abstraction over multiple brokers
- **Cons:**
  - Extra layer overhead
  - Slower than native drivers

## Best Practices

### 1. Use Separate Result Backend

```python
# Don't use RabbitMQ for results (inefficient)
# ❌ result_backend="rpc://"

# Use Redis for results (10x faster)
# ✅ result_backend="redis://localhost:6379/0"
```

### 2. Set Appropriate Timeouts

```python
# Hard limit: task killed forcefully
task_time_limit=30 * 60,

# Soft limit: graceful shutdown attempt
task_soft_time_limit=25 * 60,
```

### 3. Use Queue Priorities

```python
# High-priority (critical) tasks
Queue("high", Exchange("high"), priority=10)

# Low-priority (background) tasks
Queue("reports", Exchange("reports"), priority=1)

# Route accordingly
task_routes = {
    "app.tasks.payment.*": {"queue": "high"},
    "app.tasks.reports.*": {"queue": "reports"},
}
```

### 4. Monitor Connection Health

```python
# Check worker connectivity
celery -A celery_config inspect ping

# View active tasks
celery -A celery_config inspect active

# View reserved tasks
celery -A celery_config inspect reserved
```

### 5. Handle Connection Failures

```python
@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def reliable_task(self):
    try:
        # Task body
        return result
    except Exception as e:
        # Automatically retried on connection error
        raise self.retry(exc=e, countdown=60)
```

## Troubleshooting

### "Cannot connect to broker"

```bash
# Verify RabbitMQ is running
docker ps | grep rabbitmq

# Or check local process
rabbitmqctl status

# Test connection manually
python -c "
import pika
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
print('Connected to RabbitMQ')
"
```

### "Queue not found"

```bash
# Check if queues exist (they auto-create on first use)
rabbitmqctl list_queues

# Or wait for worker to start and declare queues
celery -A celery_config worker --loglevel=info
```

### "Tasks not processing"

```bash
# Check worker is consuming from correct queue
celery -A celery_config inspect active

# Check if tasks are routed correctly
celery -A celery_config inspect registered

# View queue depth
rabbitmqctl list_queues name messages
```

### High Memory Usage

```python
# Limit tasks per worker process
worker_max_tasks_per_child=1000  # Restart after 1000 tasks

# Restart workers periodically
worker_recycle_type="time"
worker_max_tasks_per_child=1000
```

## Docker Compose (Full Stack)

```yaml
version: '3.8'
services:
  rabbitmq:
    image: rabbitmq:4-management-alpine
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # UI
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - rabbitmq
      - redis
    command: uvicorn main:app --reload

  worker:
    build: .
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - rabbitmq
      - redis
    command: celery -A celery_config worker --loglevel=info

  flower:
    build: .
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
    depends_on:
      - rabbitmq
    command: celery -A celery_config flower --port=5555
```

Run: `docker-compose up`

Access:
- API: http://localhost:8000
- RabbitMQ UI: http://localhost:15672
- Flower: http://localhost:5555

## Production Deployment

### Kubernetes

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
        command: ["celery", "-A", "celery_config", "worker", 
                  "-Q", "high,default,email", "--concurrency=4"]
```

### Supervisor

```ini
[program:celery_worker]
command=celery -A celery_config worker -Q high,default,email --concurrency=4
directory=/app
user=appuser
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker-error.log

[program:celery_beat]
command=celery -A celery_config beat
directory=/app
user=appuser
numprocs=1
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
```

## Resources

- [Pika Documentation](https://pika.readthedocs.io/)
- [RabbitMQ Tutorial](https://www.rabbitmq.com/getstarted.html)
- [Celery with RabbitMQ](https://docs.celeryproject.io/en/stable/broker/rabbitmq/)
- [RabbitMQ Management](https://www.rabbitmq.com/management.html)
