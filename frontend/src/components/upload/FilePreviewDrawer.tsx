import React from "react";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { FileText, Loader2, Sparkles, Download } from "lucide-react";

interface FilePreviewDrawerProps {
  file: File | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const readableTypes = ["text/", "application/json", "application/xml", "application/csv", "text/csv"];

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes)) return "0 B";
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  const value = bytes / Math.pow(1024, index);
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[index]}`;
}

function isReadableFile(file: File): boolean {
  return readableTypes.some((type) => file.type.startsWith(type)) || /\.(csv|txt|json|xml)$/i.test(file.name);
}

export const FilePreviewDrawer: React.FC<FilePreviewDrawerProps> = ({ file, open, onOpenChange }) => {
  const [preview, setPreview] = React.useState<string>("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [objectUrl, setObjectUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!file) {
      setPreview("");
      setError(null);
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        setObjectUrl(null);
      }
      return;
    }

    const url = URL.createObjectURL(file);
    setObjectUrl(url);

    if (!open) {
      return () => {
        URL.revokeObjectURL(url);
      };
    }

    if (!isReadableFile(file)) {
      setPreview("");
      setError("Preview is available for CSV, JSON, or text files. Download to inspect Excel workbooks.");
      return () => {
        URL.revokeObjectURL(url);
      };
    }

    setIsLoading(true);
    setError(null);

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      if (typeof result === "string") {
        const lines = result.split(/\r?\n/).slice(0, 40);
        setPreview(lines.join("\n"));
      } else {
        try {
          const text = new TextDecoder().decode(result as ArrayBuffer);
          setPreview(text.split(/\r?\n/).slice(0, 40).join("\n"));
        } catch (err) {
          setError("Unable to render file preview.");
        }
      }
      setIsLoading(false);
    };
    reader.onerror = () => {
      setError("We couldn't read this file for preview.");
      setIsLoading(false);
    };

    reader.readAsText(file);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file, open]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full max-w-xl flex-col gap-0 p-0">
        <SheetHeader className="space-y-1 border-b border-border px-6 py-5 text-left">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/10 p-2 text-primary">
              <FileText className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <SheetTitle className="text-lg">{file?.name ?? "File preview"}</SheetTitle>
              <SheetDescription>{file ? "Review file details before ingestion" : "Select a file to preview"}</SheetDescription>
            </div>
          </div>
        </SheetHeader>

        <div className="flex-1 space-y-6 px-6 py-6">
          {file ? (
            <>
              <div className="grid gap-3 rounded-2xl border border-border/60 bg-muted/40 p-4">
                <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  <Badge variant="outline" className="rounded-full">
                    {file.type || "Unknown type"}
                  </Badge>
                  <span>{formatBytes(file.size)}</span>
                  {file.lastModified && (
                    <span>
                      Updated {new Date(file.lastModified).toLocaleString()}
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  Preview supports CSV, JSON, and plain text files. Excel workbooks are available to download once ingestion finishes.
                </p>
              </div>

              <Separator className="border-border/70" />

              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-muted-foreground">Preview</h3>
                {objectUrl && (
                  <Button asChild variant="outline" size="sm">
                    <a href={objectUrl} download={file.name}>
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </a>
                  </Button>
                )}
              </div>

              <div className="relative min-h-[200px] overflow-hidden rounded-2xl border border-border/60 bg-background/80">
                {isLoading ? (
                  <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center text-sm text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    Reading file preview…
                  </div>
                ) : error ? (
                  <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center text-sm text-muted-foreground">
                    <Sparkles className="h-6 w-6 text-primary" />
                    {error}
                  </div>
                ) : preview ? (
                  <ScrollArea className="h-72">
                    <pre className="whitespace-pre-wrap break-words bg-background p-4 text-xs leading-5 text-foreground">
                      {preview}
                    </pre>
                  </ScrollArea>
                ) : (
                  <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center text-sm text-muted-foreground">
                    <Sparkles className="h-6 w-6 text-primary" />
                    This file looks great. Download it to inspect the full workbook.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center text-muted-foreground">
              <Sparkles className="h-10 w-10 text-primary" />
              <p className="text-sm">Upload a file to unlock a smart preview.</p>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};
