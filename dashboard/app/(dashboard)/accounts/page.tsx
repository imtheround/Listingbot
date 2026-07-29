"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import type { AccountListResponse, AccountCreateRequest } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Search, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { EmptyState } from "@/components/empty-state";
import { toast } from "sonner";

export default function AccountsPage() {
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const qc = useQueryClient();

  const { data, isLoading } = useQuery<AccountListResponse>({
    queryKey: ["accounts"],
    queryFn: () => apiFetch<AccountListResponse>("/api/v1/accounts"),
  });

  const deleteAccount = useMutation({
    mutationFn: (uid: string) => apiDelete(`/api/v1/accounts/${uid}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Account deleted");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const filtered = data?.accounts.filter(
    (a) =>
      a.username?.toLowerCase().includes(search.toLowerCase()) ||
      a.uid?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Accounts</h2>
          <p className="text-sm text-muted-foreground">Manage Minecraft accounts</p>
        </div>
        <Button onClick={() => setShowAdd((s) => !s)}>
          <Plus className="mr-2 h-4 w-4" /> Add Account
        </Button>
      </div>

      {showAdd && <AddAccountForm onDone={() => setShowAdd(false)} />}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search by username or UID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10 max-w-sm"
        />
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead className="border-b">
              <tr className="text-left text-sm text-muted-foreground">
                <th className="px-4 py-3 font-medium">Username</th>
                <th className="px-4 py-3 font-medium">UID</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Networth</th>
                <th className="px-4 py-3 font-medium">Added</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td colSpan={6} className="h-16 animate-pulse bg-muted" />
                  </tr>
                ))
              ) : filtered?.length === 0 ? (
                <tr>
                  <td colSpan={6}>
                    <EmptyState
                      icon={Plus}
                      title="No accounts yet"
                      description="Add your first secured account to get started."
                    />
                  </td>
                </tr>
              ) : (
                filtered?.map((account) => (
                  <tr key={account.uid} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-3 font-medium">{account.username}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground font-mono">
                      {account.uid.slice(0, 8)}...
                    </td>
                    <td className="px-4 py-3 text-sm">{account.email ?? "—"}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {account.networth != null ? account.networth.toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {formatDate(account.created_at)}
                    </td>
                    <td className="px-4 py-3 flex gap-1">
                      <Link href={`/accounts/${account.uid}`}>
                        <Button variant="ghost" size="sm">View</Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          if (confirm(`Delete account ${account.username}?`)) {
                            deleteAccount.mutate(account.uid);
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

function AddAccountForm({ onDone }: { onDone: () => void }) {
  const qc = useQueryClient();
  const [uid, setUid] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");

  const create = useMutation({
    mutationFn: () =>
      apiPost("/api/v1/accounts", {
        uid,
        username,
        email: email || null,
        recovery_code: recoveryCode || null,
      } satisfies AccountCreateRequest),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Account added");
      onDone();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">New Account</p>
        <div className="grid gap-3 md:grid-cols-2">
          <Input placeholder="UID *" value={uid} onChange={(e) => setUid(e.target.value)} />
          <Input placeholder="Username *" value={username} onChange={(e) => setUsername(e.target.value)} />
          <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input placeholder="Recovery Code" value={recoveryCode} onChange={(e) => setRecoveryCode(e.target.value)} />
        </div>
        <div className="flex gap-2 justify-end">
          <Button variant="ghost" onClick={onDone}>Cancel</Button>
          <Button onClick={() => create.mutate()} disabled={!uid || !username || create.isPending}>
            {create.isPending ? "Adding..." : "Add"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
