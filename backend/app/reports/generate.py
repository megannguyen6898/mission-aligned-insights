import os
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from ..models.project import Project
from ..services.analytics_service import AnalyticsService

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


def render_space_report(
    db: Session,
    space_id: str,
    template_key: str,
    inputs: Dict[str, Any] | None = None,
) -> bytes:
    analytics = AnalyticsService()
    kpi_payload = analytics.get_kpis(db, space_id)
    kpis = kpi_payload.get("kpis", [])
    series_payload = analytics.get_series(
        db,
        space_id,
        ["beneficiaries", "completions"],
        group_by="year",
        time_range=None,
    )

    template_name = _resolve_space_template(template_key)
    template = env.get_template(template_name)

    context = {
        "space_id": space_id,
        "generated_at": datetime.utcnow(),
        "kpis": kpis,
        "series": series_payload.get("series", []),
        "series_meta": series_payload.get("meta", {}),
        "inputs": inputs or {},
        "narrative": _build_narrative(kpis),
    }
    html = template.render(**context)

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_path = Path(tmp_pdf.name)
    try:
        _html_to_pdf(html, tmp_path)
        return tmp_path.read_bytes()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def _resolve_space_template(template_key: str) -> str:
    candidate = f"{template_key}_space_report.html.j2"
    available = set(env.list_templates())
    if candidate in available:
        return candidate
    return "space_report.html.j2"


def _build_narrative(kpis: Sequence[Dict[str, Any]]) -> str:
    if not kpis:
        return "No KPI data available yet. Upload data to generate insights."
    top = max(kpis, key=lambda item: item.get("value", 0))
    change = top.get("delta", 0)
    trend = "increased" if change > 0 else "decreased" if change < 0 else "held steady"
    change_pct = f"{abs(change) * 100:.1f}%" if change else ""
    unit = top.get("unit", "")
    unit_suffix = f" {unit}" if unit and not unit.startswith("ratio") else ""
    magnitude = f"{top.get('value', 0):,.0f}" if isinstance(top.get("value"), (int, float)) else top.get("value")
    change_clause = f" ({change_pct})" if change_pct else ""
    return (
        f"{top.get('label')} reached {magnitude}{unit_suffix}{change_clause} over the latest period, "
        f"and overall performance {trend}."
    )
