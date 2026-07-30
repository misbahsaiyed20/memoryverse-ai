import type { EntityType } from "@/lib/career-brain-api";
import { ENTITY_META } from "@/lib/entity-meta";
import { cn } from "@/lib/utils";

export function EntityBadge({ type, className }: { type: EntityType; className?: string }) {
  const meta = ENTITY_META[type];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
        meta.color,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.label}
    </span>
  );
}
