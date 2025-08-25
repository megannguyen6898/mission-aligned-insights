import json
import hashlib
import uuid
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.data_upload import DataUpload, UploadStatus
from ..models.project import Project
from ..models.activity import Activity
from ..models.outcome import Outcome
from ..models.metric import Metric
from ..models.import_batches import ImportBatch, BatchStatus


class IngestionService:
    async def ingest_upload(self, upload_id: int, db: Session) -> None:
        """Read the stored upload file and persist project/activity/outcome/metric data."""

        upload = db.query(DataUpload).filter(DataUpload.id == upload_id).first()
        if not upload or not upload.file_path:
            return

        batch: ImportBatch | None = None
        try:
            upload.status = UploadStatus.processing
            db.commit()

            path = Path(upload.file_path)
            if not path.exists():
                raise FileNotFoundError(f"Upload file not found: {path}")

            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            batch = ImportBatch(
                id=str(uuid.uuid4()),
                source_system="excel",
                schema_version=1,
                triggered_by_user_id=str(upload.user_id),
            )
            db.add(batch)
            db.flush()

            row_count = 0
            for project_data in data:
                project = Project(
                    user_id=upload.user_id,
                    name=project_data.get("name", "Unnamed Project"),
                    row_hash=hashlib.sha256(
                        json.dumps(project_data, sort_keys=True).encode()
                    ).hexdigest(),
                    import_batch_id=batch.id,
                )
                db.add(project)
                db.flush()
                row_count += 1

                for activity_data in project_data.get("activities", []):
                    activity = Activity(
                        project_id=project.id,
                        name=activity_data.get("name", "Activity"),
                        row_hash=hashlib.sha256(
                            json.dumps(activity_data, sort_keys=True).encode()
                        ).hexdigest(),
                        import_batch_id=batch.id,
                    )
                    db.add(activity)
                    db.flush()

                    for outcome_data in activity_data.get("outcomes", []):
                        outcome = Outcome(
                            activity_id=activity.id,
                            name=outcome_data.get("name", "Outcome"),
                            row_hash=hashlib.sha256(
                                json.dumps(outcome_data, sort_keys=True).encode()
                            ).hexdigest(),
                            import_batch_id=batch.id,
                        )
                        db.add(outcome)
                        db.flush()

                        for metric_data in outcome_data.get("metrics", []):
                            metric = Metric(
                                outcome_id=outcome.id,
                                name=metric_data.get("name", "metric"),
                                value=metric_data.get("value"),
                            )
                            db.add(metric)
                            db.flush()

            batch.set_status(BatchStatus.success)
            upload.status = UploadStatus.completed
            upload.row_count = row_count
            db.commit()
        except Exception as exc:
            if batch is not None:
                batch.set_status(BatchStatus.failed, {"error": str(exc)})
            upload.status = UploadStatus.failed
            upload.error_message = str(exc)
            db.commit()
