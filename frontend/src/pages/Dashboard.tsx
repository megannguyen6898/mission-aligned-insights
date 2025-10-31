import React, { useMemo, useState } from "react";
import createPlotlyComponent from "react-plotly.js/factory";
import * as Plotly from "plotly.js-dist-min";
import { useQuery } from "@tanstack/react-query";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/layout/PageHeader";
import { KpiCard } from "@/components/common/KpiCard";
import { AINarrativeCard } from "@/components/dashboard/AINarrativeCard";
import { ChartBlock } from "@/components/charts/ChartBlock";
import { getKpis, getSeries, Kpi, Series } from "@/lib/apiClient";
import { useAuth } from "@/contexts/AuthContext";
import { Download, FileBarChart, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  askAI,
  generateDashboards,
  generateReport,
  type DashboardChart,
} from "@/api/mvp";

const Plot = createPlotlyComponent(Plotly as any);

const palette = ["#06B6D4", "#FBBF24", "#0EA5E9", "#22D3EE", "#64748B", "#34D399"];

type TrendDirection = "up" | "down" | "neutral";

const keyForLabel = (label: string) => label.toLowerCase().replace(/[^a-z0-9]+/g, "_");

const formatKpiValue = (kpi: Kpi) => {
  if (kpi.unit === "ratio") {
    return `${(kpi.value * 100).toFixed(1)}%`;
  }
  if (kpi.unit === "score") {
    return kpi.value.toFixed(1);
  }
  const formatter = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  return formatter.format(kpi.value);
};

const trendForDelta = (delta: number): { direction: TrendDirection; label: string } => {
  if (delta > 0.005) {
    return { direction: "up", label: `+${(delta * 100).toFixed(1)}% vs prior period` };
  }
  if (delta < -0.005) {
    return { direction: "down", label: `${(delta * 100).toFixed(1)}% vs prior period` };
  }
  return { direction: "neutral", label: "No material change" };
};

const buildNarrative = (kpis: Kpi[]): string => {
  if (!kpis.length) {
    return "Upload data to unlock KPI narratives and chart-based insights.";
  }
  const ordered = [...kpis].sort((a, b) => (b.value || 0) - (a.value || 0));
  const focus = ordered[0];
  const trend = trendForDelta(focus.delta);
  const change = trend.direction === "neutral" ? "held steady" : trend.direction === "up" ? "increased" : "decreased";
  const changePct = trend.direction === "neutral" ? "" : ` (${(Math.abs(focus.delta) * 100).toFixed(1)}%)`;
  return `${focus.label} reached ${formatKpiValue(focus)} ${focus.unit !== "ratio" ? focus.unit : ""}${changePct} and overall performance ${change}.`;
};

