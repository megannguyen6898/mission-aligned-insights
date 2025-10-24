import React, { useEffect, useState } from "react";
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
import { FileText, Loader2 } from "lucide-react";

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
    }, 1000);
    return () => clearInterval(interval);
  }, [reportId]);

  const generate = async () => {
    if (!selected) return;
    setStatus("queued");
    try {
      const { data } = await createReport(selected);
      setReportId(data.report_id);
      toast({ title: "Report started" });
    } catch (err) {
      console.error("Report generation failed", err);
      toast({
        title: "Report failed",
        description: "Could not start report",
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
      a.download = `report-${reportId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-foreground mb-2">Impact Reports</h1>
        <p className="text-lg text-muted-foreground">
          Generate comprehensive impact reports for your stakeholders
        </p>
      </div>

      {/* Report Generator Card */}
      <Card className="soft-shadow-lg border-border/50 rounded-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Generate New Report
          </CardTitle>
          <CardDescription>Select a template and generate a custom report</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <Select 
              value={selected?.toString()} 
              onValueChange={(v) => setSelected(Number(v))}
              disabled={status === "queued"}
            >
              <SelectTrigger className="w-[320px]">
                <SelectValue placeholder="Select report template" />
              </SelectTrigger>
              <SelectContent className="bg-popover">
                {templates.map((t) => (
                  <SelectItem key={t.id} value={t.id.toString()}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              onClick={generate} 
              disabled={!selected || status === "queued"}
              className="bg-primary hover:bg-primary/90"
            >
              {status === "queued" ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Report'
              )}
            </Button>
          </div>
          
          {status && status !== "idle" && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Status:</span>
              <span className="font-medium text-foreground capitalize">{status}</span>
            </div>
          )}
          
          {status === "ready" && (
            <Button onClick={download} variant="outline" className="border-primary text-primary">
              Download Report
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Report Tabs */}
      <ReportTabs
        onExportPDF={() => {
          toast({ title: "Exporting PDF...", description: "Your report will download shortly" });
        }}
        onExportExcel={() => {
          toast({ title: "Exporting Excel...", description: "Your data will download shortly" });
        }}
      />
    </div>
  );
};

export default Reports;
