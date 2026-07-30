"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { StatsCard, StatsCardSkeleton, StatsGrid } from "@/components/stats-card";
import { Bot, Database, Key, Activity, Link2, CreditCard } from "lucide-react";

export default function UserOverviewPage() {
  const { data: stats, isLoading } = useQuery<{ my_accounts: number; my_bots: number; my_active_bots: number; has_license: boolean; license_expiry: string | null; uptime_seconds: number; health?: Record<string, boolean> }>({
    queryKey: ["user-stats"],
    queryFn: () => apiFetch("/api/v1/dashboard/user-stats"),
  });

  function formatUptime(seconds: number): string {
    if (!seconds) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m`;
    return `${Math.round(seconds)}s`;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Overview</h1>
        <p className="text-sm text-muted-foreground">Your platform summary</p>
      </div>

      <StatsGrid>
        {isLoading || !stats ? (
          Array.from({ length: 6 }).map((_, i) => <StatsCardSkeleton key={i} />)
        ) : (
          <>
            <StatsCard icon={Database} label="My Accounts" value={stats.my_accounts} />
            <StatsCard icon={Bot} label="My Bots" value={stats.my_bots} hint={`${stats.my_active_bots} active`} />
            <StatsCard icon={Key} label="License" value={stats.has_license ? "Active" : "Inactive"} />
            <StatsCard icon={Activity} label="Uptime" value={formatUptime(stats.uptime_seconds)} />
            <StatsCard icon={CreditCard} label="Billing" value={stats.has_license ? "Premium" : "Free"} />
            <StatsCard icon={Link2} label="Webhooks" value={0} />
          </>
        )}
      </StatsGrid>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-sm font-medium">Quick Actions</h3>
          <div className="grid gap-2 sm:grid-cols-2">
            <Link href="/dashboard/accounts" className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary transition-colors">
              <Database className="h-5 w-5" /> <span>View Accounts</span>
            </Link>
            <Link href="/dashboard/bots" className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary transition-colors">
              <Bot className="h-5 w-5" /> <span>Manage Bots</span>
            </Link>
            <Link href="/dashboard/license" className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary transition-colors">
              <Key className="h-5 w-5" /> <span>License</span>
            </Link>
            <Link href="/dashboard/billing" className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-secondary transition-colors">
              <CreditCard className="h-5 w-5" /> <span>Upgrade</span>
            </Link>
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-medium">System Status</h3>
          <div className="space-y-2">
            {stats?.health && Object.entries(stats.health).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between">
                <span className="text-sm capitalize">{k}</span>
                <span className={`text-xs font-medium ${v ? "text-green-500" : "text-red-500"}`}>
                  {v ? "Online" : "Offline"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}