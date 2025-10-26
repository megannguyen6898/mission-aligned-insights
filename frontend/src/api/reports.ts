import { api } from "@/lib/api";

export function listReportTemplates() {
  return api.get("/report-templates");
}
