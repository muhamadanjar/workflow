#!/usr/bin/env python3
"""
CLI utility for professional Python async/background task scaffolding
Supports FastAPI, Django with Celery, RQ, APScheduler
"""
import click
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

TEMPLATES_DIR = Path(__file__).parent / "templates"
PROJECT_ROOT = Path.cwd()


# ============================================================
# Scaffolding Commands
# ============================================================

@click.group()
def cli():
    """Professional Python Async Task Framework"""
    pass


@cli.command()
@click.option("--name", prompt="Project name", help="Project name")
@click.option(
    "--framework",
    type=click.Choice(["fastapi", "django"]),
    default="fastapi",
    prompt="Framework",
)
@click.option(
    "--broker",
    type=click.Choice(["redis", "rabbitmq"]),
    default="redis",
    prompt="Broker (Redis/RabbitMQ)",
)
@click.option("--output", default=".", help="Output directory")
def scaffold(name: str, framework: str, broker: str, output: str):
    """Scaffold a new project with async task support"""
    output_path = Path(output) / name
    output_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"🚀 Scaffolding {framework.upper()} project: {name}")

    # Create directory structure
    dirs = [
        output_path / name,
        output_path / name / "tasks",
        output_path / name / "config",
        output_path / "tests",
        output_path / "docker",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✓ Created {d.relative_to(output_path)}")

    # Copy templates
    if framework == "fastapi":
        _scaffold_fastapi(name, output_path, broker)
    else:
        _scaffold_django(name, output_path, broker)

    click.secho(
        f"\n✅ Project scaffolded at: {output_path}",
        fg="green",
        bold=True
    )
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {output_path}")
    click.echo(f"  pip install -r requirements.txt")
    click.echo(f"  python -m uvicorn main:app --reload")


def _scaffold_fastapi(name: str, path: Path, broker: str):
    """Scaffold FastAPI project structure (default: RabbitMQ with Pika)"""
    broker_url = "amqp://guest:guest@localhost:5672//" if broker == "rabbitmq" else "redis://localhost:6379/0"

    # Main app file
    main_py = f"""
from fastapi import FastAPI
from {name}.config.celery_config import app as celery_app
from {name}.tasks import tasks

app = FastAPI(title="{name}")

@app.on_event("startup")
async def startup():
    print("Server starting...")

@app.on_event("shutdown")
async def shutdown():
    print("Server shutting down...")

@app.get("/health")
async def health():
    return {{"status": "ok"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    (path / "main.py").write_text(main_py)
    click.echo(f"  ✓ Created main.py")

    # Celery config
    celery_cfg = f"""
from celery import Celery
from kombu import Queue, Exchange

app = Celery("{name}")
app.conf.update(
    broker_url="{broker_url}",
    result_backend="redis://localhost:6379/1",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
"""
    (path / name / "config" / "celery_config.py").write_text(celery_cfg)
    click.echo(f"  ✓ Created config/celery_config.py")

    # Sample task
    sample_task = f"""
from {name}.config.celery_config import app

@app.task
def sample_task(x: int, y: int):
    return x + y

@app.task
def health_check():
    return "OK"
"""
    (path / name / "tasks" / "__init__.py").write_text(sample_task)
    click.echo(f"  ✓ Created tasks/__init__.py")


def _scaffold_django(name: str, path: Path, broker: str):
    """Scaffold Django project structure"""
    broker_url = "redis://localhost:6379/0" if broker == "redis" else "amqp://guest@localhost//"

    # Celery app
    celery_py = f"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')

app = Celery('{name}')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {{self.request!r}}')
"""
    (path / name / "celery.py").write_text(celery_py)
    click.echo(f"  ✓ Created celery.py")

    # Tasks module
    tasks_py = f"""
from celery import shared_task

@shared_task
def sample_task(x: int, y: int):
    return x + y

@shared_task
def health_check():
    return "OK"
"""
    (path / name / "tasks.py").write_text(tasks_py)
    click.echo(f"  ✓ Created tasks.py")


@cli.command()
@click.option("--config", prompt="Config file path", help="Celery config file")
def validate(config: str):
    """Validate Celery/worker configuration"""
    config_path = Path(config)

    if not config_path.exists():
        click.secho(f"❌ Config not found: {config}", fg="red")
        return

    try:
        config_data = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        click.secho(f"❌ Invalid JSON: {config}", fg="red")
        return

    errors = []
    warnings = []

    # Validate required fields
    required = ["broker_url", "result_backend"]
    for field in required:
        if field not in config_data:
            errors.append(f"Missing required field: {field}")

    # Check timeouts
    if "task_time_limit" not in config_data:
        warnings.append("No task_time_limit (recommend: 1800)")
    if "task_soft_time_limit" not in config_data:
        warnings.append("No task_soft_time_limit (recommend: 1500)")

    # Validate broker
    broker = config_data.get("broker_url", "")
    if not broker.startswith(("redis://", "amqp://", "sqs://")):
        errors.append(f"Invalid broker URL: {broker}")

    # Display results
    if errors:
        click.secho("❌ Validation failed:", fg="red", bold=True)
        for err in errors:
            click.echo(f"  • {err}")
    else:
        click.secho("✅ Validation passed", fg="green", bold=True)

    if warnings:
        click.secho("\n⚠️  Warnings:", fg="yellow")
        for warn in warnings:
            click.echo(f"  • {warn}")

    return len(errors) == 0


@cli.command()
@click.option("--broker", default="rabbitmq", help="Broker type (rabbitmq|redis)")
@click.option("--output", default="celery.conf.json", help="Output config file")
def init_config(broker: str, output: str):
    """Initialize Celery configuration template (FastAPI default: RabbitMQ + Pika)"""
    if broker == "rabbitmq":
        broker_url = "amqp://guest:guest@localhost:5672//"
        result_backend = "redis://localhost:6379/0"  # Use Redis for results
    else:
        broker_url = "redis://localhost:6379/0"
        result_backend = "redis://localhost:6379/1"

    config = {
        "broker_url": broker_url,
        "result_backend": result_backend,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
        "task_time_limit": 1800,
        "task_soft_time_limit": 1500,
        "task_autoretry_for": ["Exception"],
        "task_max_retries": 3,
        "task_default_retry_delay": 60,
        "task_routes": {
            "*.high_priority.*": {"queue": "high"},
            "*.email.*": {"queue": "email"},
        },
    }

    output_path = Path(output)
    output_path.write_text(json.dumps(config, indent=2))

    click.secho(f"✅ Config generated: {output_path}", fg="green")


@cli.command()
@click.option("--queues", default="default", help="Queues (comma-separated)")
@click.option("--concurrency", default=4, help="Worker concurrency")
@click.option("--loglevel", default="info", help="Log level")
def worker(queues: str, concurrency: int, loglevel: str):
    """Start Celery worker (development)"""
    cmd = [
        "celery",
        "-A",
        "celery_app",
        "worker",
        f"-Q {queues}",
        f"--concurrency={concurrency}",
        f"--loglevel={loglevel}",
    ]

    click.echo(f"🚀 Starting Celery worker...")
    click.echo(f"  Queues: {queues}")
    click.echo(f"  Concurrency: {concurrency}")
    click.echo(f"  Log level: {loglevel}")
    click.echo(f"\nCommand: {' '.join(cmd)}\n")

    subprocess.run(" ".join(cmd), shell=True)


@cli.command()
def beat():
    """Start Celery Beat scheduler"""
    click.echo("🚀 Starting Celery Beat scheduler...")
    subprocess.run("celery -A celery_app beat --loglevel=info", shell=True)


@cli.command()
def flower():
    """Start Flower monitoring UI"""
    click.echo("🌸 Starting Flower (http://localhost:5555)...")
    subprocess.run("celery -A celery_app flower", shell=True)


@cli.command()
@click.option("--framework", type=click.Choice(["fastapi", "django"]), prompt="Framework")
@click.option("--output", default="Dockerfile.worker", help="Output file")
def docker(framework: str, output: str):
    """Generate production Dockerfile for worker"""
    if framework == "fastapi":
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "app.tasks.celery_app", "worker", \\
     "-Q", "default,high,email", \\
     "--concurrency=4", \\
     "--loglevel=info"]
"""
    else:
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "config", "worker", \\
     "-Q", "default,high,email", \\
     "--concurrency=4", \\
     "--loglevel=info"]
"""

    Path(output).write_text(dockerfile.strip())
    click.secho(f"✅ Dockerfile generated: {output}", fg="green")


# ============================================================
# Info & Help Commands
# ============================================================

@cli.command()
def templates():
    """List available templates"""
    click.echo("Available templates:")
    for template in TEMPLATES_DIR.glob("*.py"):
        click.echo(f"  • {template.stem}")


@cli.command()
@click.option("--format", type=click.Choice(["json", "text"]), default="text")
def status(format: str):
    """Show project async task configuration status"""
    config_files = list(PROJECT_ROOT.glob("**/celery*.py")) + \
                   list(PROJECT_ROOT.glob("**/celery*.json")) + \
                   list(PROJECT_ROOT.glob("**/*tasks*.py"))

    if format == "json":
        click.echo(json.dumps({
            "config_files": [str(f.relative_to(PROJECT_ROOT)) for f in config_files],
            "count": len(config_files)
        }))
    else:
        click.echo("Async configuration files found:")
        for f in config_files:
            click.echo(f"  • {f.relative_to(PROJECT_ROOT)}")
        click.echo(f"\nTotal: {len(config_files)} files")


if __name__ == "__main__":
    cli()
