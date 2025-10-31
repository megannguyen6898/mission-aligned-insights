import React, { useEffect, useMemo, useState } from "react";
import { UploadPanel } from "@/components/upload/UploadPanel";
import { useToast } from "@/hooks/use-toast";
import type { AxiosError } from "axios";
import {
  completeUpload,
  getUploadWorkflow,
  presignUpload,
  triggerIngest,
  uploadToPresignedUrl,
  type WorkflowSummary,
} from "@/api/mvp";
import { FilePreviewDrawer } from "@/components/upload/FilePreviewDrawer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ListChecks, Lock, ShieldCheck, Sparkles } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface Step {
  name: string;
  status: "idle" | "pending" | "done" | "error";
  description: string;
}

const initialSteps: Step[] = [
  { name: "Upload", status: "idle", description: "Securely upload your source workbook" },
  { name: "Validate", status: "idle", description: "AI checks for structure, columns, and anomalies" },
  { name: "Ingest", status: "idle", description: "Data becomes available for mapping & dashboards" },
];

const Upload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [steps, setSteps] = useState<Step[]>(initialSteps);
  const [errors, setErrors] = useState<string[]>([]);
  const [uploadId, setUploadId] = useState<number | null>(null);
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowSummary | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();

  const completedCount = useMemo(() => steps.filter((s) => s.status === "done").length, [steps]);

  const mapStateToStepStatus = (state?: string): Step["status"] => {
    switch (state) {
      case "succeeded":
        return "done";
      case "running":
      case "queued":
        return "pending";
      case "failed":
        return "error";
      default:
        return "idle";
    }
  };

  const updateStepsFromWorkflow = (summary: WorkflowSummary | null) => {
    setSteps((prev) =>
      prev.map((step) => {
        switch (step.name) {
          case "Upload":
            return { ...step, status: summary ? mapStateToStepStatus(summary.upload.state) : step.status };
          case "Validate":
            return { ...step, status: summary ? mapStateToStepStatus(summary.validate.state) : step.status };
          case "Ingest":
            return { ...step, status: summary ? mapStateToStepStatus(summary.ingest.state) : step.status };
          default:
            return step;
        }
      })
    );
  };

  const extractErrorDetail = (error: unknown): string => {
    const axiosError = error as AxiosError<{ code?: string; message?: string }>;
    const detail = axiosError.response?.data;
    if (detail?.message) {
      return detail.message;
    }
    return axiosError.message || "Please try again";
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setSteps((prev) =>
      prev.map((step, idx) =>
        idx === 0 ? { ...step, status: "pending" } : { ...step, status: "idle" }
      )
    );
    setErrors([]);
    setWorkflow(null);
    setDatasetId(null);
    setUploadId(null);

    try {
      const workspaceId = user?.id ?? 1;
      const presign = await presignUpload({
        workspaceId,
        filename: file.name,
        mimeType: file.type || "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        sizeBytes: file.size,
      });

      await uploadToPresignedUrl(presign.url, file, presign.headers);

      setUploadId(presign.upload_id);
      setUploadedFiles((prev) => [...prev, file]);
      setSteps((prev) => prev.map((step, idx) => (idx === 0 ? { ...step, status: "done" } : step)));

      const summary = await completeUpload(presign.upload_id);
      setWorkflow(summary);
      updateStepsFromWorkflow(summary);
      const nextDatasetId = summary.validate.dataset_id ?? summary.ingest.dataset_id ?? null;
      setDatasetId(nextDatasetId ?? null);

      toast({ title: "Upload received", description: "Validation queued." });
    } catch (error) {
      console.error(error);
      toast({
        title: "Upload failed",
        description: extractErrorDetail(error),
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    if (!uploadId) {
      return;
    }

    let isMounted = true;
    const interval = setInterval(async () => {
      try {
        const summary = await getUploadWorkflow(uploadId);
        if (!isMounted) return;
        setWorkflow(summary);
        updateStepsFromWorkflow(summary);
        const newErrors = [] as string[];
        if (summary.validate.error) newErrors.push(summary.validate.error);
        if (summary.ingest.error) newErrors.push(summary.ingest.error);
        setErrors(newErrors);
        const nextDatasetId = summary.validate.dataset_id ?? summary.ingest.dataset_id ?? null;
        if (nextDatasetId) {
          setDatasetId(nextDatasetId);
        }
        if (summary.ingest.state === "succeeded") {
          toast({ title: "Ingest complete", description: "Dataset ready for dashboards." });
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Workflow poll failed", error);
      }
    }, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [uploadId]);

  useEffect(() => {
    if (datasetId) {
      sessionStorage.setItem("latest_dataset_id", datasetId);
    }
  }, [datasetId]);

  const handleIngest = async () => {
    if (!datasetId) return;
    try {
      await triggerIngest(datasetId);
      toast({ title: "Ingest started", description: "We are loading your dataset." });
    } catch (error) {
      toast({
        title: "Ingest failed",
        description: extractErrorDetail(error),
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-10">
      <PageHeader
        title="Upload impact data"
        description="Start with a clean Excel workbook and let ImpactView guide the rest. Your data stays encrypted in transit and we keep a full lineage from upload through reporting."
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
        <UploadPanel
          onFileSelect={handleFileUpload}
          steps={steps}
          errors={errors}
          uploadedFiles={uploadedFiles}
          isUploading={isUploading}
          onPreviewFile={(file) => {
            setPreviewFile(file);
            setIsPreviewOpen(true);
          }}
        />

        <div className="space-y-6">
          <Card className="rounded-2xl border-border/60 bg-card/80 soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">Workflow status</CardTitle>
              <CardDescription>
                {completedCount === steps.length
                  ? "Ready for mapping — confirm suggested alignments next."
                  : "Follow the steps to unlock confidence-backed mapping."}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {datasetId && workflow && ["queued", "failed"].includes(workflow.ingest.state) && (
                <Button size="sm" className="w-full" onClick={handleIngest}>
                  Start ingest
                </Button>
              )}
              <ul className="space-y-3">
                {steps.map((step) => (
                  <li key={step.name} className="rounded-xl border border-border/40 bg-background/70 px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-foreground">{step.name}</p>
                        <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
                      </div>
                      <Badge
                        variant="outline"
                        className={step.status === "done" ? "border-primary/40 text-primary" : step.status === "error" ? "border-destructive/40 text-destructive" : "border-border/70 text-muted-foreground"}
                      >
                        {step.status === "done" ? "Complete" : step.status === "pending" ? "In progress" : step.status === "error" ? "Needs review" : "Queued"}
                      </Badge>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="rounded-2xl border-primary/10 bg-primary/5 soft-shadow">
            <CardHeader className="space-y-3">
              <CardTitle className="flex items-center gap-2 text-base font-semibold text-primary">
                <ShieldCheck className="h-4 w-4" />
                Data trust commitments
              </CardTitle>
              <CardDescription className="text-sm text-primary/80">
                Your workbook is encrypted, versioned, and auditable at every step.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-primary/80">
              <div className="flex items-start gap-3">
                <Lock className="mt-0.5 h-4 w-4 shrink-0" />
                <p className="leading-relaxed">SOC2-ready storage with automatic expiry for unused uploads.</p>
              </div>
              <div className="flex items-start gap-3">
                <ListChecks className="mt-0.5 h-4 w-4 shrink-0" />
                <p className="leading-relaxed">Validation highlights missing required columns and schema drift.</p>
              </div>
              <div className="flex items-start gap-3">
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0" />
                <p className="leading-relaxed">AI detects outliers and shares confidence scores during mapping.</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <FilePreviewDrawer
        file={previewFile}
        open={isPreviewOpen}
        onOpenChange={(open) => {
          setIsPreviewOpen(open);
          if (!open) {
            setPreviewFile(null);
          }
        }}
      />
    </div>
  );
};

export default Upload;
