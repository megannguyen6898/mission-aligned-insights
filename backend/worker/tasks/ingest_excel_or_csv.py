import time
from dataclasses import dataclass
from typing import Dict, Any
import os
import time
from tempfile import NamedTemporaryFile

from celery import shared_task
from dataclasses import dataclass

from .recompute_metrics import recompute_metrics


@dataclass
class StepCounts:
    fetched: int = 0
    staged: int = 0
    loaded: int = 0


def _close_db(db) -> None:
    try:
        db.close()
    except Exception:
        pass


@shared_task(name="ingest_excel_or_csv")
def ingest_excel_or_csv(self, job_id: int) -> Dict[str, Any]:
    """Ingest an uploaded Excel/CSV file identified by an ingestion job."""
    from backend.app.database import SessionLocal
    from backend.app.models.ingestion_jobs import IngestionJob, IngestionJobStatus
    from backend.app.models.import_batches import ImportBatch, BatchStatus
    from backend.app.models.uploads import Upload
    from backend.app.observability.events import log_event
    from backend.app.ingest.parse_and_stage import parse_and_stage
    from backend.app.ingest.load_to_core import load_to_core
    from backend.app.services.analytics_service import AnalyticsService
    from backend.app.metabase.api import sync_schema
    from backend.app.storage.s3_client import get_s3_client

    start_time = time.time()
    db = SessionLocal()

    job: IngestionJob | None = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if job is None:
        _close_db(db)
        return {"status": "missing"}

    batch: ImportBatch | None = (
        db.query(ImportBatch).filter(ImportBatch.id == job.import_batch_id).first()
    )
    counts = StepCounts()

    try:
        job.status = IngestionJobStatus.running
        if batch is not None:
            batch.set_status(BatchStatus.running)
        db.commit()
        log_event("ingest_started", job_id=job.id, import_batch_id=job.import_batch_id)

        # fetch -------------------------------------------------------------
        log_event("ingest_fetch", job_id=job.id)
        upload = db.query(Upload).filter(Upload.id == job.upload_id).first()
        if upload is None:
            raise RuntimeError("Upload not found")
        bucket = os.environ.get("S3_BUCKET")
        s3 = get_s3_client()
        with NamedTemporaryFile(delete=False) as tmp:
            if bucket:
                s3.download_file(bucket, upload.object_key, tmp.name)
            else:
                s3.download_fileobj(None, upload.object_key, tmp)  # type: ignore[arg-type]
            temp_path = tmp.name
        counts.fetched = 1

        # stage -------------------------------------------------------------
        log_event("ingest_stage", job_id=job.id)
        staged_counts = parse_and_stage(
            upload_id=str(upload.id),
            import_batch_id=job.import_batch_id,
            file_path=temp_path,
            source_system="upload",
        )
        counts.staged = sum(staged_counts.values())

        # load --------------------------------------------------------------
        log_event("ingest_load", job_id=job.id)
        loaded = load_to_core(job.import_batch_id)
        counts.loaded = sum(v["inserted"] + v["updated"] for v in loaded.values())

        # refresh facts -----------------------------------------------------
        service = AnalyticsService()
        service.refresh_facts(db)

        # best-effort Metabase sync ----------------------------------------
        try:
            sync_schema()
        except Exception:
            pass

        job.status = IngestionJobStatus.success
        if batch is not None:
            batch.set_status(BatchStatus.success)
        db.commit()

        duration_ms = int((time.time() - start_time) * 1000)
        log_event(
            "ingest_completed",
            job_id=job.id,
            import_batch_id=job.import_batch_id,
            duration_ms=duration_ms,
            counts=counts.__dict__,
        )
        try:
            recompute_metrics.delay(org_id=str(job.org_id))
        except Exception:
            pass
        return {"status": "success", "duration_ms": duration_ms}
    except Exception as exc:  # pragma: no cover - exercised in tests
        db.rollback()
        error_json = {"error": str(exc), "sheet": None, "row": None}
        job.status = IngestionJobStatus.failed
        job.error_json = error_json
        if batch is not None:
            batch.set_status(BatchStatus.failed, error_json)
        db.commit()
        duration_ms = int((time.time() - start_time) * 1000)
        log_event(
            "ingest_failed",
            job_id=job.id,
            import_batch_id=job.import_batch_id,
            duration_ms=duration_ms,
            error=error_json,
        )
        raise
    finally:
        _close_db(db)
