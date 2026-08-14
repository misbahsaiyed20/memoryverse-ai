"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Menu } from "lucide-react";

import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-sm text-muted">Loading…</p>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

      <div className="flex min-h-screen flex-1 flex-col overflow-y-auto">
        {/* Mobile-only top bar — sidebar is off-canvas below md */}
        <div className="flex items-center gap-3 border-b border-border bg-surface px-4 py-3 md:hidden">
          <button
            onClick={() => setMobileNavOpen(true)}
            className="text-foreground"
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
          <span className="font-display text-sm font-semibold uppercase tracking-[0.16em] text-foreground">
            MemoryVerse
          </span>
        </div>

        {children}
      </div>
    </div>
  );
}
