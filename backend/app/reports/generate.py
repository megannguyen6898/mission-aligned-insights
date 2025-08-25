import os
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from ..models.project import Project

TEMPLATES_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "j2"]),
)

def _get_logo_path(org_id: str) -> str | None:
    candidate = Path("backend/app/assets") / f"{org_id}_logo.png"
    if candidate.exists():
        return candidate.as_posix()
    return None

def _html_to_pdf(html: str, output: Path) -> None:
    try:
        from weasyprint import HTML  # type: ignore

        HTML(string=html).write_pdf(str(output))
        return
    except Exception:
        pass

    with NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        tmp.write(html.encode("utf-8"))
        tmp.flush()
        try:
            cmd = ["wkhtmltopdf", tmp.name, str(output)]
            os.system(" ".join(cmd))
        finally:
            os.unlink(tmp.name)

def generate_pdf(project_id: str, org_id: str, sections: List[str], db: Session) -> Path:
    project: Project | None = (
        db.query(Project).filter_by(id=project_id, owner_org_id=org_id).first()
    )
    if project is None:
        raise ValueError("Project not found")

    logo = _get_logo_path(project.owner_org_id)
    template = env.get_template("impact_report.html.j2")
    html = template.render(project=project, sections=sections, logo_path=logo)

    outdir = Path("reports") / project.owner_org_id / project.project_id
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    pdf_path = outdir / f"{ts}.pdf"
    _html_to_pdf(html, pdf_path)
    return pdf_path
