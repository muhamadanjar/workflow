"""
Professional Python Async/Background Tasks Framework

Provides templates, utilities, and documentation for:
- FastAPI + Celery
- Django + Celery
- RQ (Redis Queue)
- APScheduler

Usage:
    from python_async_pro import scaffold_project, validate_config
"""

__version__ = "1.0.0"
__author__ = "Professional Python Dev"

from .cli import cli

__all__ = ["cli"]
