from __future__ import annotations

from redis import Redis
from rq import Connection, Worker

from .config import settings
from .jobs import ingest_dataset, validate_upload, run_dataset_analysis  # noqa: F401 - imported for worker discovery

QUEUES = ["default"]


def run_worker() -> None:
    """Entry point for running an RQ worker programmatically."""
    redis_conn = Redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        worker = Worker(QUEUES)
        worker.work()


if __name__ == "__main__":
    run_worker()
