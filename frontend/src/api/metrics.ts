import { api } from "@/lib/api";

export type MetricSuggestion = {
  column_name: string;
  existing_mapping?: number;
  summary: Record<string, unknown>;
  suggestions: Array<{
    metric_id: number;
    metric_name: string;
    metric_code?: string;
    unit?: string;
    category?: string;
    confidence: number;
    similarity: number;
  }>;
};

export type MetricSuggestResponse = {
  dataset_id: string;
  columns: MetricSuggestion[];
};

export type MetricConfirmPayload = {
  column_name: string;
  metric_id: number;
  confidence?: number;
  suggested_by_ai?: boolean;
};

export type MetricConfirmResponse = {
  dataset_id: string;
  confirmed: string[];
};

export type SDGIndicatorSuggestion = {
  indicator_id: number;
  indicator_code: string;
  indicator_title: string;
  metric_id: number;
  dataset_column: string;
  score: number;
};

export type SDGTargetSuggestion = {
  target_id: number;
  target_code: string;
  target_title: string;
  score: number;
  indicators: SDGIndicatorSuggestion[];
};

export type SDGGoalSuggestion = {
  goal_id: number;
  goal_number: number;
  goal_title: string;
  goal_color?: string;
  score: number;
  targets: SDGTargetSuggestion[];
};

export type SDGSuggestResponse = {
  dataset_id: string;
  goals: SDGGoalSuggestion[];
};

export type AnalysisRunResponse = {
  dataset_id: string;
  job_id?: string;
  status: string;
};

export type CorrelationResult = {
  correlation_id: string;
  metric_id: number;
  sdg_indicator_id?: number | null;
  independent_variable: string;
  r_value: number;
  p_value?: number | null;
  direction: string;
  confidence: number;
};

export type AnalysisResultsResponse = {
  dataset_id: string;
  results: CorrelationResult[];
};

export type BenchmarkMetric = {
  metric_id: number;
  metric_name: string;
  mean_value: number;
  std_dev?: number | null;
  sample_size?: number | null;
  source?: string | null;
};

export type BenchmarkResponse = {
  sector: string;
  metrics: BenchmarkMetric[];
};

export async function fetchMetricSuggestions(datasetId: string, topN = 3) {
  const { data } = await api.post<MetricSuggestResponse>(
    `/datasets/${datasetId}/metrics/suggest`,
    { top_n: topN },
  );
  return data;
}

export async function confirmMetricMappings(datasetId: string, mappings: MetricConfirmPayload[]) {
  const { data } = await api.post<MetricConfirmResponse>(
    `/datasets/${datasetId}/metrics/confirm`,
    { mappings },
  );
  return data;
}

export async function fetchSDGSuggestions(datasetId: string) {
  const { data } = await api.get<SDGSuggestResponse>(`/datasets/${datasetId}/sdg/suggest`);
  return data;
}

export async function runImpactAnalysis(datasetId: string, independentVariables: string[]) {
  const { data } = await api.post<AnalysisRunResponse>(`/datasets/${datasetId}/analysis/run`, {
    independent_variables: independentVariables,
  });
  return data;
}

export async function fetchAnalysisResults(datasetId: string) {
  const { data } = await api.get<AnalysisResultsResponse>(`/datasets/${datasetId}/analysis/results`);
  return data;
}

export async function fetchBenchmarks(sector: string) {
  const { data } = await api.get<BenchmarkResponse>(`/benchmarks/${sector}`);
  return data;
}
