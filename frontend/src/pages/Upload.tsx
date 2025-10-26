import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadPanel } from "@/components/upload/UploadPanel";
import { useToast } from "@/hooks/use-toast";
import { uploadFile, validateUpload, ingestUpload } from "@/api/uploads";
import { FilePreviewDrawer } from "@/components/upload/FilePreviewDrawer";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ListChecks, Lock, ShieldCheck, Sparkles } from "lucide-react";

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
  const navigate = useNavigate();
  const { toast } = useToast();

  const completedCount = useMemo(() => steps.filter((s) => s.status === "done").length, [steps]);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setSteps((prev) =>
      prev.map((step, idx) =>
        idx === 0 ? { ...step, status: "pending" } : { ...step, status: "idle" }
      )
    );
    setErrors([]);

    try {
      const { data } = await uploadFile(file);
      setSteps((prev) => prev.map((step, idx) => (idx === 0 ? { ...step, status: "done" } : step)));

      const validation = await validateUpload(data.upload_id);
      if (validation.data.errors && validation.data.errors.length > 0) {
        setSteps((prev) =>
          prev.map((step, idx) =>
            idx === 1 ? { ...step, status: "error" } : step
          )
        );
        setErrors(validation.data.errors);
        return;
      }
      setSteps((prev) =>
        prev.map((step, idx) => (idx === 1 ? { ...step, status: "done" } : step))
      );

      await ingestUpload(data.upload_id);
      setSteps((prev) =>
        prev.map((step, idx) => (idx === 2 ? { ...step, status: "done" } : step))
      );
      setUploadedFiles((prev) => [...prev, file]);
      toast({ title: "Upload complete", description: file.name });
      navigate("/mapping");
    } catch (error) {
      console.error(error);
      toast({
        title: "Upload failed",
        description: "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
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
