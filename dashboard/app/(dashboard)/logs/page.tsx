"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { AuditLogListResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";

const ACTION_OPTIONS = [
  "user.login",
  "user.logout",
  "account.created",
  "account.deleted",
  "bot.created",
  "bot.deleted",
  "bot.started",
  "bot.stopped",
  "license.redeemed",
  "license.generated",
  "license.transferred",
];

export default function LogsPage() {
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("");
  const [actorFilter, setActorFilter] = useState("");
  const [successFilter, setSuccessFilter] = useState<boolean | null>(null);

  const params = new URLSearchParams({ page: String(page), per_page: "50" });
  if (actionFilter) params.set("action", actionFilter);
  if (actorFilter) params.set("actor_id", actorFilter);
  if (successFilter !== null) params.set("success", String(successFilter));

  const { data, isLoading } = useQuery<AuditLogListResponse>({
    queryKey: ["logs", page, actionFilter, actorFilter, successFilter],
    queryFn: () => apiFetch<AuditLogListResponse>(`/api/v1/admin/logs?${params.toString()}`),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Activity Logs</h1>
        <p className="text-sm text-muted-foreground">System audit log</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3">
            <select
              value={actionFilter}
              onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
              className="h-9 border border-border bg-transparent px-3 text-sm"
            >
              <option value="">All actions</option>
              {ACTION_OPTIONS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>

            <Input
              placeholder="Actor ID"
              value={actorFilter}
              onChange={(e) => { setActorFilter(e.target.value); setPage(1); }}
              className="w-48"
            />

            <select
              value={successFilter === null ? "" : String(successFilter)}
              onChange={(e) => {
                const v = e.target.value;
                setSuccessFilter(v === "" ? null : v === "true");
                setPage(1);
              }}
              className="h-9 border border-border bg-transparent px-3 text-sm"
            >
              <option value="">All status</option>
              <option value="true">Success</option>
              <option value="false">Failed</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Log table */}
      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">Actor</th>
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium">Target</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Details</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                    Loading...
                  </td>
                </tr>
              ) : data?.logs?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                    No logs found
                  </td>
                </tr>
              ) : (
                data?.logs?.map((log) => (
                  <tr key={log.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                      {formatDate(log.timestamp)}
                    </td>
                    <td className="px-4 py-3 text-sm font-mono">{log.actor_id}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline" className="text-xs">{log.action}</Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {log.target_type && log.target_id
                        ? `${log.target_type}:${log.target_id}`
                        : log.target_type || "—"}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={log.success ? "success" : "destructive"}>
                        {log.success ? "OK" : "FAIL"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-[200px] truncate">
                      {log.details ? JSON.stringify(log.details) : "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data.page} of {data.pages} ({data.total} logs)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
              disabled={page >= data.pages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
