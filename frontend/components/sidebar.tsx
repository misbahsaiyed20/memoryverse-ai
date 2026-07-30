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

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-border bg-surface px-4 py-6">
      <span className="px-2 font-display text-sm font-semibold uppercase tracking-[0.2em] text-accent">
        MemoryVerse AI
      </span>

      <nav className="mt-8 flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-accent-soft text-accent"
                  : "text-muted hover:bg-background hover:text-foreground",
              )}
            >
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
  );
}
