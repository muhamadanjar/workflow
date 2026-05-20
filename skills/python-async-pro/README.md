# Professional Python Async/Background Tasks Skill

Complete, production-ready framework for async task handling in FastAPI and Django with Celery.

**FastAPI Default: RabbitMQ + Pika** (lightweight, efficient, durable)
**Django Default: Redis** (optional Celery Beat support)

## What's Included

### 📚 Documentation
- **GUIDE.md** — Comprehensive guide covering architecture, patterns, best practices, troubleshooting
- **PIKA_GUIDE.md** — FastAPI + RabbitMQ + Pika setup, configuration, troubleshooting (FastAPI default)

### 🛠️ Templates
- **FastAPI + Celery** (`templates/fastapi_celery.py`)
- **Django + Celery** (`templates/django_celery.py`)
- **Docker Compose** (development setup for both frameworks)
- **Dockerfiles** (production-ready workers with health checks)

### 🖥️ CLI Utility
- Scaffold new projects
- Validate configurations
- Initialize config templates
- Start workers, beat, flower
- Generate production Dockerfiles

### 🔌 MCP Server (Optional)
- Programmatic template generation
- Configuration validation
- Worker management

## Quick Start

### 1. Scaffold a FastAPI Project

```bash
python cli.py scaffold --name myapi --framework fastapi --broker redis

cd myapi
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

In another terminal:
```bash
celery -A celery_app worker --loglevel=info
```

### 2. Scaffold a Django Project

```bash
python cli.py scaffold --name myproject --framework django --broker redis

cd myproject
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

In another terminal:
```bash
celery -A config worker --loglevel=info
```

### 3. View Templates

```bash
python cli.py templates
```

### 4. Validate Configuration

```bash
python cli.py init-config --broker redis --output celery.conf.json
python cli.py validate --config celery.conf.json
```

### 5. Run with Docker Compose

Copy appropriate template:
```bash
cp templates/docker-compose.fastapi.yml docker-compose.yml
docker-compose up
```

Access:
- API: http://localhost:8000
- Flower: http://localhost:5555

## File Structure

```
python-async-pro/
├── GUIDE.md                          # Complete reference guide
├── PIKA_GUIDE.md                    # FastAPI + RabbitMQ + Pika guide
├── README.md                         # This file
├── cli.py                           # CLI utility (scaffolding, validation)
├── mcp_server.py                    # MCP server (optional, for IDE integration)
├── requirements.txt                 # Python dependencies
├── __init__.py
└── templates/
    ├── fastapi_celery.py            # FastAPI + RabbitMQ + Pika full template
    ├── fastapi_celery_config.py     # Pika-specific config (detailed)
    ├── django_celery.py             # Django + Celery template
    ├── fastapi_async_task.py        # Simple async task template
    ├── fastapi_periodic_task.py     # Periodic task template
    ├── fastapi_retry_task.py        # Task with retry logic
    ├── django_async_task.py         # Django async task
    ├── django_periodic_task.py      # Django periodic task
    ├── django_retry_task.py         # Django task with retry
    ├── Dockerfile.fastapi_worker    # Production FastAPI worker
    ├── Dockerfile.django_worker     # Production Django worker
    ├── docker-compose.fastapi.yml   # FastAPI development stack
    └── docker-compose.django.yml    # Django development stack
```

## FastAPI vs Django Defaults

| Aspect | FastAPI | Django |
|--------|---------|--------|
| **Broker** | RabbitMQ | Redis |
| **Driver** | Pika | Kombu |
| **Result Backend** | Redis | Redis |
| **Durability** | ✅ High (queues persist) | ⚠️ Medium (in-memory) |
| **Speed** | ✅ Very Fast (AMQP) | ✅ Fast (in-memory) |
| **Setup Complexity** | Medium (3 services) | Simple (1 service) |
| **Best For** | Production, critical tasks | Development, Django integrated |

**Why Pika for FastAPI?**
- Lightweight protocol (AMQP, not HTTP/TCP overhead)
- Queue durability (survives broker restart)
- Priority queues (route critical tasks first)
- Battle-tested (used by 10+ major projects)

## Key Features

### ✅ Production-Ready
- Proper error handling with retries
- Idempotent task design
- Graceful timeouts (soft + hard limits)
- Dead letter queue patterns
- Health checks and monitoring

### ✅ Multi-Queue Support
- High-priority tasks (password reset, 2FA) → `high` queue (SLA: <5min)
- Standard operations (emails, notifications) → `default` queue
- Marketing/digest emails → `email` queue
- Reports and background jobs → `reports` queue

