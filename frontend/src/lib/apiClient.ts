import { api } from "@/lib/api";

export type Kpi = {
  label: string;
  value: number;
  delta: number;
  unit: string;
};

export type KpiResponse = {
  kpis: Kpi[];
};

export type SeriesPoint = {
  x: number | string;
  y: number;
};

export type Series = {
  label: string;
  points: SeriesPoint[];
};

export type SeriesResponse = {
  series: Series[];
  meta?: {
    unit?: string;
    note?: string;
  };
};

export async function getKpis(spaceId: string): Promise<KpiResponse> {
  const { data } = await api.get<KpiResponse>("/analytics/kpis", {
    params: { space_id: spaceId },
  });
  return data;
}

export async function getSeries(
  spaceId: string,
  metric: string,
  params: { group_by?: "year" | "region" | "program"; time_range?: string } = {}
): Promise<SeriesResponse> {
  const query = {
    space_id: spaceId,
    metric,
    ...params,
  };
  const { data } = await api.get<SeriesResponse>("/analytics/series", {
    params: query,
  });
  return data;
}

export async function renderReport(
  spaceId: string,
  template: "sdg" | "ops" | "sroi",
  inputs?: Record<string, unknown>
): Promise<Blob> {
  const response = await api.post("/report/render", {
    space_id: spaceId,
    template,
    inputs,
  }, {
    responseType: "blob",
  });
  return response.data as Blob;
}
