import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatsCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  hint?: string;
}

export function StatsCard({ icon: Icon, label, value, hint }: StatsCardProps) {
  return (
    <div className="border border-border bg-card p-4">
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center bg-primary/10 text-primary">
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground truncate">{label}</p>
          <p className="text-lg font-semibold">{value}</p>
          {hint && <p className="text-[10px] text-muted-foreground mt-0.5">{hint}</p>}
        </div>
      </div>
    </div>
  );
}

export function StatsCardSkeleton() {
  return <div className="h-[68px] animate-pulse bg-muted" />;
}

export function StatsGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4", className)}>{children}</div>;
}
