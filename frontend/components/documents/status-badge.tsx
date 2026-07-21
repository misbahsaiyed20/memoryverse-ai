import type { DocumentItem } from "@/lib/documents-api";

const STATUS_STYLES: Record<DocumentItem["status"], string> = {
  UPLOADED: "bg-accent-soft text-accent",
  PROCESSING: "bg-yellow-100 text-yellow-700",
  PROCESSED: "bg-green-100 text-green-700",
  FAILED: "bg-red-100 text-red-700",
  ARCHIVED: "bg-neutral-100 text-neutral-500",
};

export function StatusBadge({ status }: { status: DocumentItem["status"] }) {
  return (
    <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[status]}`}>
      {status}
    </span>
  );
}