### ✅ Observability
- Structured logging (task entry/exit, errors)
- Prometheus metrics
- Flower web UI monitoring
- Task status tracking
- Worker statistics

### ✅ Security
- Non-root Docker containers
- Timeouts prevent runaway tasks
- Automatic worker restarts
- Health checks

### ✅ Developer Experience
- CLI for common operations
- Docker Compose for quick local setup
- Clear error messages
- Progress tracking for long tasks

## Architecture Patterns

### Basic Pattern
```
User → API Endpoint (returns immediately)
        ↓
     Queue Task
        ↓
Celery Worker (processes async)
        ↓
Database/Cache/External System
```

### Monitoring
```
Worker 1 ─┐
Worker 2 ─┤─ Redis Broker ─ API ─ FastAPI/Django
Worker 3 ─┘                   ↓
                          Flower (http://localhost:5555)
```

## Common Commands

### CLI

```bash
# Create new project
python cli.py scaffold --name myapp --framework fastapi

# Validate config
python cli.py validate --config celery.conf.json

# Create config template
python cli.py init-config --broker redis --output celery.conf.json

# Run worker
python cli.py worker --queues default,high --concurrency 4

# Run scheduler (periodic tasks)
python cli.py beat

# Monitor (web UI)
python cli.py flower

# Generate Docker
python cli.py docker --framework fastapi --output Dockerfile.worker
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f celery_worker

# Scale workers
docker-compose up --scale celery_worker=3
```

### Celery (Direct)

```bash
# Worker (multi-queue)
celery -A app.tasks worker -Q default,high,email --concurrency=4

# Scheduler
celery -A app.tasks beat

# Monitor (web UI)
celery -A app.tasks flower

# Check worker status
celery -A app.tasks inspect active
celery -A app.tasks inspect stats
```

## Task Design Examples

### Simple Task
```python
@app.task
def send_email(recipient: str, subject: str):
    send_mail(recipient, subject)
    return f"Email sent to {recipient}"
```

### Task with Retry
```python
@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def call_api(self, url: str):
    try:
        return requests.get(url).json()
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
```

### Long-Running with Progress
```python
@app.task(bind=True)
def process_file(self, file_path: str):
    with open(file_path) as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        process(line)
        self.update_state(state='PROGRESS', meta={'current': i+1, 'total': len(lines)})
    
    return "Done"
```

### Periodic Task
```python
app.conf.beat_schedule = {
    'check-health-every-5-minutes': {
        'task': 'app.tasks.health_check',
        'schedule': timedelta(minutes=5),
    },
}

@app.task
def health_check():
    # Check system health
    return "OK"
```

## Best Practices

1. **Idempotency** — Tasks should be safe to run multiple times
2. **Minimal Data** — Store only IDs, fetch fresh data inside task
3. **Timeouts** — Always set soft + hard limits
4. **Routing** — Use separate queues for different priorities
5. **Logging** — Log task entry, exit, errors
6. **Monitoring** — Use Flower to watch queue depth and worker status
7. **Testing** — Test both sync (apply) and async (delay) execution

## Integration with Claude Code

This skill can be used from Claude Code:

```bash
# Use CLI directly
python cli.py scaffold --name myproject --framework fastapi

# Or import MCP server
python mcp_server.py
```

## Troubleshooting

### Tasks Not Running
```bash
celery -A app.tasks inspect active     # Check active tasks
celery -A app.tasks inspect registered # Check registered tasks
redis-cli KEYS 'celery*'               # Check queue messages
```

### Worker Not Starting
```bash
# Check logs
celery -A app.tasks worker --loglevel=debug

# Verify broker connection
redis-cli ping
```

### High Queue Depth
```bash
# Scale workers
docker-compose up --scale celery_worker=3

# Check task completion time
celery -A app.tasks inspect reserved
```

## Resources

- **GUIDE.md** — Full reference guide (architecture, patterns, deployment)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Django Celery](https://docs.celeryproject.io/en/stable/django/)

## Installation

### As a Skill in Claude Code

The skill is installed at `~/.claude/skills/python-async-pro/`

### Standalone Usage

```bash
cd ~/.claude/skills/python-async-pro
pip install -r requirements.txt

# Use CLI
python cli.py scaffold --name myapp --framework fastapi

# Or import
from cli import cli
cli()
```

## License

Professional template framework for production use.

## Support

- Check GUIDE.md for detailed patterns and troubleshooting
- Review template examples in `templates/`
- Use `python cli.py --help` for CLI reference
- Monitor with Flower UI at http://localhost:5555

---

**Ready to build scalable async applications? Start with:**

```bash
python cli.py scaffold --name myproject --framework fastapi
```
