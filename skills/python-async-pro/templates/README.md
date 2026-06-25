# FastAPI + Celery + RabbitMQ Templates

Complete production-ready templates for async task processing.

## Files

- `fastapi-celery-base.py` — Complete FastAPI app with Celery integration
- `celery_config.py` — Celery configuration (queues, retries, scheduling)
- `docker-compose.yml` — Docker setup (PostgreSQL, RabbitMQ, Redis, workers)
- `Dockerfile` — Python app container
- `requirements.txt` — Python dependencies
- `README.md` — This file

## Quick Start

### 1. Setup Project Structure

```bash
mkdir async-project
cd async-project

# Copy template files
cp fastapi-celery-base.py main.py
cp celery_config.py .
cp docker-compose.yml .
cp Dockerfile .
cp requirements.txt .
```

### 2. Configure Environment

Create `.env`:

```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/async_db
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

Services:
- FastAPI: http://localhost:8000
- Flower (monitoring): http://localhost:5555
- RabbitMQ (management): http://localhost:15672
- PostgreSQL: localhost:5432

### 4. Test API

```bash
# Create task
curl -X POST http://localhost:8000/tasks/process \
  -H "Content-Type: application/json" \
  -d '{"data":"hello","priority":"default"}'

# Check status
curl http://localhost:8000/tasks/{task_id}

# Send email
curl -X POST http://localhost:8000/tasks/send-email \
  -d "email=user@example.com&subject=Test&body=Hello"

# Generate report
curl -X POST http://localhost:8000/tasks/generate-report \
  -H "Content-Type: application/json" \
  -d '{"report_type":"sales","filters":{"year":2024}}'
```

## Architecture

```
FastAPI App
    ↓
RabbitMQ (Message Broker)
    ↓
Celery Workers (default, high, low priority)
    ↓
Task Results → Redis Cache
```

## Customization

### Add New Task

```python
@celery_app.task(
    name="my_task",
    queue="default",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5}
)
def my_task(self: Task, param1: str):
    """Your task implementation"""
    try:
        result = process(param1)
        return {"status": "success", "result": result}
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)
```

### Add FastAPI Route

```python
@app.post("/tasks/my-task")
async def create_my_task(param1: str):
    task = my_task.apply_async(
        args=[param1],
        queue="default"
    )
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Task {task.id} queued"
    )
```

### Scale Workers

In `docker-compose.yml`, add more workers:

```yaml
celery_worker_extra:
  build:
    context: .
    dockerfile: Dockerfile
  command: celery -A celery_app worker --loglevel=info --queue=default -c 4
  # ... rest of config
```

### Change Queue Priority

```python
# For high priority tasks, more concurrency
celery_worker_high:
  command: celery -A celery_app worker --loglevel=info --queue=high_priority -c 8

# For low priority, fewer workers
celery_worker_low:
  command: celery -A celery_app worker --loglevel=info --queue=low_priority -c 2
```

## Monitoring

### Flower Web UI

Visit http://localhost:5555

- Active tasks
- Worker stats
- Task history
- Queue status
- Pool size

### Logs

```bash
# View app logs
docker-compose logs app

# View worker logs
docker-compose logs celery_worker_default

# Follow logs
docker-compose logs -f app
```

### RabbitMQ Management

Visit http://localhost:15672 (guest/guest)

- Queue status
- Message rates
- Connection info

### Redis CLI

```bash
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Get task result
GET celery-task-meta-{task_id}

# Monitor activity
MONITOR
```

## Production Considerations

### 1. Security

- Change RabbitMQ default credentials
- Use SSL/TLS for connections
- Set strong Celery SECRET_KEY
- Use Redis with password

### 2. Scaling

- Use separate Redis instances for different purposes
- Run multiple worker instances
- Use Celery autoscaling
- Monitor queue depths

### 3. Reliability

- Enable task persistence (RabbitMQ)
- Configure result expiry appropriately
- Implement retry logic with backoff
- Use task acknowledgment

### 4. Monitoring

- Set up Prometheus metrics
- Configure alerting for stuck tasks
- Monitor worker health
- Track queue depths

### 5. Database Connections

```python
# Properly handle DB connections in tasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@celery_app.task
def task_with_db():
    session = SessionLocal()
    try:
        # Do work
        pass
    finally:
        session.close()
```

## Performance Tuning

### Worker Concurrency

```bash
# CPU-bound: set to CPU count
celery -A celery_app worker -c 4

# I/O-bound: set higher (10-50)
celery -A celery_app worker -c 20 -l info
```

### Prefetch

```bash
# Task distribution strategy
celery -A celery_app worker --prefetch-multiplier=4
```

### Time Limits

```python
# In task definition
@celery_app.task(
    time_limit=600,  # Hard limit 10 min
    soft_time_limit=540  # Soft limit 9 min
)
def long_task():
    # Will be terminated after hard limit
    pass
```

## Troubleshooting

### Tasks not running

1. Check RabbitMQ connection
   ```bash
   docker-compose logs rabbitmq
   ```

2. Check worker is consuming from queue
   ```bash
   docker-compose logs celery_worker_default
   ```

3. Verify task routing in celery_config.py

### High memory usage

- Reduce worker concurrency
- Enable task result cleanup
- Limit result expiry time

### Tasks timing out

- Increase time_limit
- Check for deadlocks in task code
- Use asyncio for I/O operations

### Messages not being processed

- Check queue bindings in RabbitMQ
- Verify task names match
- Check worker queue subscriptions

---

Last Updated: 2026-06-25
