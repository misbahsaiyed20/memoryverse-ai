"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";
import { apiFetch } from "@/lib/api";
import { StatCard } from "@/components/stat-card";

interface DashboardStats {
  documents: number;
  skills: number;
  projects: number;
  certificates: number;
}

const EMPTY_STATS: DashboardStats = {
  documents: 0,
  skills: 0,
  projects: 0,
  certificates: 0,
};

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>(EMPTY_STATS);
  const [statsLoading, setStatsLoading] = useState(true);

  // Redirect unauthenticated users to login.
  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (!user) return;

    let cancelled = false;
    apiFetch("/api/v1/dashboard/stats")
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch(() => {
        // Stats failing to load isn't critical here — the dashboard still
        // renders with zeros, which is an honest state anyway this sprint.
      })
      .finally(() => {
        if (!cancelled) setStatsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user]);

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  if (loading || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-muted">Loading…</p>
      </main>
    );
  }

  const firstName = user.displayName?.split(" ")[0] ?? "there";

  return (
    <main className="min-h-screen px-6 py-10 sm:px-10">
      <div className="mx-auto max-w-4xl">
        <header className="flex items-center justify-between">
          <span className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-accent">
            MemoryVerse AI
          </span>
          <button
            onClick={handleLogout}
            className="text-sm font-medium text-muted transition-colors hover:text-foreground"
          >
            Log out
          </button>
        </header>

        <h1 className="mt-10 font-display text-3xl font-semibold text-foreground">
          Welcome, {firstName}.
        </h1>

        <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Documents" value={statsLoading ? 0 : stats.documents} />
          <StatCard label="Skills" value={statsLoading ? 0 : stats.skills} />
          <StatCard label="Projects" value={statsLoading ? 0 : stats.projects} />
          <StatCard label="Certificates" value={statsLoading ? 0 : stats.certificates} />
        </div>

        <div className="mt-10 rounded-2xl border border-dashed border-border bg-surface px-8 py-14 text-center">
          <p className="text-muted">
            Your Career Brain is empty. Upload your first document to begin
            building your digital identity.
          </p>
        </div>
      </div>
    </main>
  );
}
