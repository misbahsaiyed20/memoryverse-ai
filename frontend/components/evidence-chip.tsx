"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { FileText } from "lucide-react";

import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";

interface EvidenceChipProps {
  filename: string | null;
  quote: string;
}

export function EvidenceChip({ filename, quote }: EvidenceChipProps) {
  if (!filename) return null;

  return (
    <Dialog>
      <DialogPrimitive.Trigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-2.5 py-1 text-xs font-medium text-muted transition-colors hover:border-accent hover:text-accent"
        >
          <FileText size={12} />
          <span className="max-w-[10rem] truncate">{filename}</span>
        </button>
      </DialogPrimitive.Trigger>
      <DialogContent>
        <DialogTitle className="font-display text-base font-semibold text-foreground">
          Evidence
        </DialogTitle>
        <DialogDescription asChild>
          <div className="mt-3 space-y-3">
            <p className="flex items-center gap-1.5 text-xs font-medium text-muted">
              <FileText size={13} />
              {filename}
            </p>
            <blockquote className="rounded-xl border border-border bg-background px-4 py-3 text-sm italic text-foreground">
              &ldquo;{quote}&rdquo;
            </blockquote>
          </div>
        </DialogDescription>
      </DialogContent>
    </Dialog>
  );
}
