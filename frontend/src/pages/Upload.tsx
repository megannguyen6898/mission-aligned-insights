import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Upload as UploadIcon, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { uploadFile, validateUpload, ingestUpload } from "@/api/uploads";

interface Step {
  name: string;
  status: "idle" | "pending" | "done" | "error";
}

const Upload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [steps, setSteps] = useState<Step[]>([
    { name: "Upload", status: "idle" },
    { name: "Validate", status: "idle" },
    { name: "Ingest", status: "idle" },
  ]);
  const [errors, setErrors] = useState<string[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

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
      <h1 className="text-3xl font-bold text-gray-900">Upload Data</h1>

      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
          <CardDescription>Upload your impact data (.xlsx)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="text-lg font-medium text-gray-900">Click to upload</span>
                <span className="text-gray-500"> or drag and drop</span>
              </label>
              <Input
                id="file-upload"
                type="file"
                accept=".xlsx"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">Only .xlsx files up to 10MB</p>
          </div>

          {uploadedFiles.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Uploaded Files</h4>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center p-2 bg-gray-50 rounded">
                    <FileText className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm">{file.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(isUploading || steps.some((s) => s.status !== "idle")) && (
            <ul className="mt-4 space-y-1 text-sm">
              {steps.map((step) => (
                <li key={step.name}>
                  {step.name}: {step.status}
                </li>
              ))}
            </ul>
          )}

          {errors.length > 0 && (
            <ul className="mt-2 text-sm text-red-600 list-disc pl-4">
              {errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Upload;
