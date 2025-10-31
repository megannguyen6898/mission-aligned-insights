import { api } from "@/lib/api";

export type UploadPresignPayload = {
  workspaceId: number;
  filename: string;
  mimeType: string;
  sizeBytes: number;
};

export type UploadPresignResponse = {
  upload_id: number;
  storage_key: string;
  url: string;
  headers: Record<string, string>;
  max_mb: number;
};

export type WorkflowStepState = {
  step: string;
  state: string;
  error?: string;
  id?: string;
  dataset_id?: string | null;
};

export type WorkflowSummary = {
  upload: WorkflowStepState;
  validate: WorkflowStepState;
  ingest: WorkflowStepState;
};

export type WorkflowStatus = {
  id: string;
  step: string;
  state: string;
  progress?: number | null;
  error?: string | null;
};

export type DatasetResponse = {
  schema: Array<Record<string, unknown>>;
  preview: Array<Record<string, unknown>>;
  row_count: number | null;
  table_name: string | null;
};

export type DashboardChart = {
  id: string;
  title: string;
  spec: Record<string, unknown>;
};

export type DashboardGenerateResponse = {
  charts: DashboardChart[];
  layout: Record<string, unknown>;
};

export type AIAskResponse = {
  answer: string;
  usage_ms: number;
};

export type ReportGenerateResponse = {
  report_id: string;
  download_url: string;
};

export async function presignUpload(payload: UploadPresignPayload) {
  const body = {
    workspace_id: payload.workspaceId,
    filename: payload.filename,
    mime_type: payload.mimeType,
    size_bytes: payload.sizeBytes,
  };
  const { data } = await api.post<UploadPresignResponse>("/uploads/presign", body);
  return data;
}

export async function uploadToPresignedUrl(url: string, file: File, headers: Record<string, string>) {
  const response = await fetch(url, {
    method: "PUT",
    headers,
    body: file,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Upload failed: ${response.status} ${text}`);
  }
}

export async function completeUpload(uploadId: number) {
  const { data } = await api.post<WorkflowSummary>(`/uploads/${uploadId}/complete`);
  return data;
}

export async function getUploadWorkflow(uploadId: number) {
  const { data } = await api.get<WorkflowSummary>(`/uploads/${uploadId}/workflow`);
  return data;
}

export async function getWorkflowStatus(workflowId: string) {
  const { data } = await api.get<WorkflowStatus>(`/workflows/${workflowId}/status`);
  return data;
}

export async function triggerIngest(datasetId: string) {
  const { data } = await api.post<WorkflowStatus>(`/workflows/${datasetId}/ingest`);
  return data;
}

export async function getDataset(datasetId: string) {
  const { data } = await api.get<DatasetResponse>(`/datasets/${datasetId}`);
  return data;
}

export async function generateDashboards(datasetId: string) {
  const { data } = await api.post<DashboardGenerateResponse>("/dashboards/generate", {
    dataset_id: datasetId,
  });
  return data;
}

export async function askAI(workspaceId: number, datasetId: string, question: string) {
  const { data } = await api.post<AIAskResponse>("/ai/ask", {
    workspace_id: workspaceId,
    dataset_id: datasetId,
    question,
  });
  return data;
}

export async function generateReport(payload: {
  datasetId: string;
  selectedChartIds: string[];
  narrativeBlocks: { heading?: string; body?: string }[];
  branding?: { logo_url?: string; primary_color?: string };
}) {
  const { data } = await api.post<ReportGenerateResponse>("/reports/generate", {
    dataset_id: payload.datasetId,
    selected_chart_ids: payload.selectedChartIds,
    narrative_blocks: payload.narrativeBlocks,
    branding: payload.branding,
  });
  return data;
}
