"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import type { BotResponse, BotCreateRequest, BotRestartResponse } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Plus, Trash2, Play, Square, RotateCw, Bot as BotIcon } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useState } from "react";
import { EmptyState } from "@/components/empty-state";
import { toast } from "sonner";

export default function BotsPage() {
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const { data: bots, isLoading } = useQuery<BotResponse[]>({
    queryKey: ["bots"],
    queryFn: () => apiFetch<BotResponse[]>("/api/v1/bots"),
  });

  const startBot = useMutation({
    mutationFn: (id: number) => apiPost<BotRestartResponse>(`/api/v1/bots/${id}/start`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const stopBot = useMutation({
    mutationFn: (id: number) => apiPost<BotRestartResponse>(`/api/v1/bots/${id}/stop`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const restartBot = useMutation({
    mutationFn: (id: number) => apiPost<BotRestartResponse>(`/api/v1/bots/${id}/restart`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteBot = useMutation({
    mutationFn: (id: number) => apiDelete(`/api/v1/bots/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success("Bot deleted");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createBot = useMutation({
    mutationFn: (token: string) => apiPost<BotResponse>("/api/v1/bots", { token } satisfies BotCreateRequest),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success("Bot created");
      setShowCreate(false);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Bots</h1>
          <p className="text-sm text-muted-foreground">Manage Discord bot instances</p>
        </div>
        <Button onClick={() => setShowCreate((s) => !s)}>
          <Plus className="mr-2 h-4 w-4" /> New Bot
        </Button>
      </div>

      {showCreate && (
        <CreateBotForm
          onSubmit={(token) => createBot.mutate(token)}
          loading={createBot.isPending}
          onCancel={() => setShowCreate(false)}
        />
      )}

      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Bot #</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">
                    Loading...
                  </td>
                </tr>
              ) : bots?.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState
                      icon={BotIcon}
                      title="No bots yet"
                      description="Create your first bot instance to get started."
                    />
                  </td>
                </tr>
              ) : (
                bots?.map((bot) => (
                  <tr key={bot.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-3 text-sm font-mono">{bot.id}</td>
                    <td className="px-4 py-3 text-sm">
                      <Link href={`/bots/${bot.id}`} className="hover:underline">
                        Bot #{bot.botnumber}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={bot.status === "running" ? "success" : "secondary"}>
                        <span
                          className={`h-1.5 w-1.5 rounded-full mr-1.5 ${
                            bot.status === "running" ? "bg-emerald-400 animate-pulse" : "bg-muted-foreground"
                          }`}
                        />
                        {bot.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {bot.created_at ? formatDate(bot.created_at) : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        {bot.status === "running" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => stopBot.mutate(bot.id)}
                            disabled={stopBot.isPending}
                            title="Stop"
                          >
                            <Square className="h-4 w-4" />
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => startBot.mutate(bot.id)}
                            disabled={startBot.isPending}
                            title="Start"
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => restartBot.mutate(bot.id)}
                          disabled={restartBot.isPending}
                          title="Restart"
                        >
                          <RotateCw className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (confirm(`Delete Bot #${bot.botnumber}? This cannot be undone.`)) {
                              deleteBot.mutate(bot.id);
                            }
                          }}
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
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

function CreateBotForm({
  onSubmit,
  loading,
  onCancel,
}: {
  onSubmit: (token: string) => void;
  loading: boolean;
  onCancel: () => void;
}) {
  const [token, setToken] = useState("");

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">Create New Bot</p>
        <Input
          placeholder="Discord bot token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="font-mono text-xs"
        />
        <p className="text-xs text-muted-foreground">
          Paste your Discord bot token here. You can get this from the{" "}
          <a
            href="https://discord.com/developers/applications"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline"
          >
            Discord Developer Portal
          </a>
          .
        </p>
        <div className="flex gap-2 justify-end">
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={() => onSubmit(token)} disabled={!token.trim() || loading}>
            {loading ? "Creating..." : "Create Bot"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
