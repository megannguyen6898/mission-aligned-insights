from sqlalchemy.orm import Session
from ..models.report import Report
from ..models.audit_log import AuditLog

class ReportService:
    async def generate_report(self, user_id: int, framework: str, title: str, db: Session) -> Report:
        report = Report(user_id=user_id, framework=framework, title=title)
        db.add(report)
        db.commit()
        db.refresh(report)

        log = AuditLog(
            user_id=user_id,
            action="report_generated",
            resource_type="report",
            resource_id=report.id,
        )
        db.add(log)
        db.commit()
        return report

    async def get_report(self, report_id: int, user_id: int, db: Session) -> Report:
        return db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == user_id,
        ).first()

    async def download_report(self, report_id: int, user_id: int, format: str, db: Session) -> str:
        report = await self.get_report(report_id, user_id, db)
        if not report:
            raise ValueError("Report not found")
        # In a real implementation this would generate a file
        return f"/tmp/report_{report_id}.{format}"
