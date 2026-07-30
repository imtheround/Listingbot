"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/empty-state";
import { Database, Search, Plus, Trash2 } from "lucide-react";

export default function AccountsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ uid: "", username: "", email: "", recovery_code: "" });

  const { data, isLoading } = useQuery<{ accounts?: Array<Record<string, unknown>>; total?: number; page?: number; pages?: number }>({
    queryKey: ["my-accounts", search],
    queryFn: () => apiFetch(`/api/v1/accounts?search=${search}`),
  });

  const addAccount = useMutation({
    mutationFn: (body: Record<string, unknown>) => apiPost("/api/v1/accounts", body),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["my-accounts"] }); setShowAdd(false); setForm({ uid: "", username: "", email: "", recovery_code: "" }); },
  });

  const deleteAccount = useMutation({
    mutationFn: (uid: string) => apiDelete(`/api/v1/accounts/${uid}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-accounts"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">My Accounts</h1>
          <p className="text-sm text-muted-foreground">Your secured accounts</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)} size="sm">
          <Plus className="h-4 w-4 mr-1" /> Add Account
        </Button>
      </div>

      {showAdd && (
        <Card className="p-4 space-y-3">
          <Input placeholder="UID" value={form.uid} onChange={(e) => setForm({ ...form, uid: e.target.value })} />
          <Input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <Input placeholder="Email (optional)" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input placeholder="Recovery Code (optional)" value={form.recovery_code} onChange={(e) => setForm({ ...form, recovery_code: e.target.value })} />
          <Button onClick={() => addAccount.mutate(form)} disabled={!form.uid || !form.username} size="sm">
            Save Account
          </Button>
        </Card>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input className="pl-9" placeholder="Search accounts..." value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-16 animate-pulse bg-muted rounded-lg" />)}</div>
      ) : data?.accounts?.length ? (
        <div className="space-y-2">
          {data.accounts.map((a: Record<string, unknown>) => (
            <div key={a.uid as string} className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="text-sm font-medium">{a.username as string}</p>
                <p className="text-xs text-muted-foreground">{a.uid as string}{a.email ? ` | ${a.email}` : ""}</p>
              </div>
              <div className="flex items-center gap-2">
                {a.networth != null && <Badge variant="outline">{String(a.networth)}</Badge>}
                <Button variant="ghost" size="icon" onClick={() => deleteAccount.mutate(a.uid as string)}>
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState icon={Database} title="No accounts yet" description="Add your first secured account." />
      )}
    </div>
  );
}