const transformSeries = (series?: Series[]) => {
  if (!series || !series.length) {
    return { data: [], keys: [] as { key: string; label: string; color: string }[] };
  }
  const rows = new Map<string, Record<string, number | string>>();
  const keys: { key: string; label: string; color: string }[] = [];

  series.forEach((serie, index) => {
    const key = keyForLabel(serie.label) || `series_${index}`;
    keys.push({ key, label: serie.label, color: palette[index % palette.length] });
    serie.points.forEach((point) => {
      const bucket = String(point.x);
      const existing = rows.get(bucket) ?? { x: bucket };
      existing[key] = point.y;
      rows.set(bucket, existing);
    });
  });

  const sorted = Array.from(rows.values()).sort((a, b) => {
    const ax = a.x as string;
    const bx = b.x as string;
    const axNum = Number(ax);
    const bxNum = Number(bx);
    if (!Number.isNaN(axNum) && !Number.isNaN(bxNum)) {
      return axNum - bxNum;
    }
    return ax.localeCompare(bx);
  });

  return { data: sorted, keys };
};

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const spaceId = user?.organization_name || "org1";
  const workspaceId = user?.id ?? 1;
  const [datasetId, setDatasetId] = useState<string | null>(() => sessionStorage.getItem("latest_dataset_id"));
  const [charts, setCharts] = useState<DashboardChart[]>([]);
  const [isGeneratingCharts, setIsGeneratingCharts] = useState(false);
  const [aiQuestion, setAiQuestion] = useState("Which regions are most efficient?");
  const [aiNarrative, setAiNarrative] = useState("Upload data to unlock AI guidance.");
  const [aiBullets, setAiBullets] = useState<string[]>([]);
  const [isAskingAI, setIsAskingAI] = useState(false);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const { data: kpiData } = useQuery({
    queryKey: ["analytics", "kpis", spaceId],
    queryFn: () => getKpis(spaceId),
    enabled: Boolean(spaceId),
  });

  const { data: timeSeriesData } = useQuery({
    queryKey: ["analytics", "series", spaceId, "year"],
    queryFn: () => getSeries(spaceId, "beneficiaries,completions", { group_by: "year" }),
    enabled: Boolean(spaceId),
  });

  const { data: regionSeriesData } = useQuery({
    queryKey: ["analytics", "series", spaceId, "region"],
    queryFn: () => getSeries(spaceId, "beneficiaries", { group_by: "region" }),
    enabled: Boolean(spaceId),
  });

  const kpis = useMemo(() => kpiData?.kpis ?? [], [kpiData]);
  const narrative = useMemo(() => buildNarrative(kpis), [kpis]);
  const { data: lineData, keys: lineKeys } = useMemo(() => transformSeries(timeSeriesData?.series), [timeSeriesData]);
  const regionData = useMemo(() => {
    const first = regionSeriesData?.series?.[0];
    if (!first) return [];
    return first.points.map((point, idx) => ({
      name: String(point.x),
      value: point.y,
      color: palette[idx % palette.length],
    }));
  }, [regionSeriesData]);

  const handleGenerateDashboards = async () => {
    if (!datasetId) {
      toast({
        title: "Dataset not ready",
        description: "Upload and ingest a dataset first.",
        variant: "destructive",
      });
      return;
    }
    setIsGeneratingCharts(true);
    try {
      const result = await generateDashboards(datasetId);
      setCharts(result.charts);
      toast({ title: "Dashboards ready", description: "Charts generated from your dataset." });
    } catch (error) {
      console.error(error);
      toast({
        title: "Dashboards failed",
        description: "Could not generate dashboards right now.",
        variant: "destructive",
      });
    } finally {
      setIsGeneratingCharts(false);
    }
  };

  const handleAskAI = async () => {
    if (!datasetId) {
      toast({
        title: "Dataset not ready",
        description: "Upload and ingest a dataset first.",
        variant: "destructive",
      });
      return;
    }
    setIsAskingAI(true);
    try {
      const result = await askAI(workspaceId, datasetId, aiQuestion);
      const lines = result.answer
        .split(/\n+/)
        .map((line) => line.replace(/^[-*•]\s*/, "").trim())
        .filter(Boolean);
      setAiNarrative(lines[0] ?? result.answer);
      setAiBullets(lines.length > 1 ? lines : []);
    } catch (error) {
      console.error(error);
      toast({
        title: "AI unavailable",
        description: "The local model did not respond in time.",
        variant: "destructive",
      });
    } finally {
      setIsAskingAI(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!datasetId) {
      toast({
        title: "Dataset not ready",
        description: "Upload and ingest a dataset first.",
        variant: "destructive",
      });
      return;
    }
    setIsGeneratingReport(true);
    try {
      const result = await generateReport({
        datasetId,
        selectedChartIds: charts.map((chart) => chart.id),
        narrativeBlocks: aiBullets.map((body) => ({ body })),
      });
      setReportUrl(result.download_url);
      toast({ title: "Report ready", description: "Download your narrated PDF." });
    } catch (error) {
      console.error(error);
      toast({
        title: "Report failed",
        description: "Could not render the report.",
        variant: "destructive",
      });
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <div className="space-y-10">
      <PageHeader
        title="Impact intelligence"
        description={`Review dynamic KPIs, AI-ready narratives, and ready-to-export insights—all powered by first-party analytics. Dataset: ${
          datasetId ? datasetId.slice(0, 8) : "pending"
        }`}
        actions={
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="rounded-full border-primary/40 text-primary" onClick={handleGenerateDashboards} disabled={isGeneratingCharts}>
              <Sparkles className="mr-2 h-4 w-4" />
              {isGeneratingCharts ? "Generating" : "Generate dashboards"}
            </Button>
            <Button
              size="sm"
              className="rounded-full bg-primary px-5"
              onClick={handleGenerateReport}
              disabled={isGeneratingReport}
            >
              <FileBarChart className="mr-2 h-4 w-4" />
              {isGeneratingReport ? "Rendering" : "Generate report"}
            </Button>
            {reportUrl && (
              <Button asChild variant="ghost" size="sm" className="rounded-full">
                <a href={reportUrl} target="_blank" rel="noopener noreferrer">
                  <Download className="mr-2 h-4 w-4" /> Download PDF
                </a>
              </Button>
            )}
          </div>
        }
      />

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.length === 0 ? (
          <p className="text-sm text-muted-foreground">No KPI data available yet.</p>
        ) : (
          kpis.map((kpi, idx) => {
            const trend = trendForDelta(kpi.delta);
            return (
              <KpiCard
                key={`${kpi.label}-${idx}`}
                title={kpi.label}
                value={formatKpiValue(kpi)}
                trend={{ direction: trend.direction, value: trend.label }}
              />
            );
          })
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-8">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Input
                value={aiQuestion}
                onChange={(event) => setAiQuestion(event.target.value)}
                placeholder="Ask the AI about your dataset"
              />
              <Button size="sm" onClick={handleAskAI} disabled={isAskingAI}>
                <Sparkles className="mr-2 h-4 w-4" />
                {isAskingAI ? "Thinking" : "Ask AI"}
              </Button>
            </div>
            <AINarrativeCard
              narrative={aiNarrative}
              bullets={aiBullets}
              highlights={kpis.slice(0, 3).map((kpi) => `${kpi.label}: ${formatKpiValue(kpi)}`)}
            />
          </div>

          <ChartBlock
            title="Impact over time"
            description="Aggregated beneficiaries and completions grouped by year."
          >
            {lineData.length === 0 ? (
              <p className="py-6 text-sm text-muted-foreground">No time-series data available yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="x" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {lineKeys.map(({ key, label, color }) => (
                    <Line key={key} type="monotone" dataKey={key} name={label} stroke={color} strokeWidth={2} dot={{ r: 3 }} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </ChartBlock>
        </div>

        <div className="space-y-6">
          <ChartBlock
            title="Impact by region"
            description="Breakdown of beneficiaries across active regions."
          >
            {regionData.length === 0 ? (
              <p className="py-6 text-sm text-muted-foreground">No regional data mapped yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={regionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value">
                    {regionData.map((entry, idx) => (
                      <Cell key={`cell-${entry.name}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartBlock>

          <ChartBlock
            title="Share of impact"
            description="Quick composition snapshot using the same regional data."
          >
            {regionData.length === 0 ? (
              <p className="py-6 text-sm text-muted-foreground">Awaiting data uploads.</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Tooltip />
                  <Pie data={regionData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={4}>
                    {regionData.map((entry) => (
                      <Cell key={`slice-${entry.name}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            )}
          </ChartBlock>
        </div>
      </div>

      {charts.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2">
          {charts.map((chart) => (
            <ChartBlock key={chart.id} title={chart.title} description="Auto-generated from your dataset">
              <Plot
                data={(chart.spec.data as any[]) ?? []}
                layout={{ height: 360, autosize: true, ...(chart.spec.layout as Record<string, unknown>) }}
                useResizeHandler
                style={{ width: "100%", height: "100%" }}
                config={{ displayModeBar: false }}
              />
            </ChartBlock>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
