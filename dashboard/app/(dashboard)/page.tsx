"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Bot, Key, Activity } from "lucide-react";

export default function OverviewPage() {
  const { data: health } = useQuery({ queryKey: ["health"], queryFn: () => apiFetch<any>("/api/v1/health") });
  const { data: users } = useQuery({ queryKey: ["admin-users"], queryFn: () => apiFetch<any>("/api/v1/admin/users") });
  const { data: licenses } = useQuery({ queryKey: ["admin-licenses"], queryFn: () => apiFetch<any>("/api/v1/admin/licenses") });
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: () => apiFetch<any>("/api/v1/status") });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Overview</h1>
        <p className="text-sm text-muted-foreground">Platform status and summary</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Total Users" value={users?.total ?? "..."} />
        <StatCard icon={Bot} label="Active Bots" value={status?.active_bots ?? "..."} />
        <StatCard icon={Key} label="Licenses" value={licenses?.total ?? "..."} />
        <StatCard icon={Activity} label="Uptime" value={health?.uptime ? Math.round(health.uptime) + "s" : "..."} />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>System Health</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {health?.checks ? Object.entries(health.checks).map(([k, v]: [string, any]) => (
              <div key={k} className="flex items-center justify-between">
                <span className="text-sm capitalize">{k}</span>
                <Badge variant={v ? "success" : "destructive"}>{v ? "OK" : "DOWN"}</Badge>
              </div>
            )) : <p className="text-sm text-muted-foreground">Loading...</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Select a section from the sidebar to manage resources.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value }: { icon: any; label: string; value: string | number }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div className="flex h-10 w-10 items-center justify-center bg-primary/10 text-primary">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-lg font-semibold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}
