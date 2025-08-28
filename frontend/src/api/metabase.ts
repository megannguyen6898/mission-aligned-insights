import { api } from "@/lib/api";

export function listDashboards() {
  return api.get("/dashboards");
}

export function getSignedDashboard(id: number, params?: Record<string, any>) {
  return api.post("/metabase/signed", { resource: "dashboard", id, params });
}
