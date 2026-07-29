"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PublicStatus {
  status: string;
  uptime: number;
  database: boolean;
  redis: boolean;
}

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function PublicStatusPage() {
  const { data: status, isLoading } = useQuery<PublicStatus>({
    queryKey: ["public-status"],
    queryFn: () => fetch("/api/v1/public/status").then((r) => r.json()),
    refetchInterval: 10000,
  });

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">AutoSecure Status</h1>
          <p className="text-sm text-muted-foreground mt-1">System health overview</p>
        </div>

        {isLoading ? (
          <div className="h-48 animate-pulse bg-muted rounded-lg" />
        ) : (
          <>
            {/* Overall Status */}
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span
                    className={`h-3 w-3 rounded-full ${
                      status?.status === "ok" ? "bg-emerald-400 animate-pulse" : "bg-yellow-400"
                    }`}
                  />
                  <span className="text-lg font-semibold capitalize">{status?.status || "Unknown"}</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Uptime: {status?.uptime ? formatUptime(status.uptime) : "—"}
                </p>
              </CardContent>
            </Card>

            {/* Service Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Services</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Database</span>
                  <Badge variant={status?.database ? "success" : "destructive"}>
                    {status?.database ? "Connected" : "Down"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Redis</span>
                  <Badge variant={status?.redis ? "success" : "destructive"}>
                    {status?.redis ? "Connected" : "Down"}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <p className="text-xs text-muted-foreground text-center">
          AutoSecure v1.0.0 — Auto-refreshes every 10s
        </p>
      </div>
    </div>
  );
}
