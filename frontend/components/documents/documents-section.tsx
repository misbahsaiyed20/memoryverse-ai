"use client";

import { useEffect, useState } from "react";

import { listDocuments, renameDocument, deleteDocument, type DocumentItem } from "@/lib/documents-api";
import { UploadDropzone } from "@/components/documents/upload-dropzone";
import { DocumentList } from "@/components/documents/document-list";

export function DocumentsSection() {
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

  function handleUploaded(doc: DocumentItem) {
    setDocuments((prev) => [doc, ...prev]);
  }

  async function handleRename(id: string, title: string) {
    const updated = await renameDocument(id, title);
    setDocuments((prev) => prev.map((d) => (d.id === id ? updated : d)));
  }

  async function handleDelete(id: string) {
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
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
        <DocumentList documents={documents} onRename={handleRename} onDelete={handleDelete} />
      )}
    </section>
  );
}
