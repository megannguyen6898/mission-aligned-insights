import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Upload as UploadIcon, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UploadStep {
  name: string;
  status: 'idle' | 'pending' | 'done' | 'error';
}

interface UploadPanelProps {
  onFileSelect: (file: File) => Promise<void>;
  steps?: UploadStep[];
  errors?: string[];
  uploadedFiles?: File[];
  isUploading?: boolean;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
  onFileSelect,
  steps = [],
  errors = [],
  uploadedFiles = [],
  isUploading = false,
}) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelect(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  const completedSteps = steps.filter((s) => s.status === 'done').length;
  const progress = steps.length > 0 ? (completedSteps / steps.length) * 100 : 0;

  return (
    <Card className="soft-shadow-lg border-border/50 rounded-2xl">
      <CardHeader>
        <CardTitle>Upload Impact Data</CardTitle>
        <CardDescription>
          Upload your Excel file (.xlsx) to begin analyzing your impact
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Drop Zone */}
        <div
          className={cn(
            'border-2 border-dashed rounded-2xl p-12 text-center transition-colors',
            dragActive
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary/50 hover:bg-accent/50',
            isUploading && 'opacity-50 pointer-events-none'
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <UploadIcon className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <div className="space-y-2">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="text-lg font-medium text-foreground">Click to upload</span>
              <span className="text-muted-foreground"> or drag and drop</span>
            </label>
            <Input
              id="file-upload"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileInput}
              className="hidden"
              disabled={isUploading}
            />
            <p className="text-sm text-muted-foreground">Excel files up to 10MB</p>
          </div>
        </div>

        {/* Progress Steps */}
        {steps.length > 0 && (
          <div className="space-y-4">
            <Progress value={progress} className="h-2" />
            <div className="space-y-2">
              {steps.map((step) => (
                <div key={step.name} className="flex items-center gap-3 text-sm">
                  {step.status === 'done' ? (
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                  ) : step.status === 'error' ? (
                    <AlertCircle className="h-4 w-4 text-destructive" />
                  ) : step.status === 'pending' ? (
                    <div className="h-4 w-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-muted" />
                  )}
                  <span
                    className={cn(
                      step.status === 'done' && 'text-foreground',
                      step.status === 'error' && 'text-destructive',
                      step.status === 'pending' && 'text-primary font-medium',
                      step.status === 'idle' && 'text-muted-foreground'
                    )}
                  >
                    {step.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Errors */}
        {errors.length > 0 && (
          <div className="rounded-xl border border-destructive/50 bg-destructive/5 p-4">
            <p className="text-sm font-medium text-destructive mb-2">Upload errors:</p>
            <ul className="space-y-1 text-sm text-destructive/90">
              {errors.map((err, idx) => (
                <li key={idx}>• {err}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Uploaded Files */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm font-medium text-foreground">Uploaded files:</p>
            <div className="space-y-2">
              {uploadedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 rounded-xl bg-accent border border-border"
                >
                  <FileText className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-foreground flex-1">
                    {file.name}
                  </span>
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
