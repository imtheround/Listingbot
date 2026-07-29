"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import type { WebhookListResponse, WebhookResponse, WebhookCreateRequest } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2, Webhook } from "lucide-react";
import { toast } from "sonner";
import { EmptyState } from "@/components/empty-state";

const AVAILABLE_EVENTS = [
  "account.created",
  "account.deleted",
  "bot.created",
  "bot.deleted",
  "bot.started",
  "bot.stopped",
  "license.redeemed",
  "license.generated",
  "email.received",
];

export default function WebhooksPage() {
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading } = useQuery<WebhookListResponse>({
    queryKey: ["webhooks"],
    queryFn: () => apiFetch<WebhookListResponse>("/api/v1/webhooks"),
  });

  const deleteWebhook = useMutation({
    mutationFn: (id: number) => apiDelete(`/api/v1/webhooks/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["webhooks"] });
      toast.success("Webhook removed");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createWebhook = useMutation({
    mutationFn: (body: WebhookCreateRequest) => apiPost<WebhookResponse>("/api/v1/webhooks", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["webhooks"] });
      toast.success("Webhook created");
      setShowCreate(false);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Webhooks</h1>
          <p className="text-sm text-muted-foreground">Manage webhook subscriptions</p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="mr-2 h-4 w-4" /> New Webhook
        </Button>
      </div>

      {showCreate && (
        <CreateWebhookForm
          onSubmit={(body) => createWebhook.mutate(body)}
          loading={createWebhook.isPending}
          onCancel={() => setShowCreate(false)}
        />
      )}

      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">URL</th>
                <th className="px-4 py-3 font-medium">Events</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">
                    Loading...
                  </td>
                </tr>
              ) : data?.webhooks?.length === 0 ? (
                <tr>
                  <td colSpan={4}>
                    <EmptyState
                      icon={Webhook}
                      title="No webhooks"
                      description="Create a webhook to receive event notifications."
                    />
                  </td>
                </tr>
              ) : (
                data?.webhooks?.map((wh) => (
                  <tr key={wh.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-3 text-sm font-mono max-w-[300px] truncate">{wh.url}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {wh.events?.slice(0, 3).map((ev) => (
                          <Badge key={ev} variant="outline" className="text-xs">
                            {ev}
                          </Badge>
                        ))}
                        {wh.events && wh.events.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{wh.events.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={wh.active ? "success" : "secondary"}>
                        {wh.active ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (confirm("Delete this webhook?")) {
                            deleteWebhook.mutate(wh.id);
                          }
                        }}
                      >
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

function CreateWebhookForm({
  onSubmit,
  loading,
  onCancel,
}: {
  onSubmit: (body: WebhookCreateRequest) => void;
  loading: boolean;
  onCancel: () => void;
}) {
  const [url, setUrl] = useState("");
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  function toggleEvent(event: string) {
    setSelectedEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event]
    );
  }

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">Create Webhook</p>
        <Input
          placeholder="https://example.com/webhook"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="text-sm"
        />
        <div>
          <p className="text-xs text-muted-foreground mb-2">Events to subscribe to:</p>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_EVENTS.map((ev) => (
              <button
                key={ev}
                onClick={() => toggleEvent(ev)}
                className={`px-2 py-1 text-xs border border-border ${
                  selectedEvents.includes(ev)
                    ? "bg-primary text-primary-foreground"
                    : "bg-transparent text-muted-foreground"
                }`}
              >
                {ev}
              </button>
            ))}
          </div>
        </div>
        <div className="flex gap-2 justify-end">
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            onClick={() => onSubmit({ url, events: selectedEvents })}
            disabled={!url.trim() || loading}
          >
            {loading ? "Creating..." : "Create Webhook"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
