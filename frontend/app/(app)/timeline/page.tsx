"use client";

import { useEffect, useState } from "react";
import { Clock, FileText } from "lucide-react";

import { getTimeline, type TimelineEntry } from "@/lib/career-brain-api";
import { EntityBadge } from "@/components/entity-badge";
import { EvidenceChip } from "@/components/evidence-chip";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function TimelinePage() {
  const [entries, setEntries] = useState<TimelineEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getTimeline()
      .then((data) => {
        if (!cancelled) setEntries(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load timeline.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl font-semibold text-foreground">Timeline</h1>
        <p className="mt-1.5 text-sm text-muted">
          What was extracted from each document, in the order you uploaded them.
        </p>

        <div className="mt-8">
          {error ? (
            <EmptyState icon={Clock} title="Couldn't load timeline" description={error} />
          ) : !entries ? (
            <div className="space-y-6">
              {Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : entries.length === 0 ? (
            <EmptyState
              icon={Clock}
              title="Nothing extracted yet"
              description="Once a document is processed and extracted, it'll show up here."
            />
          ) : (
            <ol className="relative space-y-8 border-l border-border pl-6">
              {entries.map((entry) => (
                <li key={entry.document_id} className="relative">
                  <span className="absolute -left-[29px] top-1 h-3 w-3 rounded-full border-2 border-surface bg-accent" />
                  <p className="flex items-center gap-1.5 text-xs font-medium text-muted">
                    <FileText size={13} />
                    {entry.filename}
                    <span className="text-border">·</span>
                    {new Date(entry.created_at).toLocaleDateString()}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {entry.nodes.map((node) => (
                      <div
                        key={node.id}
                        className="flex items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2"
                      >
                        <EntityBadge type={node.entity_type} />
                        <span className="text-sm text-foreground">{node.name}</span>
                        <EvidenceChip filename={node.filename} quote={node.evidence_quote} />
                      </div>
                    ))}
                  </div>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </main>
  );
}
