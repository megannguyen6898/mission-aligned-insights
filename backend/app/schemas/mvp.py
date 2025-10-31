from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, conint, constr


class UploadPresignRequest(BaseModel):
    workspace_id: conint(ge=1)
    filename: constr(min_length=1)
    mime_type: constr(min_length=1)
    size_bytes: conint(gt=0)


class UploadPresignResponse(BaseModel):
    upload_id: int
    storage_key: str
    url: str
    headers: Dict[str, str]
    max_mb: int


class UploadCompleteResponse(BaseModel):
    upload: Dict[str, Optional[str]]
    validate: Dict[str, Optional[str]]
    ingest: Dict[str, Optional[str]]


class WorkflowStatusResponse(BaseModel):
    workflow_id: str = Field(alias="id")
    step: str
    state: str
    progress: Optional[int] = None
    error: Optional[str] = None


class WorkflowTriggerRequest(BaseModel):
    dataset_id: str


class DatasetResponse(BaseModel):
    schema: List[Dict[str, str]]
    preview: List[Dict[str, str]]
    row_count: Optional[int]
    table_name: Optional[str]


class DashboardGenerateRequest(BaseModel):
    dataset_id: str


class ChartSpec(BaseModel):
    id: str
    title: str
    spec: Dict[str, object]


class DashboardGenerateResponse(BaseModel):
    charts: List[ChartSpec]
    layout: Dict[str, object]


class AIAskRequest(BaseModel):
    workspace_id: int
    dataset_id: str
    question: constr(min_length=2)


class AIAskResponse(BaseModel):
    answer: str
    usage_ms: int


class NarrativeBlock(BaseModel):
    heading: Optional[str] = None
    body: Optional[str] = None


class Branding(BaseModel):
    logo_url: Optional[HttpUrl] = None
    primary_color: Optional[str] = None


class ReportGenerateRequest(BaseModel):
    dataset_id: str
    selected_chart_ids: List[str] = Field(default_factory=list)
    narrative_blocks: List[NarrativeBlock] = Field(default_factory=list)
    branding: Optional[Branding] = None


class ReportGenerateResponse(BaseModel):
    report_id: str
    download_url: str
