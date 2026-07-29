"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useRouter } from "next/navigation";
import { apiFetch, apiPut, apiPost, apiDelete } from "@/lib/api";
import type { BotDetailResponse, BotUpdateRequest, BotRestartResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Play, Square, RotateCw, Trash2, Save, Bot as BotIcon } from "lucide-react";
import Link from "next/link";
import { formatDate } from "@/lib/utils";
import { toast } from "sonner";

export default function BotDetailPage() {
  const params = useParams();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: bot, isLoading } = useQuery<BotDetailResponse>({
    queryKey: ["bot", params.id],
    queryFn: () => apiFetch<BotDetailResponse>(`/api/v1/bots/${params.id}`),
  });

  const [domain, setDomain] = useState("");
  const [dmmode, setDmmode] = useState(false);
  const [activityJson, setActivityJson] = useState("");
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (bot) {
      setDomain(bot.domain);
      setDmmode(bot.dmmode);
      setActivityJson(bot.activity ? JSON.stringify(bot.activity, null, 2) : "");
    }
  }, [bot]);

  const updateBot = useMutation({
    mutationFn: (body: BotUpdateRequest) => apiPut<BotDetailResponse>(`/api/v1/bots/${params.id}`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bot", params.id] });
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success("Configuration saved");
      setEditing(false);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const startBot = useMutation({
    mutationFn: () => apiPost<BotRestartResponse>(`/api/v1/bots/${params.id}/start`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bot", params.id] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const stopBot = useMutation({
    mutationFn: () => apiPost<BotRestartResponse>(`/api/v1/bots/${params.id}/stop`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bot", params.id] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const restartBot = useMutation({
    mutationFn: () => apiPost<BotRestartResponse>(`/api/v1/bots/${params.id}/restart`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["bot", params.id] });
      toast.success(data.message);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteBot = useMutation({
    mutationFn: () => apiDelete(`/api/v1/bots/${params.id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bots"] });
      toast.success("Bot deleted");
      router.push("/bots");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function handleSave() {
    const body: BotUpdateRequest = {};
    if (domain !== bot?.domain) body.domain = domain;
    if (dmmode !== bot?.dmmode) body.dmmode = dmmode;
    if (activityJson.trim()) {
      try {
        body.activity = JSON.parse(activityJson);
      } catch {
        toast.error("Activity JSON is invalid");
        return;
      }
    }
    updateBot.mutate(body);
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse bg-muted" />
        <div className="h-64 animate-pulse bg-muted" />
      </div>
    );
  }

  if (!bot) {
    return (
      <div className="space-y-4">
        <Link href="/bots">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Bots
          </Button>
        </Link>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <BotIcon className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-sm font-medium">Bot not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/bots">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h2 className="text-lg font-semibold">Bot #{bot.botnumber}</h2>
          <p className="text-sm text-muted-foreground font-mono">ID: {bot.id}</p>
        </div>
        <Badge variant={bot.status === "running" ? "success" : "secondary"}>
          <span
            className={`h-1.5 w-1.5 rounded-full mr-1.5 ${
              bot.status === "running" ? "bg-emerald-400 animate-pulse" : "bg-muted-foreground"
            }`}
          />
          {bot.status}
        </Badge>
      </div>

      {/* Action bar */}
      <div className="flex gap-2">
        {bot.status === "running" ? (
          <Button variant="outline" size="sm" onClick={() => stopBot.mutate()} disabled={stopBot.isPending}>
            <Square className="mr-2 h-4 w-4" /> Stop
          </Button>
        ) : (
          <Button variant="outline" size="sm" onClick={() => startBot.mutate()} disabled={startBot.isPending}>
            <Play className="mr-2 h-4 w-4" /> Start
          </Button>
        )}
        <Button variant="outline" size="sm" onClick={() => restartBot.mutate()} disabled={restartBot.isPending}>
          <RotateCw className="mr-2 h-4 w-4" /> Restart
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="text-destructive"
          onClick={() => {
            if (confirm(`Delete Bot #${bot.botnumber}? This cannot be undone.`)) {
              deleteBot.mutate();
            }
          }}
        >
          <Trash2 className="mr-2 h-4 w-4" /> Delete
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Details card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Bot #</span>
              <span>{bot.botnumber}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Owner</span>
              <span className="font-mono text-xs">{bot.user_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge variant={bot.status === "running" ? "success" : "secondary"}>{bot.status}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Verified</span>
              <Badge variant={bot.verified ? "success" : "secondary"}>{bot.verified ? "Yes" : "No"}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">DM Mode</span>
              <Badge variant={bot.dmmode ? "success" : "secondary"}>{bot.dmmode ? "On" : "Off"}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{bot.created_at ? formatDate(bot.created_at) : "—"}</span>
            </div>
          </CardContent>
        </Card>

        {/* Config editor */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Configuration</CardTitle>
              {editing ? (
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => setEditing(false)}>
                    Cancel
                  </Button>
                  <Button size="sm" onClick={handleSave} disabled={updateBot.isPending}>
                    <Save className="mr-1 h-3 w-3" /> Save
                  </Button>
                </div>
              ) : (
                <Button variant="ghost" size="sm" onClick={() => setEditing(true)}>
                  Edit
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Domain</label>
              {editing ? (
                <Input value={domain} onChange={(e) => setDomain(e.target.value)} className="text-sm" />
              ) : (
                <p className="text-sm font-medium">{bot.domain}</p>
              )}
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">DM Mode</label>
              {editing ? (
                <button
                  onClick={() => setDmmode(!dmmode)}
                  className={`px-3 py-1.5 text-xs border border-border ${
                    dmmode ? "bg-primary text-primary-foreground" : "bg-transparent text-muted-foreground"
                  }`}
                >
                  {dmmode ? "ON" : "OFF"}
                </button>
              ) : (
                <p className="text-sm font-medium">{bot.dmmode ? "On" : "Off"}</p>
              )}
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Activity (JSON)</label>
              {editing ? (
                <textarea
                  value={activityJson}
                  onChange={(e) => setActivityJson(e.target.value)}
                  className="w-full border border-border bg-input p-2 text-xs font-mono h-24 resize-none"
                  placeholder='{"type": "PLAYING", "name": "with security"}'
                />
              ) : (
                <p className="text-xs font-mono text-muted-foreground">
                  {bot.activity ? JSON.stringify(bot.activity, null, 2) : "—"}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
