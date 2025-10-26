import React from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { KpiCard } from "@/components/common/KpiCard";
import { AINarrativeCard } from "@/components/dashboard/AINarrativeCard";
import { ChartBlock } from "@/components/charts/ChartBlock";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Target, TrendingUp, DollarSign, Download, FileBarChart, ArrowRight } from "lucide-react";

const kpis = [
  {
    title: "Lives impacted",
    value: "2,547",
    trend: { direction: "up" as const, value: "+12% vs last month" },
    icon: <Users className="h-5 w-5" />,
  },
  {
    title: "Programs active",
    value: "23",
    trend: { direction: "up" as const, value: "+3 this quarter" },
    icon: <Target className="h-5 w-5" />,
  },
  {
    title: "SDG alignment",
    value: "89%",
    trend: { direction: "neutral" as const, value: "Holding steady" },
    icon: <TrendingUp className="h-5 w-5" />,
  },
  {
    title: "Social ROI",
    value: "$4.2M",
    trend: { direction: "up" as const, value: "+18% YoY" },
    icon: <DollarSign className="h-5 w-5" />,
  },
];

const impactByRegion = [
  { label: "East Africa", value: 62 },
  { label: "South Asia", value: 48 },
  { label: "Latin America", value: 37 },
  { label: "Europe", value: 28 },
];

const sdgHighlights = [
  {
    title: "SDG 4 • Quality Education",
    narrative:
      "Coaching support and coding bootcamps increased completion rates to 92%. AI flagged strong upward momentum for young women in Nairobi.",
  },
  {
    title: "SDG 8 • Decent Work",
    narrative:
      "Microfinance pilot created 180 new jobs in the last quarter. Loan repayment rates remain above 95% across cohorts.",
  },
  {
    title: "SDG 13 • Climate Action",
    narrative:
      "Climate innovation fund backed 14 new ventures. Carbon reduction estimates are trending ahead of target by 9%.",
  },
];

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-10">
      <PageHeader
        title="Impact intelligence"
        description="Review your most important outcomes, AI narratives, and ready-to-share insights. Everything ties back to the lineage established during mapping."
        actions={
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="rounded-full border-primary/40 text-primary">
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
            <Button size="sm" className="rounded-full bg-primary px-5">
              <FileBarChart className="mr-2 h-4 w-4" />
              Generate report
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.title} {...kpi} className="rounded-2xl bg-card/95" />
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-8">
          <AINarrativeCard
            narrative="Youth-focused programs reached 2,547 beneficiaries with a 12% month-over-month uplift. The biggest contributor was the Nairobi Skills Hub, adding 410 participants and maintaining a 92% graduation rate. Drop-off remains lowest where mentorship was embedded from week two."
            highlights={["Skills Hub ↑ 18%", "Attrition 4%", "Equity lens maintained"]}
          />

          <ChartBlock
            title="Impact distribution by region"
            description="Categorised by unique beneficiaries across active programs. Target confidence ≥ 0.8 for comparison readiness."
          >
            <div className="space-y-4">
              {impactByRegion.map((region) => (
                <div key={region.label} className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    <span>{region.label}</span>
                    <span>{region.value}%</span>
                  </div>
                  <div className="h-3 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{ width: `${Math.max(10, region.value)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-6 text-xs text-muted-foreground leading-relaxed">
              AI summary: East Africa remains the growth engine, while Latin America shows steady gains after the curriculum refresh.
            </p>
          </ChartBlock>
        </div>

        <div className="space-y-6">
          <Card className="rounded-2xl border-border/60 bg-card soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">Data quality & lineage</CardTitle>
              <CardDescription className="text-sm leading-relaxed text-muted-foreground">
                Mapping approvals synced 3 days ago. No validation issues detected in the last ingest cycle.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm leading-relaxed text-muted-foreground">
              <div className="rounded-2xl border border-border/60 bg-muted/30 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground/80">
                  Traceability
                </p>
                <p className="mt-2 text-xs leading-relaxed">
                  KPI cards reference Upload Batch #21 • Mapping version 3.2 • Report template “Annual Board.”
                </p>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-primary/20 bg-primary/10 px-4 py-3 text-xs text-primary">
                <Badge variant="secondary" className="rounded-full bg-primary text-primary-foreground">
                  98% coverage
                </Badge>
                Required dimensions are populated. Continue collecting socio-economic impact disaggregation.
              </div>
              <Button variant="ghost" className="group inline-flex w-full items-center justify-start gap-2 px-0 text-sm text-primary hover:text-primary">
                Review data lineage
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </CardContent>
          </Card>

          <Card className="rounded-2xl border-border/60 bg-card soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">SDG insights</CardTitle>
              <CardDescription>See which global goals your programs are driving forward.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {sdgHighlights.map(({ title, narrative }) => (
                <div key={title} className="space-y-2 rounded-2xl border border-border/50 bg-muted/40 p-4">
                  <p className="text-sm font-semibold text-foreground">{title}</p>
                  <p className="text-xs leading-relaxed text-muted-foreground">{narrative}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
