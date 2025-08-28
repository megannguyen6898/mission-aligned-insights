import { api } from "@/lib/api";

export function listReportTemplates() {
  return api.get("/report-templates");
}

export function createReport(templateId: number, params?: Record<string, any>) {
  return api.post("/reports", { template_id: templateId, params });
}

export function getReportStatus(id: number) {
  return api.get(`/reports/${id}`);
}

export function downloadReport(id: number) {
  return api.get(`/reports/${id}/download`, { responseType: "blob" });
}
