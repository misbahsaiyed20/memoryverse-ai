import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: number;
  icon?: LucideIcon;
}

export function StatCard({ label, value, icon: Icon }: StatCardProps) {
  return (
    <div className="group rounded-2xl border border-border bg-surface p-6 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-card">
      <div className="flex items-start justify-between">
        <p className="font-display text-3xl font-semibold tabular-nums text-foreground">{value}</p>
        {Icon && (
          <span className="rounded-lg bg-accent-soft p-1.5 text-accent transition-colors group-hover:bg-accent group-hover:text-accent-foreground">
            <Icon size={16} strokeWidth={2.2} />
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-muted">{label}</p>
    </div>
  );
}
