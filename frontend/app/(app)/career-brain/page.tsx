"use client";

import { useEffect, useState } from "react";
import { Brain } from "lucide-react";

import { getNodes, type EntityType, type KnowledgeNodeItem } from "@/lib/career-brain-api";
import { ENTITY_META, ENTITY_TYPES } from "@/lib/entity-meta";
import { EntityBadge } from "@/components/entity-badge";
import { EvidenceChip } from "@/components/evidence-chip";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export default function CareerBrainPage() {
  const [activeType, setActiveType] = useState<EntityType | "ALL">("ALL");
  const [nodes, setNodes] = useState<KnowledgeNodeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getNodes({ entityType: activeType === "ALL" ? undefined : activeType })
      .then((data) => {
        if (!cancelled) setNodes(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeType]);

  return (
    <main className="px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <h1 className="font-display text-3xl font-semibold text-foreground">Career Brain</h1>
        <p className="mt-1.5 text-sm text-muted">
          Every entity here was independently verified against the document it came from.
        </p>

        <div className="mt-6 flex flex-wrap gap-2">
          <FilterPill active={activeType === "ALL"} onClick={() => setActiveType("ALL")}>
            All
          </FilterPill>
          {ENTITY_TYPES.map((type) => (
            <FilterPill key={type} active={activeType === type} onClick={() => setActiveType(type)}>
              {ENTITY_META[type].label}
            </FilterPill>
          ))}
        </div>

        <div className="mt-6">
          {loading ? (
            <div className="grid gap-3 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-28 w-full" />
              ))}
            </div>
          ) : error ? (
            <EmptyState icon={Brain} title="Couldn't load Career Brain" description={error} />
          ) : nodes.length === 0 ? (
            <EmptyState
              icon={Brain}
              title="Nothing here yet"
              description="Upload and extract a document to start building your Career Brain."
            />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {nodes.map((node) => (
                <div key={node.id} className="rounded-2xl border border-border bg-surface p-5">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-display text-base font-semibold text-foreground">{node.name}</p>
                    <EntityBadge type={node.entity_type} />
                  </div>
                  {node.description && (
                    <p className="mt-2 text-sm text-muted">{node.description}</p>
                  )}
                  <div className="mt-4 flex items-center justify-between">
                    <EvidenceChip filename={node.filename} quote={node.evidence_quote} />
                    {node.confidence !== null && (
                      <span className="text-xs text-muted">
                        {Math.round(node.confidence * 100)}% confidence
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

function FilterPill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
        active
          ? "border-accent bg-accent text-accent-foreground"
          : "border-border bg-surface text-muted hover:border-accent hover:text-accent",
      )}
    >
      {children}
    </button>
  );
}
