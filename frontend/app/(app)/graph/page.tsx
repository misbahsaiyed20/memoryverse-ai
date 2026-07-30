"use client";

import { useEffect, useState } from "react";
import { Share2 } from "lucide-react";

import { getGraph, type KnowledgeEdgeItem, type KnowledgeNodeItem } from "@/lib/career-brain-api";
import { KnowledgeGraph } from "@/components/knowledge-graph";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function GraphPage() {
  const [data, setData] = useState<{ nodes: KnowledgeNodeItem[]; edges: KnowledgeEdgeItem[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getGraph()
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load graph.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <h1 className="font-display text-3xl font-semibold text-foreground">Knowledge Graph</h1>
        <p className="mt-1.5 text-sm text-muted">
          Drag to pan, scroll the zoom controls, click a node for its evidence.
        </p>

        <div className="mt-6">
          {error ? (
            <EmptyState icon={Share2} title="Couldn't load graph" description={error} />
          ) : !data ? (
            <Skeleton className="h-[600px] w-full" />
          ) : data.nodes.length === 0 ? (
            <EmptyState
              icon={Share2}
              title="No knowledge graph yet"
              description="Extract a document to see how your skills, projects, and experience connect."
            />
          ) : (
            <KnowledgeGraph nodes={data.nodes} edges={data.edges} />
          )}
        </div>
      </div>
    </main>
  );
}
