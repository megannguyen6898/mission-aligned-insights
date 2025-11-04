from __future__ import annotations

import base64
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import plotly.io as pio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from ..config import settings
from ..models import Dataset
from ..storage.presign import create_presigned_get
from ..storage.s3_client import get_s3_client
from .dashboards import load_dataset_frame

templates_dir = Path(__file__).resolve().parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"]),
)


def _figure_to_base64_image(spec: Dict[str, object]) -> str:
    fig = pio.from_json(spec)
    png_bytes = pio.to_image(fig, format="png", width=960, height=540)
    return base64.b64encode(png_bytes).decode("ascii")


def _ensure_bucket() -> str:
    bucket = settings.storage_bucket
    if not bucket:
        raise RuntimeError("STORAGE_BUCKET not configured")
    return bucket


def build_report_html(
    dataset: Dataset,
    charts: List[Dict[str, object]],
    narratives: List[Dict[str, Optional[str]]],
    branding: Optional[Dict[str, str]],
    sdg_summary: Optional[Dict[str, object]] = None,
    correlations: Optional[List[Dict[str, object]]] = None,
) -> str:
    template = env.get_template("report.html")
    data_frame = load_dataset_frame(dataset, limit=1000)
    kpi_rows = []
    for column in data_frame.select_dtypes(include=["number"]).columns[:4]:
        series = data_frame[column]
        kpi_rows.append(
            {
                "label": column,
                "total": f"{series.sum():,.2f}",
                "average": f"{series.mean():,.2f}",
            }
        )

    chart_blocks = []
    for chart in charts:
        try:
            chart_blocks.append(
                {
                    "title": chart.get("title", "Chart"),
                    "image": _figure_to_base64_image(chart["spec"]),
                }
            )
        except Exception:  # pragma: no cover - fallback if chart conversion fails
            continue

    return template.render(
        dataset=dataset,
        kpi_rows=kpi_rows,
        chart_blocks=chart_blocks,
        narratives=narratives,
        branding=branding or {},
        sdg_summary=sdg_summary or {},
        correlations=correlations or [],
    )


def generate_report(
    dataset: Dataset,
    charts: List[Dict[str, object]],
    narratives: List[Dict[str, Optional[str]]],
    branding: Optional[Dict[str, str]] = None,
    sdg_summary: Optional[Dict[str, object]] = None,
    correlations: Optional[List[Dict[str, object]]] = None,
) -> Dict[str, str]:
    html_content = build_report_html(
        dataset,
        charts,
        narratives,
        branding,
        sdg_summary=sdg_summary,
        correlations=correlations,
    )
    pdf_bytes = HTML(string=html_content).write_pdf()

    report_id = str(uuid.uuid4())
    workspace_segment = dataset.workspace_id or "shared"
    storage_key = f"reports/{workspace_segment}/{report_id}.pdf"

    client = get_s3_client()
    client.put_object(
        Bucket=_ensure_bucket(),
        Key=storage_key,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )

    download_url = create_presigned_get(storage_key, expires_in=3600)
    return {"report_id": report_id, "download_url": download_url, "storage_key": storage_key}
