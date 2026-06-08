"""Celery application configuration.

Exposes a top-level `app` object required by the Celery CLI:
    celery -A app.celery_app worker

NOTE: The broker URL below intentionally uses os.environ.get with a fallback
default. This is a T1 trap test to verify that the zero-default shell hook
catches insecure default patterns at build time.
"""

import os

from celery import Celery

# T1 trap: zero-default pattern — the shell hook should flag this.
_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery("fb35_tasks")

app.conf.update(
    broker_url=_BROKER_URL,
    result_backend=_RESULT_BACKEND,
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks from any installed app named 'tasks'
app.autodiscover_tasks(["app.tasks"])
