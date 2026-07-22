"use client";

import { useState } from "react";
import { Download, Loader2, Pencil, Sparkles, Trash2 } from "lucide-react";

import { downloadDocument, type DocumentItem } from "@/lib/documents-api";
import { DocumentFileIcon } from "@/components/documents/file-icon";
import { StatusBadge } from "@/components/documents/status-badge";
import { RenameDialog } from "@/components/documents/rename-dialog";
import { DeleteConfirmDialog } from "@/components/documents/delete-confirm-dialog";

interface DocumentListProps {
  documents: DocumentItem[];
  onRename: (id: string, title: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onProcess: (id: string) => Promise<void>;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function DocumentList({ documents, onRename, onDelete, onProcess }: DocumentListProps) {
  const [renaming, setRenaming] = useState<DocumentItem | null>(null);
  const [deleting, setDeleting] = useState<DocumentItem | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

  async function handleDownload(doc: DocumentItem) {
    setDownloadError(null);
    try {
      await downloadDocument(doc.id, doc.original_filename);
    } catch {
      setDownloadError(`Couldn't download "${doc.title}". Try again.`);
    }
  }

  async function handleProcess(doc: DocumentItem) {
    setProcessingIds((prev) => new Set(prev).add(doc.id));
    try {
      await onProcess(doc.id);
    } finally {
      setProcessingIds((prev) => {
        const next = new Set(prev);
        next.delete(doc.id);
        return next;
      });
    }
  }

  return (
    <div className="mt-6">
      {downloadError && (
        <p className="mb-3 text-sm text-red-600" role="alert">
          {downloadError}
        </p>
      )}
      <div className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
        {documents.map((doc) => {
          const canProcess = doc.status === "UPLOADED" || doc.status === "FAILED";
          const isProcessing = doc.status === "PROCESSING";
          const isTriggering = processingIds.has(doc.id);

          return (
            <div key={doc.id} className="px-5 py-4">
              <div className="flex items-center gap-4">
                <DocumentFileIcon extension={doc.file_extension} className="shrink-0 text-muted" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">{doc.title}</p>
                  <p className="mt-0.5 text-xs text-muted">
                    {formatFileSize(doc.file_size)} · {formatDate(doc.created_at)}
                  </p>
                </div>
                <StatusBadge status={doc.status} />
                <div className="flex shrink-0 items-center gap-1">
                  {isProcessing ? (
                    <span className="flex items-center gap-1.5 p-2 text-xs text-muted" title="Processing…">
                      <Loader2 size={16} className="animate-spin" />
                    </span>
                  ) : (
                    canProcess && (
                      <button
                        onClick={() => handleProcess(doc)}
                        disabled={isTriggering}
                        className="rounded-full p-2 text-muted transition-colors hover:bg-accent-soft hover:text-accent disabled:opacity-50"
                        title={doc.status === "FAILED" ? "Retry processing" : "Process"}
                        aria-label={`${doc.status === "FAILED" ? "Retry processing" : "Process"} ${doc.title}`}
                      >
                        <Sparkles size={16} />
                      </button>
                    )
                  )}
                  <button
                    onClick={() => handleDownload(doc)}
                    className="rounded-full p-2 text-muted transition-colors hover:bg-accent-soft hover:text-accent"
                    title="Download"
                    aria-label={`Download ${doc.title}`}
                  >
                    <Download size={16} />
                  </button>
                  <button
                    onClick={() => setRenaming(doc)}
                    className="rounded-full p-2 text-muted transition-colors hover:bg-accent-soft hover:text-accent"
                    title="Rename"
                    aria-label={`Rename ${doc.title}`}
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => setDeleting(doc)}
                    className="rounded-full p-2 text-muted transition-colors hover:bg-red-50 hover:text-red-600"
                    title="Delete"
                    aria-label={`Delete ${doc.title}`}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              {doc.status === "FAILED" && doc.processing_error && (
                <p className="mt-2 pl-9 text-xs text-red-600">{doc.processing_error}</p>
              )}
            </div>
          );
        })}
      </div>

      {renaming && (
        <RenameDialog
          document={renaming}
          open={!!renaming}
          onOpenChange={(open) => !open && setRenaming(null)}
          onRename={onRename}
        />
      )}
      {deleting && (
        <DeleteConfirmDialog
          document={deleting}
          open={!!deleting}
          onOpenChange={(open) => !open && setDeleting(null)}
          onConfirm={onDelete}
        />
      )}
    </div>
  );
}
