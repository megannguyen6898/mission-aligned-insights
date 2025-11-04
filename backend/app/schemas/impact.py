from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetricSuggestRequest(BaseModel):
    top_n: int = Field(default=3, ge=1, le=10)


class MetricSuggestion(BaseModel):
    metric_id: int
    metric_name: str
    metric_code: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    confidence: float
    similarity: float


class ColumnSuggestion(BaseModel):
    column_name: str
    existing_mapping: Optional[int] = None
    summary: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[MetricSuggestion]


class MetricSuggestResponse(BaseModel):
    dataset_id: str
    columns: List[ColumnSuggestion]


class MetricConfirmItem(BaseModel):
    column_name: str
    metric_id: int
    confidence: Optional[float] = None
    suggested_by_ai: bool = True


class MetricConfirmRequest(BaseModel):
    mappings: List[MetricConfirmItem]


class MetricConfirmResponse(BaseModel):
    dataset_id: str
    confirmed: List[str]


class SDGIndicatorSuggestion(BaseModel):
    indicator_id: int
    indicator_code: str
    indicator_title: str
    metric_id: int
    dataset_column: str
    score: float


class SDGTargetSuggestion(BaseModel):
    target_id: int
    target_code: str
    target_title: str
    score: float
    indicators: List[SDGIndicatorSuggestion]


class SDGGoalSuggestion(BaseModel):
    goal_id: int
    goal_number: int
    goal_title: str
    goal_color: Optional[str] = None
    score: float
    targets: List[SDGTargetSuggestion]


class SDGSuggestResponse(BaseModel):
    dataset_id: str
    goals: List[SDGGoalSuggestion]


class AnalysisRunRequest(BaseModel):
    independent_variables: List[str] = Field(default_factory=list)


class AnalysisRunResponse(BaseModel):
    dataset_id: str
    job_id: Optional[str] = None
    status: str


class CorrelationResultItem(BaseModel):
    correlation_id: str
    metric_id: int
    sdg_indicator_id: Optional[int] = None
    independent_variable: str
    r_value: float
    p_value: Optional[float] = None
    direction: str
    confidence: float


class AnalysisResultsResponse(BaseModel):
    dataset_id: str
    results: List[CorrelationResultItem]


class BenchmarkMetric(BaseModel):
    metric_id: int
    metric_name: str
    mean_value: float
    std_dev: Optional[float] = None
    sample_size: Optional[int] = None
    source: Optional[str] = None


class BenchmarkResponse(BaseModel):
    sector: str
    metrics: List[BenchmarkMetric]
