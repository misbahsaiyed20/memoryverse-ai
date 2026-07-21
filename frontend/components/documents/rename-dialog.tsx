"use client";

import { useState } from "react";

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import type { DocumentItem } from "@/lib/documents-api";

interface RenameDialogProps {
  document: DocumentItem;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onRename: (id: string, title: string) => Promise<void>;
}

export function RenameDialog({ document, open, onOpenChange, onRename }: RenameDialogProps) {
  const [title, setTitle] = useState(document.title);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    const trimmed = title.trim();
    if (!trimmed) {
      setError("Title can't be empty.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onRename(document.id, trimmed);
      onOpenChange(false);
    } catch {
      setError("Couldn't rename the document. Try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle className="font-display text-lg font-semibold text-foreground">
          Rename document
        </DialogTitle>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSave()}
          className="mt-4 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent"
          autoFocus
        />
        {error && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={() => onOpenChange(false)}
            className="rounded-full px-4 py-2 text-sm font-medium text-muted transition-colors hover:text-foreground"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90 disabled:opacity-60"
          >
            {saving ? "Saving…" : "Save"}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
