from __future__ import annotations

import logging
from typing import List, Optional
from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError  # pragma: no cover - imported for API completeness
from rq.job import Job
from rq.retry import Retry

from .config import settings
from .database import SessionLocal
from .models import Dataset, Upload, UploadStatus, Workflow, WorkflowState
from .storage.s3_client import get_s3_client
from .services.ingest import write_dataframe
from .services.validation import ValidationResult, analyse_workbook
from .services.analytics import ImpactAnalyticsService

logger = logging.getLogger(__name__)

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue("default", connection=redis_conn)
analytics_service = ImpactAnalyticsService()


def enqueue_validation(upload_id: int, workflow_id: str) -> Job:
    return queue.enqueue(
        "app.jobs.validate_upload",
        upload_id,
        workflow_id,
        retry=Retry(max=2, interval=[5, 15]),
        job_timeout=600,
    )


def enqueue_ingest(dataset_id: str, workflow_id: str) -> Job:
    return queue.enqueue(
        "app.jobs.ingest_dataset",
        dataset_id,
        workflow_id,
        retry=Retry(max=2, interval=[5, 15]),
        job_timeout=900,
    )


def enqueue_analysis_job(dataset_id: str, independent_variables: List[str]) -> Optional[Job]:
    try:
        return queue.enqueue(
            "app.jobs.run_dataset_analysis",
            dataset_id,
            independent_variables,
            retry=Retry(max=1, interval=[15]),
            job_timeout=900,
        )
    except Exception:  # pragma: no cover - fallback in tests without Redis
        logger.exception("Failed to enqueue analysis job, running inline")
        return None


def _load_upload_bytes(upload: Upload) -> bytes:
    bucket = settings.storage_bucket
    if not bucket:
        raise RuntimeError("STORAGE_BUCKET not configured")

    client = get_s3_client()
    obj = client.get_object(Bucket=bucket, Key=upload.object_key)
    return obj["Body"].read()


def _get_or_create_dataset(session, upload: Upload) -> Dataset:
    dataset = upload.dataset
    if dataset:
        return dataset
    dataset = Dataset(
        workspace_id=upload.workspace_id,
        upload_id=upload.id,
    )
    session.add(dataset)
    session.flush()
    return dataset


def validate_upload(upload_id: int, workflow_id: str) -> None:
    session = SessionLocal()
    try:
        workflow: Optional[Workflow] = session.get(Workflow, workflow_id)
        upload: Optional[Upload] = session.get(Upload, upload_id)
        if not upload:
            raise ValueError(f"Upload {upload_id} not found")

        if workflow:
            workflow.state = WorkflowState.running
            workflow.progress = 10
            session.commit()

        if upload.status in {UploadStatus.validated, UploadStatus.ingested}:
            logger.info("Upload %s already validated, skipping", upload_id)
            if workflow:
                workflow.state = WorkflowState.succeeded
                workflow.progress = 100
                session.commit()
            return

        raw = _load_upload_bytes(upload)
        result: ValidationResult = analyse_workbook(raw)
        dataset = _get_or_create_dataset(session, upload)
        dataset.schema = result.schema
        dataset.preview = result.preview
        dataset.row_count = result.row_count
        session.commit()

        if workflow and not workflow.dataset_id:
            workflow.dataset_id = dataset.id
            session.commit()

        upload.status = UploadStatus.validated
        upload.errors_json = None
        upload.error_message = None
        session.commit()

        if workflow:
            workflow.state = WorkflowState.succeeded
            workflow.progress = 100
            workflow.error = None
            workflow.meta = {"row_count": dataset.row_count}
            session.commit()
    except Exception as exc:  # pragma: no cover - error path
        session.rollback()
        logger.exception("Validation failed for upload %s", upload_id)
        upload = session.get(Upload, upload_id)
        if upload:
            upload.status = UploadStatus.failed
            upload.error_message = str(exc)
            upload.errors_json = {"message": str(exc)}
            session.commit()
        if workflow:
            workflow.state = WorkflowState.failed
            workflow.error = str(exc)
            workflow.progress = 100
            session.commit()
        raise
    finally:
        session.close()


def ingest_dataset(dataset_id: str, workflow_id: str) -> None:
    session = SessionLocal()
    try:
        workflow: Optional[Workflow] = session.get(Workflow, workflow_id)
        dataset: Optional[Dataset] = session.get(Dataset, dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        upload = dataset.upload
        if not upload:
            raise ValueError("Dataset missing source upload")

        if workflow:
            workflow.state = WorkflowState.running
            workflow.progress = 10
            session.commit()

        raw = _load_upload_bytes(upload)
        result: ValidationResult = analyse_workbook(raw)
        df = result.dataframe
        table_name = dataset.table_name or f"dataset_{dataset.id.hex}"
        write_dataframe(df, table_name, if_exists="replace")

        dataset.table_name = table_name
        dataset.row_count = int(df.shape[0])
        session.commit()

        if workflow and not workflow.dataset_id:
            workflow.dataset_id = dataset.id
            session.commit()

        upload.status = UploadStatus.ingested
        session.commit()

        if workflow:
            workflow.state = WorkflowState.succeeded
            workflow.progress = 100
            workflow.error = None
            workflow.meta = {"table_name": table_name, "row_count": dataset.row_count}
            session.commit()
    except Exception as exc:  # pragma: no cover - error path
        session.rollback()
        logger.exception("Ingest failed for dataset %s", dataset_id)
        dataset = session.get(Dataset, dataset_id)
        if dataset:
            dataset.table_name = dataset.table_name or f"dataset_{dataset_id}"
            session.commit()
        workflow = session.get(Workflow, workflow_id)
        if workflow:
            workflow.state = WorkflowState.failed
            workflow.error = str(exc)
            workflow.progress = 100
            session.commit()
        raise
    finally:
        session.close()


def run_dataset_analysis(dataset_id: str, independent_variables: List[str]) -> None:
    session = SessionLocal()
    try:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        analytics_service.run_correlations(session, dataset, independent_variables or [])
    finally:
        session.close()
