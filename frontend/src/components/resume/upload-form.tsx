"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface UploadFormProps {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

export function UploadForm({ onUpload, isLoading }: UploadFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        setSelectedFile(file);
        onUpload(file);
      }
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: isLoading,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors",
        isDragActive
          ? "border-primary bg-primary/5"
          : "border-muted-foreground/25 hover:border-primary/50",
        isLoading && "pointer-events-none opacity-60",
      )}
    >
      <input {...getInputProps()} />
      {isLoading ? (
        <>
          <Loader2 className="mb-4 h-10 w-10 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">
            Parsing resume and extracting skills...
          </p>
        </>
      ) : selectedFile ? (
        <>
          <FileText className="mb-4 h-10 w-10 text-primary" />
          <p className="font-medium">{selectedFile.name}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Drop a new file to replace
          </p>
        </>
      ) : (
        <>
          <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
          <p className="font-medium">
            {isDragActive ? "Drop your resume here" : "Upload your resume"}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Drag and drop a PDF file, or click to browse
          </p>
          <Button variant="outline" size="sm" className="mt-4">
            Browse files
          </Button>
        </>
      )}
    </div>
  );
}
