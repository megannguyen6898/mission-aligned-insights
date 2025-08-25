import os
import subprocess
import time

import pytest
from celery.contrib.testing.worker import start_worker


@pytest.fixture(scope="module")
def redis_server():
    proc = subprocess.Popen(["redis-server", "--save", "", "--appendonly", "no"])
    time.sleep(0.5)
    yield proc
    proc.terminate()
    proc.wait()


def test_worker_boots(redis_server, monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    from backend.worker.worker import app, ping

    with start_worker(app, concurrency=1):
        result = ping.delay()
        assert result.get(timeout=10) == "pong"
