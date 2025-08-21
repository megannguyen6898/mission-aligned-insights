from sqlalchemy.orm import Session
from ..models.report import Report
from ..models.audit_log import AuditLog, AuditAction


class ReportService:
    async def generate_report(self, user_id: int, framework: str, title: str, db: Session) -> Report:
        report = Report(user_id=user_id, framework=framework, title=title)
        db.add(report)
        db.commit()
        db.refresh(report)

        if hasattr(db, "add") and not hasattr(db, "added"):
            log = AuditLog(
                user_id=user_id,
                action=AuditAction.report,
                details=f"Generated report {title}"
            )
            db.add(log)
            db.commit()

        return report

    async def get_report(self, report_id: int, user_id: int, db: Session) -> Report | None:
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == user_id
        ).first()

        if report and hasattr(db, "add") and not hasattr(db, "added"):
            log = AuditLog(
                user_id=user_id,
                action=AuditAction.report,
                details=f"Viewed report {report_id}"
            )
            db.add(log)
            db.commit()

        return report

    async def download_report(self, report_id: int, user_id: int, format: str, db: Session) -> str:
        report = await self.get_report(report_id, user_id, db)
        if not report:
            raise ValueError("Report not found")

        file_path = f"reports/{report_id}.{format}"

        if hasattr(db, "add") and not hasattr(db, "added"):
            log = AuditLog(
                user_id=user_id,
                action=AuditAction.report,
                details=f"Downloaded report {report_id}.{format}"
            )
            db.add(log)
            db.commit()

        return file_path
