"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/empty-state";
import { Link2, Plus, Trash2 } from "lucide-react";

const WEBHOOK_EVENTS = ["account_created", "bot_started", "bot_stopped", "license_activated", "email_received"];

export default function WebhooksPage() {
  const qc = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [url, setUrl] = useState("");
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  const { data: webhooks, isLoading } = useQuery<Array<Record<string, unknown>>>({
    queryKey: ["my-webhooks"],
    queryFn: () => apiFetch("/api/v1/webhooks"),
  });

  const create = useMutation({
    mutationFn: () => apiPost("/api/v1/webhooks", { url, events: selectedEvents }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["my-webhooks"] }); setShowAdd(false); setUrl(""); setSelectedEvents([]); },
  });

  const remove = useMutation({
    mutationFn: (id: number) => apiDelete(`/api/v1/webhooks/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-webhooks"] }),
  });

  const toggleEvent = (e: string) => {
    setSelectedEvents(prev => prev.includes(e) ? prev.filter(x => x !== e) : [...prev, e]);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Webhooks</h1>
          <p className="text-sm text-muted-foreground">Configure webhook endpoints</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)} size="sm"><Plus className="h-4 w-4 mr-1" /> Add Webhook</Button>
      </div>

      {showAdd && (
        <Card className="p-4 space-y-3">
          <Input placeholder="Webhook URL" value={url} onChange={(e) => setUrl(e.target.value)} />
          <div className="flex flex-wrap gap-2">
            {WEBHOOK_EVENTS.map((evt) => (
              <Badge key={evt} variant={selectedEvents.includes(evt) ? "default" : "outline"} className="cursor-pointer" onClick={() => toggleEvent(evt)}>
                {evt}
              </Badge>
            ))}
          </div>
          <Button onClick={() => create.mutate()} disabled={!url || selectedEvents.length === 0} size="sm">Save</Button>
        </Card>
      )}

      {isLoading ? (
        <div className="space-y-2">{[1, 2].map(i => <div key={i} className="h-12 animate-pulse bg-muted rounded-lg" />)}</div>
      ) : webhooks?.length ? (
        <div className="space-y-2">
          {webhooks.map((w) => (
            <div key={w.id as number} className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="text-sm font-medium truncate max-w-md">{w.url as string}</p>
                <div className="flex gap-1 mt-1">
                  {(w.events as string[]).map((e) => <Badge key={e} variant="outline" className="text-[10px]">{e}</Badge>)}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={w.active ? "success" : "secondary"}>{(w.active as boolean) ? "Active" : "Inactive"}</Badge>
                <Button variant="ghost" size="icon" onClick={() => remove.mutate(w.id as number)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState icon={Link2} title="No webhooks" description="Add your first webhook endpoint." />
      )}
    </div>
  );
}
