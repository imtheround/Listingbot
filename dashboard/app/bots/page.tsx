"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function BotsPage() {
  const qc = useQueryClient();
  const { data: bots, isLoading } = useQuery<any[]>({ queryKey: ["bots"], queryFn: () => apiFetch("/api/v1/bots") });

  const createBot = useMutation({
    mutationFn: () => apiPost<any>("/api/v1/bots", { token: "pending" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bots"] }),
  });

  const deleteBot = useMutation({
    mutationFn: (id: number) => apiDelete("/api/v1/bots/" + id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bots"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Bots</h1>
          <p className="text-sm text-muted-foreground">Manage Discord bot instances</p>
        </div>
        <Button onClick={() => createBot.mutate()} disabled={createBot.isPending}>
          <Plus className="mr-2 h-4 w-4" /> New Bot
        </Button>
      </div>
      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Bot #</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">Loading...</td></tr>
              ) : bots?.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">No bots yet. Create one to get started.</td></tr>
              ) : (
                bots?.map((bot: any) => (
                  <tr key={bot.id} className="border-b last:border-0 hover:bg-secondary/50">
                    <td className="px-4 py-3 text-sm font-mono">{bot.id}</td>
                    <td className="px-4 py-3 text-sm">Bot #{bot.botnumber}</td>
                    <td className="px-4 py-3"><Badge variant={bot.status === "active" ? "success" : "secondary"}>{bot.status}</Badge></td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{formatDate(bot.created_at)}</td>
                    <td className="px-4 py-3">
                      <Button variant="ghost" size="sm" onClick={() => deleteBot.mutate(bot.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
