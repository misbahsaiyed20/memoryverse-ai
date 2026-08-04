"use client";

import { useEffect, useState } from "react";

import {
  listDocuments,
  renameDocument,
  deleteDocument,
  processDocument,
  chunkDocument,
  extractDocument,
  type DocumentItem,
} from "@/lib/documents-api";
import { UploadDropzone } from "@/components/documents/upload-dropzone";
import { DocumentList } from "@/components/documents/document-list";

const POLL_INTERVAL_MS = 3000;

export function DocumentsSection({ onDocumentsChanged }: { onDocumentsChanged?: () => void } = {}) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listDocuments()
      .then((docs) => {
        if (!cancelled) setDocuments(docs);
      })
      .catch(() => {
        if (!cancelled) setLoadError("Couldn't load your documents. Try refreshing.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // While anything is PROCESSING, poll for status updates — there's no
  // push notification from the background task, so this is how the UI
  // finds out when it flips to PROCESSED/FAILED.
  useEffect(() => {
    const hasProcessing = documents.some((d) => d.status === "PROCESSING");
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      listDocuments()
        .then(setDocuments)
        .catch(() => {
          // Transient poll failure — next tick retries, no need to surface it.
        });
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [documents]);

  function handleUploaded(doc: DocumentItem) {
    setDocuments((prev) => [doc, ...prev]);
    onDocumentsChanged?.();
  }

  async function handleRename(id: string, title: string) {
    const updated = await renameDocument(id, title);
    setDocuments((prev) => prev.map((d) => (d.id === id ? updated : d)));
  }

  async function handleDelete(id: string) {
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    onDocumentsChanged?.();
  }

  async function handleProcess(id: string) {
    const { status } = await processDocument(id);
    setDocuments((prev) => prev.map((d) => (d.id === id ? { ...d, status, processing_error: null } : d)));
    onDocumentsChanged?.();
  }

  async function handleChunk(id: string) {
    await chunkDocument(id);
    onDocumentsChanged?.();
  }

  async function handleExtract(id: string) {
    const result = await extractDocument(id);
    onDocumentsChanged?.();
    return result;
  }

  return (
    <section className="mt-10">
      <h2 className="font-display text-xl font-semibold text-foreground">Documents</h2>

      <div className="mt-4">
        <UploadDropzone onUploaded={handleUploaded} />
      </div>

      {loadError && (
        <p className="mt-4 text-sm text-red-600" role="alert">
          {loadError}
        </p>
      )}

      {!loading && documents.length === 0 && !loadError && (
        <div className="mt-6 rounded-2xl border border-dashed border-border bg-surface px-8 py-14 text-center">
          <p className="text-muted">
            Your Career Brain is empty. Upload your first document to begin
            building your digital identity.
          </p>
        </div>
      )}

      {!loading && documents.length > 0 && (
        <DocumentList
          documents={documents}
          onRename={handleRename}
          onDelete={handleDelete}
          onProcess={handleProcess}
          onChunk={handleChunk}
          onExtract={handleExtract}
        />
      )}
    </section>
  );
}
