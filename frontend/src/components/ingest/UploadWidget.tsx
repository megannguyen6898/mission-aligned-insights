import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload as UploadIcon } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

interface JobStatus {
  status: string;
  error?: any;
}

const POLL_INTERVAL_MS = 2000;

const UploadWidget: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [sheetErrors, setSheetErrors] = useState<Record<string, string[]>>({});
  const [jobId, setJobId] = useState<number | null>(null);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;
    if (jobId !== null) {
      timer = setInterval(async () => {
        try {
          const res = await api.get<JobStatus>(`/ingest/jobs/${jobId}`);
          if (res.data.status === "success") {
            clearInterval(timer!);
            toast({ title: "Ingestion complete", description: "File processed successfully" });
            setJobId(null);
          } else if (res.data.status === "failed") {
            clearInterval(timer!);
            const err = res.data.error;
            const parsed: Record<string, string[]> = {};
            if (err) {
              let detail: any = err;
              if (typeof err.error === "string") {
                try {
                  detail = JSON.parse(err.error);
                } catch {
                  detail = err;
                }
              }
              if (detail.sheet && Array.isArray(detail.missing)) {
                parsed[detail.sheet] = detail.missing;
              } else if (detail.sheet && detail.error) {
                parsed[detail.sheet] = [String(detail.error)];
              } else if (detail.error) {
                parsed["General"] = [String(detail.error)];
              }
            }
            setSheetErrors(parsed);
            toast({
              title: "Ingestion failed",
              description: "See errors below",
              variant: "destructive",
            });
            setJobId(null);
          }
        } catch (pollErr) {
          console.error(pollErr);
          clearInterval(timer!);
          setJobId(null);
        }
      }, POLL_INTERVAL_MS);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [jobId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setSheetErrors({});
    try {
      const signed = await api.post(
        "/ingest/uploads:signed-url",
        {
          filename: file.name,
          mime: file.type,
          size: file.size,
        }
      );
      const { url, fields, upload_id } = signed.data;
      const form = new FormData();
      Object.entries(fields).forEach(([k, v]) => form.append(k, v as string));
      form.append("file", file);
      await fetch(url, { method: "POST", body: form });

      const jobRes = await api.post("/ingest/jobs", { upload_id });
      setJobId(jobRes.data.job_id);
      toast({ title: "File uploaded", description: "Processing has started" });
    } catch (err) {
      console.error(err);
      toast({
        title: "Upload failed",
        description: "Could not upload file",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <UploadIcon className="h-5 w-5" />
          <span>Upload Data</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Input
            type="file"
            accept=".xlsx,.csv"
            onChange={handleFileUpload}
            disabled={isUploading}
          />
          {isUploading && <p className="text-sm text-gray-500">Uploading...</p>}
          {Object.keys(sheetErrors).length > 0 && (
            <div className="space-y-4">
              {Object.entries(sheetErrors).map(([sheet, errors]) => (
                <div key={sheet}>
                  <h4 className="font-medium">{sheet}</h4>
                  <ul className="list-disc pl-5 text-sm text-red-600">
                    {errors.map((err, idx) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default UploadWidget;

