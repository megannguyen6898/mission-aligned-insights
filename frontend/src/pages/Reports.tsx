import React, { useEffect, useMemo, useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ReportTabs } from "@/components/report/ReportTabs";
import { useToast } from "@/hooks/use-toast";
import {
  listReportTemplates,
  createReport,
  getReportStatus,
  downloadReport,
} from "@/api/reports";
import { Badge } from "@/components/ui/badge";
import { Loader2, Sparkles, FileBarChart, CheckCircle2, AlertCircle, Clock } from "lucide-react";

interface Template {
  id: number;
  name: string;
  description?: string;
}

const Reports: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selected, setSelected] = useState<number | undefined>();
  const [reportId, setReportId] = useState<number | null>(null);
  const [status, setStatus] = useState<string>("");
  const { toast } = useToast();

  useEffect(() => {
    async function load() {
      try {
        const { data } = await listReportTemplates();
        setTemplates(data.templates || []);
      } catch (err) {
        console.error("Failed to load templates", err);
      }
    }
    load();
  }, []);

  useEffect(() => {
    if (!reportId) return;
    const interval = setInterval(async () => {
      const { data } = await getReportStatus(reportId);
      setStatus(data.status);
      if (data.status === "ready" || data.status === "failed") {
        clearInterval(interval);
      }
    }, 1200);
    return () => clearInterval(interval);
  }, [reportId]);

  const activeTemplate = useMemo(
    () => templates.find((template) => template.id === selected),
    [templates, selected]
  );

  const generate = async () => {
    if (!selected) return;
    setStatus("queued");
    try {
      const { data } = await createReport(selected);
      setReportId(data.report_id);
      toast({ title: "Report queued", description: "We’ll notify you when it’s ready." });
    } catch (err) {
      console.error("Report generation failed", err);
      toast({
        title: "Report failed",
        description: "Could not start report generation.",
        variant: "destructive",
      });
      setStatus("");
    }
  };

  const download = async () => {
    if (!reportId) return;
    try {
      const res = await downloadReport(reportId);
      const blob = new Blob([res.data], { type: res.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `impact-report-${reportId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed", err);
      toast({
        title: "Download failed",
        description: "Please try again or regenerate the report.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-10">
      <PageHeader
        title="Impact reporting studio"
        description="Build multi-level narratives for boards, programme teams, and investors. All reports trace back to trusted mappings and AI narrative cards."
        actions={
          reportId && status === "ready" ? (
            <Button onClick={download} size="sm" className="rounded-full bg-primary px-5">
              Download latest
            </Button>
          ) : null
        }
      />

      <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Card className="rounded-2xl border-border/60 bg-card/95 soft-shadow">
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardTitle className="text-lg font-semibold text-foreground">Generate a narrative-ready report</CardTitle>
              <CardDescription className="text-sm text-muted-foreground leading-relaxed">
                Choose a template tuned for your audience. AI will stitch together KPIs, mappings, and qualitative insight.
              </CardDescription>
            </div>
            <Badge className="rounded-full bg-primary/10 text-primary">SDG • Ops • SROI</Badge>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_200px]">
              <div className="space-y-2">
                <label htmlFor="report-template" className="text-sm font-medium text-foreground">
                  Report template
                </label>
                <Select
                  value={selected?.toString()}
                  onValueChange={(value) => setSelected(Number(value))}
                  disabled={status === "queued"}
                >
                  <SelectTrigger id="report-template" className="rounded-xl border-border/70 bg-background">
                    <SelectValue placeholder="Select report template" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id.toString()}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {activeTemplate?.description && (
                  <p className="text-xs text-muted-foreground leading-relaxed">{activeTemplate.description}</p>
                )}
              </div>

              <div className="flex flex-col gap-3 rounded-2xl border border-muted/50 bg-muted/30 p-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-2 text-muted-foreground/90">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Narrative intelligence
                </div>
                <p>Includes AI summaries under each section; edit in docs mode before exporting.</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                onClick={generate}
                disabled={!selected || status === "queued"}
                className="rounded-full bg-primary px-5"
              >
                {status === "queued" ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating…
                  </>
                ) : (
                  <>
                    <FileBarChart className="mr-2 h-4 w-4" />
                    Generate report
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                disabled={status === "queued"}
                className="rounded-full border-primary/40 text-primary"
              >
                Preview structure
              </Button>
              {status && (
                <Badge
                  variant="outline"
                  className={status === "failed" ? "border-destructive/40 text-destructive" : "border-primary/40 text-primary"}
                >
                  Status: {status}
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="rounded-2xl border-border/60 bg-card soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">Report activity</CardTitle>
              <CardDescription className="text-sm leading-relaxed text-muted-foreground">
                Track which teams recently generated reports and how they used them.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <div className="flex items-start gap-3 rounded-2xl border border-primary/20 bg-primary/10 p-4 text-primary">
                <CheckCircle2 className="mt-0.5 h-4 w-4" />
                <p className="leading-relaxed">
                  “Annual Board Update” was regenerated yesterday using fresh mapping approvals. Shared with 5 board members.
                </p>
              </div>
              <div className="flex items-start gap-3 rounded-2xl border border-border/40 bg-muted/30 p-4">
                <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <p className="leading-relaxed">
                  Operations weekly digest scheduled for Friday delivery. Confirms progress toward equitable hiring targets.
                </p>
              </div>
              <div className="flex items-start gap-3 rounded-2xl border border-destructive/30 bg-destructive/10 p-4 text-destructive">
                <AlertCircle className="mt-0.5 h-4 w-4" />
                <p className="leading-relaxed">
                  Investor-ready SROI report failed to publish last week. Re-run after mapping Province → Region fix.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <ReportTabs
        onExportPDF={() => {
          toast({ title: "Exporting PDF…", description: "Your report will download shortly." });
        }}
        onExportExcel={() => {
          toast({ title: "Exporting Excel…", description: "We’ll share the workbook when it’s ready." });
        }}
      />
    </div>
  );
};

export default Reports;
