"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { AccountResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { formatDate } from "@/lib/utils";
import { EmptyState } from "@/components/empty-state";

export default function AccountDetailPage() {
  const params = useParams();
  const { data: account, isLoading } = useQuery<AccountResponse>({
    queryKey: ["account", params.id],
    queryFn: () => apiFetch<AccountResponse>(`/api/v1/accounts/${params.id}`),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse bg-muted" />
        <div className="h-64 animate-pulse bg-muted" />
      </div>
    );
  }

  if (!account) {
    return <EmptyState title="Account not found" description="This account may have been deleted." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/accounts">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h2 className="text-lg font-semibold">{account.username}</h2>
          <p className="text-sm text-muted-foreground font-mono">{account.uid}</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row label="Username" value={account.username} />
            <Row label="UID" value={account.uid} mono />
            <Row label="Email" value={account.email ?? "—"} />
            <Row label="Networth" value={account.networth != null ? account.networth.toLocaleString() : "—"} />
            <Row label="Created" value={formatDate(account.created_at)} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Use the <span className="font-mono text-xs">/api/v1/accounts/{account.uid}/stats</span> endpoint
              to fetch live Hypixel stats for this account.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className={mono ? "font-mono text-xs" : ""}>{value}</span>
    </div>
  );
}
