"use client";

import { useState } from "react";
import { Search as SearchIcon, FileText } from "lucide-react";

import { searchDocuments, type SearchResultItem } from "@/lib/search-api";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

function relevancePercent(distance: number | null): number | null {
  if (distance === null) return null;
  // Chroma's default distance is unbounded L2 (lower = more similar), not
  // a 0-1 score — see SearchService's own comment on why it isn't
  // normalized. This clamps it into a rough visual indicator only, not a
  // precise probability.
  return Math.max(0, Math.round((1 - Math.min(distance, 1)) * 100));
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResultItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(q: string) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await searchDocuments(q, 8);
      setResults(data);
      setHistory((prev) => [q, ...prev.filter((h) => h !== q)].slice(0, 6));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl font-semibold text-foreground">Search</h1>
        <p className="mt-1.5 text-sm text-muted">
          Semantic search across every document you&apos;ve uploaded.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            runSearch(query);
          }}
          className="mt-6 flex items-center gap-2 rounded-2xl border border-border bg-surface px-4 py-3 focus-within:border-accent"
        >
          <SearchIcon size={18} className="text-muted" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your career history…"
            className="flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted"
          />
        </form>

        {history.length > 0 && !results && (
          <div className="mt-3 flex flex-wrap gap-2">
            {history.map((h) => (
              <button
                key={h}
                onClick={() => {
                  setQuery(h);
                  runSearch(h);
                }}
                className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted hover:border-accent hover:text-accent"
              >
                {h}
              </button>
            ))}
          </div>
        )}

        <div className="mt-6">
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          ) : error ? (
            <EmptyState icon={SearchIcon} title="Search failed" description={error} />
          ) : !results ? (
            <EmptyState
              icon={SearchIcon}
              title="Search your documents"
              description="Ask about a skill, project, or company — results are ranked by relevance."
            />
          ) : results.length === 0 ? (
            <EmptyState
              icon={SearchIcon}
              title="No matches"
              description="Try a different phrase, or upload more documents."
            />
          ) : (
            <ul className="space-y-3">
              {results.map((result) => {
                const relevance = relevancePercent(result.distance);
                return (
                  <li key={result.chunk_id} className="rounded-2xl border border-border bg-surface p-5">
                    <div className="flex items-center justify-between gap-3">
                      <span className="flex min-w-0 items-center gap-1.5 text-xs font-medium text-muted">
                        <FileText size={13} className="shrink-0" />
                        <span className="truncate">{result.filename ?? "Unknown document"}</span>
                      </span>
                      {relevance !== null && (
                        <span className="shrink-0 rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent">
                          {relevance}% match
                        </span>
                      )}
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-foreground">
                      <HighlightedText text={result.chunk_text ?? ""} query={query} />
                    </p>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </main>
  );
}

function HighlightedText({ text, query }: { text: string; query: string }) {
  const terms = query.trim().split(/\s+/).filter((t) => t.length > 2);
  if (terms.length === 0) return <>{text}</>;

  const pattern = new RegExp(`(${terms.map(escapeRegExp).join("|")})`, "gi");
  const parts = text.split(pattern);

  return (
    <>
      {parts.map((part, i) =>
        terms.some((t) => t.toLowerCase() === part.toLowerCase()) ? (
          <mark key={i} className="rounded bg-accent-soft px-0.5 text-accent">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
