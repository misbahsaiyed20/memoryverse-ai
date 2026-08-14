"use client";

import { useRef, useState, type DragEvent } from "react";
import { UploadCloud } from "lucide-react";

import { uploadDocument, type DocumentItem } from "@/lib/documents-api";

interface UploadingFile {
  id: string;
  name: string;
  progress: number;
  error?: string;
}

interface UploadDropzoneProps {
  onUploaded: (doc: DocumentItem) => void;
}

const ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "txt", "png", "jpg", "jpeg"];
const MAX_SIZE_BYTES = 25 * 1024 * 1024;

function validateClientSide(file: File): string | null {
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  if (!ALLOWED_EXTENSIONS.includes(ext)) return `.${ext} isn't a supported file type.`;
  if (file.size === 0) return "File is empty.";
  if (file.size > MAX_SIZE_BYTES) return "File exceeds the 25 MB limit.";
  return null;
}

export function UploadDropzone({ onUploaded }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [uploads, setUploads] = useState<UploadingFile[]>([]);

  function handleFiles(files: FileList | null) {
    if (!files) return;

    Array.from(files).forEach((file) => {
      const uploadId = `${file.name}-${Date.now()}-${Math.random()}`;
      const clientError = validateClientSide(file);

      if (clientError) {
        setUploads((prev) => [...prev, { id: uploadId, name: file.name, progress: 0, error: clientError }]);
        return;
      }

      setUploads((prev) => [...prev, { id: uploadId, name: file.name, progress: 0 }]);

      const { promise } = uploadDocument(file, (percent) => {
        setUploads((prev) => prev.map((u) => (u.id === uploadId ? { ...u, progress: percent } : u)));
      });

      promise
        .then((doc) => {
          setUploads((prev) => prev.filter((u) => u.id !== uploadId));
          onUploaded(doc);
        })
        .catch((error: Error) => {
          setUploads((prev) => prev.map((u) => (u.id === uploadId ? { ...u, error: error.message } : u)));
        });
    });
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    handleFiles(event.dataTransfer.files);
  }

  function dismissUpload(id: string) {
    setUploads((prev) => prev.filter((u) => u.id !== id));
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition-all duration-200 ${
          dragging
            ? "scale-[1.01] border-accent bg-accent-soft"
            : "border-border bg-surface hover:border-accent/40 hover:bg-accent-soft/40"
        }`}
      >
        <span
          className={`flex h-11 w-11 items-center justify-center rounded-full transition-colors ${
            dragging ? "bg-accent text-accent-foreground" : "bg-accent-soft text-accent"
          }`}
        >
          <UploadCloud size={20} strokeWidth={2.2} />
        </span>
        <p className="mt-3.5 text-sm font-medium text-foreground">
          {dragging ? "Drop to upload" : "Drag & drop a file, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-muted">PDF, DOC, DOCX, TXT, PNG, JPG — up to 25 MB</p>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {uploads.length > 0 && (
        <ul className="mt-4 space-y-2">
          {uploads.map((u) => (
            <li key={u.id} className="rounded-xl border border-border bg-surface px-4 py-3 text-sm shadow-card">
              <div className="flex items-center justify-between gap-3">
                <span className="truncate text-foreground">{u.name}</span>
                {u.error ? (
                  <button onClick={() => dismissUpload(u.id)} className="shrink-0 text-xs text-muted hover:text-foreground">
                    Dismiss
                  </button>
                ) : (
                  <span className="shrink-0 text-muted">{u.progress}%</span>
                )}
              </div>
              {u.error ? (
                <p className="mt-1 text-red-600">{u.error}</p>
              ) : (
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-border">
                  <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${u.progress}%` }} />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
