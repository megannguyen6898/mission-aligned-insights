import os
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from backend.app.observability.events import log_event

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
WORKER_CONCURRENCY = int(os.environ.get("WORKER_CONCURRENCY", "2"))

app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_concurrency=WORKER_CONCURRENCY,
    task_default_queue="ingest",
)

class BaseTask(app.Task):
    """Task base class with automatic retries and backoff."""

    autoretry_for = (Exception,)
    retry_backoff = True
    retry_jitter = True


@app.task(bind=True, base=BaseTask)
def ping(self):
    """Simple task used for worker heartbeats in tests."""
    return "pong"


ORG_ID = os.getenv("ORG_ID")
PROJECT_ID = os.getenv("PROJECT_ID")


@worker_ready.connect
def _on_worker_ready(**_):
    log_event("worker_ready", org_id=ORG_ID, project_id=PROJECT_ID)


@worker_shutdown.connect
def _on_worker_shutdown(**_):
    log_event("worker_shutdown", org_id=ORG_ID, project_id=PROJECT_ID)

# Ensure tasks are registered
from .tasks import ingest_excel_or_csv, recompute_metrics  # noqa: F401
