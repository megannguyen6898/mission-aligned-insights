from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from .dashboard_service import DashboardService
from ..models.report import Report


class ReportService:
    def __init__(self) -> None:
        self.dashboard_service = DashboardService()

    async def generate_report(
        self, user_id: int, framework: str, title: str, db: Session
    ) -> Report:
        """Create a basic report record."""

        report = Report(
            user_id=user_id,
            title=title,
            framework=framework,
            metrics={},
            visualizations={},
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    async def get_report(
        self, report_id: int, user_id: int, db: Session
    ) -> Optional[Report]:
        """Retrieve a report for a specific user."""

        return (
            db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user_id)
            .first()
        )

    async def generate_pdf(
        self, report_id: int, user_id: int, db: Session
    ) -> str:
        """Generate a PDF report including metrics and charts."""

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics import renderPDF

        report = await self.get_report(report_id, user_id, db)
        if not report:
            raise ValueError("Report not found")

        metrics: Dict[str, Any] = report.metrics or {}
        charts: Dict[str, Any] = report.visualizations or {}

        dashboards = await self.dashboard_service.get_user_dashboards(user_id, db)
        if dashboards:
            charts.update(dashboards[0].chart_data or {})

        pdf_file = NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(pdf_file.name, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, report.title)
        y -= 30

        c.setFont("Helvetica", 12)
        if metrics:
            c.drawString(40, y, "Metrics")
            y -= 20
            for name, value in metrics.items():
                c.drawString(60, y, f"{name}: {value}")
                y -= 15
            y -= 10

        impact_data = charts.get("impact")
        if impact_data:
            c.drawString(40, y, "Impact Chart")
            y -= 170
            drawing = Drawing(400, 150)
            data = [item.get("value", 0) for item in impact_data]
            names = [item.get("name", "") for item in impact_data]
            chart = VerticalBarChart()
            chart.x = 0
            chart.y = 0
            chart.height = 150
            chart.width = 400
            chart.data = [data]
            chart.categoryAxis.categoryNames = names
            drawing.add(chart)
            renderPDF.draw(drawing, c, 40, y)
            y -= 10

        c.showPage()
        c.save()
        pdf_file.close()

        report.report_url = pdf_file.name
        db.commit()

        return pdf_file.name
