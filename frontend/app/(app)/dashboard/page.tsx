"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Sparkles } from "lucide-react";

import { useAuth } from "@/lib/auth-context";
import { apiFetch } from "@/lib/api";
import { getNodes, type EntityType } from "@/lib/career-brain-api";
import { ENTITY_META } from "@/lib/entity-meta";
import { StatCard } from "@/components/stat-card";
import { Skeleton } from "@/components/ui/skeleton";
import { DocumentsSection } from "@/components/documents/documents-section";

interface DashboardStats {
  documents: { total: number; by_status: Record<string, number> };
  knowledge: Record<EntityType, number>;
  recent_documents: { id: string; filename: string; status: string; created_at: string }[];
}

const EMPTY_KNOWLEDGE = Object.fromEntries(Object.keys(ENTITY_META).map((k) => [k, 0])) as Record<
  EntityType,
  number
>;

function topByName(names: string[], limit: number): { name: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const name of names) counts.set(name, (counts.get(name) ?? 0) + 1);
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([name, count]) => ({ name, count }));
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [topSkills, setTopSkills] = useState<{ name: string; count: number }[]>([]);
  const [topTech, setTopTech] = useState<{ name: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);
  // Bumped after any action in DocumentsSection (upload/process/chunk/
  // extract/delete) — DocumentsSection has its own independent state, so
  // without this the stat cards/widgets above it would only ever reflect
  // whatever existed at initial page load.
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;

    Promise.all([
      apiFetch("/api/v1/dashboard/stats").then((res) => {
        if (!res.ok) throw new Error("Stats request failed");
        return res.json() as Promise<DashboardStats>;
      }),
      getNodes({ entityType: "SKILL" }),
      getNodes({ entityType: "TECHNOLOGY" }),
    ])
      .then(([statsData, skills, tech]) => {
        if (cancelled) return;
        setStats(statsData);
        setTopSkills(topByName(skills.map((n) => n.name), 6));
        setTopTech(topByName(tech.map((n) => n.name), 6));
      })
      .catch(() => {
        if (!cancelled) setStats(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user, refreshKey]);

  const knowledge = stats?.knowledge ?? EMPTY_KNOWLEDGE;
  const firstName = user?.displayName?.split(" ")[0] ?? "there";

  return (
    <main className="px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <h1 className="font-display text-3xl font-semibold text-foreground">
          Welcome, {firstName}.
        </h1>
        <p className="mt-1.5 text-sm text-muted">
          Your career, extracted and evidence-linked from every document you&apos;ve uploaded.
        </p>

        <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Documents" value={loading ? 0 : stats?.documents.total ?? 0} />
          <StatCard label="Skills" value={loading ? 0 : knowledge.SKILL} />
          <StatCard label="Projects" value={loading ? 0 : knowledge.PROJECT} />
          <StatCard label="Certifications" value={loading ? 0 : knowledge.CERTIFICATE} />
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <DistributionCard title="Top skills" icon={Sparkles} items={topSkills} loading={loading} emptyHint="Extract a document to see your skills here." />
          <DistributionCard title="Technology distribution" icon={Sparkles} items={topTech} loading={loading} emptyHint="Technologies you've used will show up here." />
        </div>

        <div className="mt-6 rounded-2xl border border-border bg-surface p-6">
          <h2 className="font-display text-base font-semibold text-foreground">Recent documents</h2>
          {loading ? (
            <div className="mt-4 space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : !stats?.recent_documents.length ? (
            <p className="mt-3 text-sm text-muted">No documents uploaded yet.</p>
          ) : (
            <ul className="mt-4 divide-y divide-border">
              {stats.recent_documents.map((doc) => (
                <li key={doc.id} className="flex items-center justify-between py-2.5">
                  <span className="flex items-center gap-2 truncate text-sm text-foreground">
                    <FileText size={15} className="shrink-0 text-muted" />
                    <span className="truncate">{doc.filename}</span>
                  </span>
                  <StatusPill status={doc.status} />
                </li>
              ))}
            </ul>
          )}
        </div>

        <DocumentsSection onDocumentsChanged={() => setRefreshKey((k) => k + 1)} />
      </div>
    </main>
  );
}

function DistributionCard({
  title,
  icon: Icon,
  items,
  loading,
  emptyHint,
}: {
  title: string;
  icon: typeof Sparkles;
  items: { name: string; count: number }[];
  loading: boolean;
  emptyHint: string;
}) {
  const max = Math.max(1, ...items.map((i) => i.count));

  return (
    <div className="rounded-2xl border border-border bg-surface p-6">
      <h2 className="flex items-center gap-2 font-display text-base font-semibold text-foreground">
        <Icon size={16} className="text-accent" />
        {title}
      </h2>
      {loading ? (
        <div className="mt-4 space-y-2.5">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </div>
      ) : items.length === 0 ? (
        <p className="mt-3 text-sm text-muted">{emptyHint}</p>
      ) : (
        <ul className="mt-4 space-y-2.5">
          {items.map((item) => (
            <li key={item.name} className="flex items-center gap-3">
              <span className="w-24 shrink-0 truncate text-sm text-foreground" title={item.name}>
                {item.name}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-background">
                <div
                  className="h-full rounded-full bg-accent"
                  style={{ width: `${(item.count / max) * 100}%` }}
                />
              </div>
              <span className="w-4 shrink-0 text-right text-xs text-muted">{item.count}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const styles: Record<string, string> = {
    PROCESSED: "text-emerald-700 bg-emerald-50",
    PROCESSING: "text-amber-700 bg-amber-50",
    FAILED: "text-rose-700 bg-rose-50",
    UPLOADED: "text-muted bg-background",
    ARCHIVED: "text-muted bg-background",
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status] ?? styles.UPLOADED}`}>
      {status}
    </span>
  );
}
