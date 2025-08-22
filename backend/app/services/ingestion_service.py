import json
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.data_upload import DataUpload, UploadStatus
from ..models.project import Project
from ..models.activity import Activity
from ..models.outcome import Outcome
from ..models.metric import Metric


class IngestionService:
    async def ingest_upload(self, upload_id: int, db: Session) -> None:
        """Read the stored upload file and persist project/activity/outcome/metric data."""

        upload = db.query(DataUpload).filter(DataUpload.id == upload_id).first()
        if not upload or not upload.file_path:
            return

        try:
            upload.status = UploadStatus.processing
            db.commit()

            path = Path(upload.file_path)
            if not path.exists():
                raise FileNotFoundError(f"Upload file not found: {path}")

            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            row_count = 0
            for project_data in data:
                project = Project(user_id=upload.user_id, name=project_data.get("name", "Unnamed Project"))
                db.add(project)
                db.flush()
                row_count += 1

                for activity_data in project_data.get("activities", []):
                    activity = Activity(project_id=project.id, name=activity_data.get("name", "Activity"))
                    db.add(activity)
                    db.flush()

                    for outcome_data in activity_data.get("outcomes", []):
                        outcome = Outcome(activity_id=activity.id, name=outcome_data.get("name", "Outcome"))
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

            upload.status = UploadStatus.completed
            upload.row_count = row_count
            db.commit()
        except Exception as exc:
            upload.status = UploadStatus.failed
            upload.error_message = str(exc)
            db.commit()
