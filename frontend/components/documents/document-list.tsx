"use client";

import { useState } from "react";
import { Brain, Download, Loader2, Pencil, Scissors, Sparkles, Trash2 } from "lucide-react";

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
  onChunk: (id: string) => Promise<void>;
  onExtract: (id: string) => Promise<{ nodes_created: number; edges_created: number }>;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function DocumentList({ documents, onRename, onDelete, onProcess, onChunk, onExtract }: DocumentListProps) {
  const [renaming, setRenaming] = useState<DocumentItem | null>(null);
  const [deleting, setDeleting] = useState<DocumentItem | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());
  const [chunkingIds, setChunkingIds] = useState<Set<string>>(new Set());
  const [extractingIds, setExtractingIds] = useState<Set<string>>(new Set());
  // Per-document status line for chunk/extract results and errors — these
  // two actions have no status field on Document to reflect, unlike
  // process, so feedback has to live here instead of in a StatusBadge.
  const [actionMessages, setActionMessages] = useState<Record<string, { text: string; isError: boolean }>>({});

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

  async function handleChunk(doc: DocumentItem) {
    setChunkingIds((prev) => new Set(prev).add(doc.id));
    setActionMessages((prev) => { const next = { ...prev }; delete next[doc.id]; return next; });
    try {
      await onChunk(doc.id);
      setActionMessages((prev) => ({ ...prev, [doc.id]: { text: "Chunking started.", isError: false } }));
    } catch (err) {
      setActionMessages((prev) => ({
        ...prev,
        [doc.id]: { text: err instanceof Error ? err.message : "Chunking failed.", isError: true },
      }));
    } finally {
      setChunkingIds((prev) => {
        const next = new Set(prev);
        next.delete(doc.id);
        return next;
      });
    }
  }

  async function handleExtract(doc: DocumentItem) {
    setExtractingIds((prev) => new Set(prev).add(doc.id));
    setActionMessages((prev) => { const next = { ...prev }; delete next[doc.id]; return next; });
    try {
      // Synchronous on the backend — can take a while (one Gemini call per
      // 5 chunks). The spinner stays until this actually resolves.
      const result = await onExtract(doc.id);
      setActionMessages((prev) => ({
        ...prev,
        [doc.id]: {
          text: `Extracted ${result.nodes_created} knowledge node${result.nodes_created === 1 ? "" : "s"}, ${result.edges_created} relationship${result.edges_created === 1 ? "" : "s"}.`,
          isError: false,
        },
      }));
    } catch (err) {
      setActionMessages((prev) => ({
        ...prev,
        [doc.id]: { text: err instanceof Error ? err.message : "Extraction failed.", isError: true },
      }));
    } finally {
      setExtractingIds((prev) => {
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
          // Chunk/Extract both require PROCESSED — the backend enforces this
          // itself (409 otherwise), this just avoids showing a button that
          // would immediately fail. There's no has_chunks/has_extracted flag
          // on DocumentItem, so a document that's already been chunked or
          // extracted still shows the button; clicking it again surfaces the
          // backend's own "already chunked/extracted" message below instead
          // of silently doing nothing.
          const canChunkOrExtract = doc.status === "PROCESSED";
          const isChunking = chunkingIds.has(doc.id);
          const isExtracting = extractingIds.has(doc.id);
          const message = actionMessages[doc.id];

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
                  {canChunkOrExtract && (
                    <button
                      onClick={() => handleChunk(doc)}
                      disabled={isChunking}
                      className="rounded-full p-2 text-muted transition-colors hover:bg-accent-soft hover:text-accent disabled:opacity-50"
                      title="Chunk"
                      aria-label={`Chunk ${doc.title}`}
                    >
                      {isChunking ? <Loader2 size={16} className="animate-spin" /> : <Scissors size={16} />}
                    </button>
                  )}
                  {canChunkOrExtract && (
                    <button
                      onClick={() => handleExtract(doc)}
                      disabled={isExtracting}
                      className="rounded-full p-2 text-muted transition-colors hover:bg-accent-soft hover:text-accent disabled:opacity-50"
                      title="Extract knowledge"
                      aria-label={`Extract knowledge from ${doc.title}`}
                    >
                      {isExtracting ? <Loader2 size={16} className="animate-spin" /> : <Brain size={16} />}
                    </button>
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
              {message && (
                <p className={`mt-2 pl-9 text-xs ${message.isError ? "text-red-600" : "text-emerald-700"}`}>
                  {message.text}
                </p>
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
