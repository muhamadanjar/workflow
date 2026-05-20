#!/usr/bin/env python3
"""
MCP Server: Python Async/Background Tasks Professional Skill
Provides tools for scaffolding FastAPI/Django projects with background job support
"""
import json
import subprocess
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("python-async-pro")

TEMPLATES_DIR = Path(__file__).parent / "templates"


@server.call_tool
def scaffold_fastapi_celery(project_name: str, use_redis: bool = True) -> str:
    """Scaffold FastAPI project with Celery background tasks"""
    template = (TEMPLATES_DIR / "fastapi_celery.py").read_text()
    template = template.replace("{{PROJECT_NAME}}", project_name)
    return template


@server.call_tool
def scaffold_django_celery(project_name: str) -> str:
    """Scaffold Django project with Celery background tasks"""
    template = (TEMPLATES_DIR / "django_celery.py").read_text()
    template = template.replace("{{PROJECT_NAME}}", project_name)
    return template


@server.call_tool
def validate_worker_config(config_path: str) -> dict:
    """Validate Celery/background worker configuration"""
    config = json.loads(Path(config_path).read_text())
    errors = []
    warnings = []

    if "broker_url" not in config:
        errors.append("Missing broker_url (Redis, RabbitMQ, etc)")
    if "result_backend" not in config:
        errors.append("Missing result_backend for task results")
    if "task_time_limit" not in config:
        warnings.append("No task_time_limit set (recommend: 30 minutes)")
    if "task_soft_time_limit" not in config:
        warnings.append("No task_soft_time_limit set (recommend: 25 minutes)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


@server.call_tool
def generate_task_template(framework: str, task_type: str) -> str:
    """Generate task template (framework: fastapi|django, task_type: async|periodic|retry)"""
    filename = f"{framework}_{task_type}_task.py"
    template_path = TEMPLATES_DIR / filename

    if not template_path.exists():
        return f"Template not found: {filename}"

    return template_path.read_text()


@server.call_tool
def generate_worker_dockerfile(framework: str) -> str:
    """Generate production-ready Dockerfile for worker"""
    filename = f"Dockerfile.{framework}_worker"
    template_path = TEMPLATES_DIR / filename

    if not template_path.exists():
        return f"Dockerfile not found: {filename}"

    return template_path.read_text()


@server.call_tool
def list_templates() -> list:
    """List all available templates"""
    templates = []
    for f in TEMPLATES_DIR.glob("*.py"):
        templates.append({
            "name": f.stem,
            "type": "template"
        })
    return templates


if __name__ == "__main__":
    server.run()
