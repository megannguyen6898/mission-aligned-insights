import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadPanel } from "@/components/upload/UploadPanel";
import { useToast } from "@/hooks/use-toast";
import { uploadFile, validateUpload, ingestUpload } from "@/api/uploads";
import { FilePreviewDrawer } from "@/components/upload/FilePreviewDrawer";

interface Step {
  name: string;
  status: "idle" | "pending" | "done" | "error";
}

const Upload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [steps, setSteps] = useState<Step[]>([
    { name: "Upload", status: "idle" },
    { name: "Validate", status: "idle" },
    { name: "Ingest", status: "idle" },
  ]);
  const [errors, setErrors] = useState<string[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleFileUpload = async (file: File) => {

    setIsUploading(true);
    setSteps([
      { name: "Upload", status: "pending" },
      { name: "Validate", status: "idle" },
      { name: "Ingest", status: "idle" },
    ]);
    setErrors([]);

    try {
      const { data } = await uploadFile(file);
      setSteps((s) => [{ ...s[0], status: "done" }, s[1], s[2]]);

      const validation = await validateUpload(data.upload_id);
      if (validation.data.errors && validation.data.errors.length > 0) {
        setSteps((s) => [s[0], { ...s[1], status: "error" }, s[2]]);
        setErrors(validation.data.errors);
        return;
      }
      setSteps((s) => [s[0], { ...s[1], status: "done" }, s[2]]);

      await ingestUpload(data.upload_id);
      setSteps((s) => [s[0], s[1], { ...s[2], status: "done" }]);
      setUploadedFiles((prev) => [...prev, file]);
      toast({ title: "Upload complete", description: file.name });
      navigate("/dashboard");
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
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-foreground mb-2">Upload Data</h1>
        <p className="text-lg text-muted-foreground">
          Upload your impact data to begin analysis and reporting
        </p>
      </div>

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
