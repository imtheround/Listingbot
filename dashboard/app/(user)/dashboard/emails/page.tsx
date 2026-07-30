"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/empty-state";
import { Mail, Plus, Trash2, Eye } from "lucide-react";

export default function EmailsPage() {
  const qc = useQueryClient();
  const [email, setEmail] = useState("");
  const [selectedInbox, setSelectedInbox] = useState("");

  const { data: watched } = useQuery<{ addresses?: Array<{ email: string }> }>({
    queryKey: ["my-watched-emails"],
    queryFn: () => apiFetch("/api/v1/emails/watched/list"),
  });

  const { data: inbox } = useQuery<{ emails?: Array<Record<string, unknown>> }>({
    queryKey: ["inbox", selectedInbox],
    queryFn: () => selectedInbox ? apiFetch(`/api/v1/emails/${selectedInbox}`) : Promise.resolve({ emails: [] }),
    enabled: !!selectedInbox,
  });

  const watch = useMutation({
    mutationFn: () => apiPost("/api/v1/emails/watch", { email }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["my-watched-emails"] }); setEmail(""); },
  });

  const unwatch = useMutation({
    mutationFn: (addr: string) => apiDelete(`/api/v1/emails/watch/${addr}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-watched-emails"] }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Email Inbox</h1>
        <p className="text-sm text-muted-foreground">Monitor and manage your email addresses</p>
      </div>

      <Card className="p-4 space-y-3">
        <h3 className="text-sm font-medium">Watch New Email</h3>
        <div className="flex gap-2">
          <Input placeholder="email@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Button onClick={() => watch.mutate()} disabled={!email} size="sm"><Plus className="h-4 w-4" /></Button>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Watched Addresses</h3>
          {watched?.addresses?.length ? (
            watched.addresses.map((a) => (
              <div key={a.email} className="flex items-center justify-between p-2 border border-border">
                <button onClick={() => setSelectedInbox(a.email)} className="text-sm hover:text-primary truncate">{a.email}</button>
                <Button variant="ghost" size="icon" onClick={() => unwatch.mutate(a.email)}><Trash2 className="h-3 w-3" /></Button>
              </div>
            ))
          ) : (
            <p className="text-xs text-muted-foreground">No addresses watched</p>
          )}
        </div>

        <div className="md:col-span-2">
          <h3 className="text-sm font-medium mb-2">{selectedInbox || "Select an address to view inbox"}</h3>
          {selectedInbox && inbox ? (
            <div className="space-y-2">
              {inbox.emails?.map((m, i) => (
                <div key={i} className="p-3 border border-border">
                  <p className="text-sm font-medium">{m.sender as string}</p>
                  <p className="text-xs text-muted-foreground">{m.subject as string}</p>
                  <p className="text-[10px] text-muted-foreground mt-1">{m.time as string}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={Eye} title="No emails" description={selectedInbox ? "No messages yet" : "Select a watched address"} />
          )}
        </div>
      </div>
    </div>
  );
}
