"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Brain,
  Share2,
  Search,
  MessageCircle,
  Clock,
  Sparkles,
  LogOut,
  X,
} from "lucide-react";

import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/career-brain", label: "Career Brain", icon: Brain },
  { href: "/insights", label: "Career Intelligence", icon: Sparkles },
  { href: "/graph", label: "Knowledge Graph", icon: Share2 },
  { href: "/search", label: "Search", icon: Search },
  { href: "/chat", label: "Verse AI", icon: MessageCircle },
  { href: "/timeline", label: "Timeline", icon: Clock },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ mobileOpen = false, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <>
      {/* Mobile-only backdrop, shown behind the drawer while open */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex h-screen w-60 shrink-0 flex-col border-r border-border bg-surface px-4 py-6 transition-transform duration-200 md:static md:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
              <Brain size={15} strokeWidth={2.4} />
            </span>
            <span className="font-display text-sm font-semibold uppercase tracking-[0.16em] text-foreground">
              MemoryVerse
            </span>
          </div>
          <button onClick={onClose} className="text-muted md:hidden" aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <nav className="mt-8 flex flex-1 flex-col gap-0.5">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  active
                    ? "bg-accent-soft text-accent"
                    : "text-muted hover:bg-background hover:text-foreground",
                )}
              >
                {active && (
                  <span className="absolute -left-4 top-1/2 h-5 w-1 -translate-y-1/2 rounded-full bg-accent" />
                )}
                <Icon size={17} strokeWidth={active ? 2.4 : 2} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border pt-4">
          <p className="truncate px-2 text-xs font-medium text-muted">{user?.email}</p>
          <button
            onClick={handleLogout}
            className="mt-2 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:bg-background hover:text-foreground"
          >
            <LogOut size={17} />
            Log out
          </button>
        </div>
      </aside>
    </>
  );
}
