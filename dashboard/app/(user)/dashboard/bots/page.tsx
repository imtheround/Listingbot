"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/empty-state";
import { Bot, Plus, Trash2, Play, Square, RefreshCw } from "lucide-react";

export default function BotsPage() {
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [token, setToken] = useState("");

  const { data: bots, isLoading } = useQuery<Array<Record<string, unknown>>>({
    queryKey: ["my-bots"],
    queryFn: () => apiFetch("/api/v1/bots"),
  });

  const createBot = useMutation({
    mutationFn: () => apiPost("/api/v1/bots", { token }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["my-bots"] }); setShowCreate(false); setToken(""); },
  });

  const deleteBot = useMutation({
    mutationFn: (id: number) => apiDelete(`/api/v1/bots/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-bots"] }),
  });

  const actionBot = (id: number, action: string) => {
    apiPost(`/api/v1/bots/${id}/${action}`).then(() => qc.invalidateQueries({ queryKey: ["my-bots"] }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">My Bots</h1>
          <p className="text-sm text-muted-foreground">Your bot instances</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)} size="sm"><Plus className="h-4 w-4 mr-1" /> Create Bot</Button>
      </div>

      {showCreate && (
        <Card className="p-4 space-y-3">
          <Input placeholder="Discord Bot Token" value={token} onChange={(e) => setToken(e.target.value)} />
          <Button onClick={() => createBot.mutate()} disabled={!token} size="sm">Create</Button>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-2">{[1, 2].map(i => <div key={i} className="h-16 animate-pulse bg-muted rounded-lg" />)}</div>
      ) : bots?.length ? (
        <div className="space-y-2">
          {bots.map((b) => (
            <div key={b.id as number} className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="text-sm font-medium">Bot #{b.botnumber as number}</p>
                <p className="text-xs text-muted-foreground">ID: {b.id as number}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={b.status === "running" ? "success" : "secondary"}>{b.status as string}</Badge>
                <Button variant="ghost" size="icon" onClick={() => actionBot(b.id as number, "start")}><Play className="h-4 w-4" /></Button>
                <Button variant="ghost" size="icon" onClick={() => actionBot(b.id as number, "stop")}><Square className="h-4 w-4" /></Button>
                <Button variant="ghost" size="icon" onClick={() => actionBot(b.id as number, "restart")}><RefreshCw className="h-4 w-4" /></Button>
                <Button variant="ghost" size="icon" onClick={() => deleteBot.mutate(b.id as number)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState icon={Bot} title="No bots yet" description="Create your first bot instance." />
      )}
    </div>
  );
}
