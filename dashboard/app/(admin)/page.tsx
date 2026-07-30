"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { DashboardStats } from "@/lib/types";
import { StatsCard, StatsCardSkeleton, StatsGrid } from "@/components/stats-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Bot, Key, Activity, Database, Server, Link2, FileText } from "lucide-react";

export default function OverviewPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => apiFetch<DashboardStats>("/api/v1/dashboard/stats"),
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
        <p className="text-sm text-muted-foreground">Platform status and summary</p>
      </div>

      <StatsGrid>
        {isLoading || !stats ? (
          Array.from({ length: 8 }).map((_, i) => <StatsCardSkeleton key={i} />)
        ) : (
          <>
            <StatsCard icon={Users} label="Total Users" value={stats.total_users} />
            <StatsCard icon={Database} label="Total Accounts" value={stats.total_accounts} />
            <StatsCard icon={Bot} label="Total Bots" value={stats.total_bots} hint={`${stats.active_bots} active`} />
            <StatsCard icon={Key} label="Licenses" value={stats.total_licenses} hint={`${stats.active_licenses} active`} />
            <StatsCard icon={Activity} label="Uptime" value={formatUptime(stats.uptime_seconds)} />
            <StatsCard icon={Server} label="API Status" value={stats.health.database ? "Online" : "Degraded"} />
            <StatsCard icon={Link2} label="Redis" value={stats.health.redis ? "Online" : "Offline"} />
            <StatsCard icon={FileText} label="Recent Events" value={stats.recent_activity.length} />
          </>
        )}
      </StatsGrid>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {stats?.health
              ? Object.entries(stats.health).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{k}</span>
                    <Badge variant={v ? "success" : "destructive"}>{v ? "OK" : "DOWN"}</Badge>
                  </div>
                ))
              : Array.from({ length: 2 }).map((_, i) => (
                  <div key={i} className="h-5 animate-pulse bg-muted" />
                ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Link href="/accounts"><Button variant="outline" size="sm">View Accounts</Button></Link>
            <Link href="/bots"><Button variant="outline" size="sm">Manage Bots</Button></Link>
            <Link href="/licenses"><Button variant="outline" size="sm">Licenses</Button></Link>
            <Link href="/emails"><Button variant="outline" size="sm">Emails</Button></Link>
            <Link href="/settings"><Button variant="outline" size="sm">Settings</Button></Link>
          </CardContent>
        </Card>
      </div>

      {stats && stats.recent_activity.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.recent_activity.map((evt, i) => (
                <div key={i} className="flex items-center justify-between border-b border-border py-2 last:border-0">
                  <span className="text-sm font-mono">{evt.action}</span>
                  <span className="text-xs text-muted-foreground">
                    {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : "—"}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
