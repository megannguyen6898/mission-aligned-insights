import React, { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import {
  listReportTemplates,
  createReport,
  getReportStatus,
  downloadReport,
} from "@/api/reports";

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
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Reports</h1>

      <Card>
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
          <CardDescription>Select a template and generate a report</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select value={selected?.toString()} onValueChange={(v) => setSelected(Number(v))}>
            <SelectTrigger className="w-[300px]">
              <SelectValue placeholder="Select template" />
            </SelectTrigger>
            <SelectContent>
              {templates.map((t) => (
                <SelectItem key={t.id} value={t.id.toString()}>
                  {t.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={generate} disabled={!selected || status === "queued"}>
            Generate Report
          </Button>
          {status && <p className="text-sm">Status: {status}</p>}
          {status === "ready" && (
            <Button onClick={download} variant="outline">
              Download
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
