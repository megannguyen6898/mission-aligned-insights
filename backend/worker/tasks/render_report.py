import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Dict

from celery import shared_task
from jinja2 import Template, StrictUndefined


@shared_task(name="render_report")
def render_report_job(job_id: int) -> Dict[str, str]:
    """Render a report job defined in the database."""
    from backend.app.database import SessionLocal
    from backend.app.models.report import ReportJob, ReportTemplate, ReportJobStatus
    from backend.app.storage.s3_client import get_s3_client

    db = SessionLocal()
    job = db.query(ReportJob).filter(ReportJob.id == job_id).first()
    if job is None:
        db.close()
        return {"status": "missing"}

    template = db.query(ReportTemplate).filter(ReportTemplate.id == job.template_id).first()
    bucket = os.environ.get("S3_BUCKET")
    s3 = get_s3_client()

    try:
        job.status = ReportJobStatus.running
        db.commit()

        with NamedTemporaryFile(delete=False) as tmp:
            if bucket:
                s3.download_file(bucket, template.object_key, tmp.name)
            else:
                s3.download_file(None, template.object_key, tmp.name)  # type: ignore[arg-type]
            template_path = tmp.name

        if template.engine.value == "html":
            with open(template_path, "r", encoding="utf-8") as f:
                tpl = Template(f.read(), undefined=StrictUndefined)
            html = tpl.render(job.params_json or {})
            with NamedTemporaryFile(delete=False, suffix=".pdf") as out:
                try:
                    from weasyprint import HTML  # type: ignore

                    HTML(string=html).write_pdf(out.name)
                except Exception:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter

                    c = canvas.Canvas(out.name, pagesize=letter)
                    c.drawString(40, 750, html[:1000])
                    c.save()
                output_path = out.name
            key = f"reports/{job.id}.pdf"
            with open(output_path, "rb") as data:
                s3.put_object(Bucket=bucket, Key=key, Body=data.read(), ContentType="application/pdf")
        else:
            from docxtpl import DocxTemplate  # type: ignore

            doc = DocxTemplate(template_path)
            doc.render(job.params_json or {})
            with NamedTemporaryFile(delete=False, suffix=".docx") as out:
                doc.save(out.name)
                output_path = out.name
            key = f"reports/{job.id}.docx"
            with open(output_path, "rb") as data:
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data.read(),
                    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

        job.status = ReportJobStatus.success
        job.output_object_key = key
        job.completed_at = datetime.utcnow()
        db.commit()
        return {"status": "success", "key": key}
    except Exception as exc:  # pragma: no cover
        db.rollback()
        job.status = ReportJobStatus.failed
        job.error_json = {"error": str(exc)}
        job.completed_at = datetime.utcnow()
        db.commit()
        raise
    finally:
        db.close()
