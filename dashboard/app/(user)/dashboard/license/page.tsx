"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Key, Ticket } from "lucide-react";

export default function LicensePage() {
  const qc = useQueryClient();
  const [redeemKey, setRedeemKey] = useState("");
  const [transferTo, setTransferTo] = useState("");
  const [transferKey, setTransferKey] = useState("");

  const { data: profile } = useQuery<{ user_id: string; role: string }>({
    queryKey: ["my-profile"],
    queryFn: () => apiFetch("/auth/me"),
  });

  const { data: stats } = useQuery<{ has_license: boolean; license_expiry: string | null }>({
    queryKey: ["user-stats"],
    queryFn: () => apiFetch("/api/v1/dashboard/user-stats"),
  });

  const redeem = useMutation({
    mutationFn: () => apiPost("/api/v1/licenses/redeem", { license_key: redeemKey }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["user-stats"] }); setRedeemKey(""); },
  });

  const transfer = useMutation({
    mutationFn: () => apiPost("/api/v1/licenses/transfer", { license_key: transferKey, new_user_id: transferTo }),
    onSuccess: () => { setTransferTo(""); setTransferKey(""); },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">License</h1>
        <p className="text-sm text-muted-foreground">Your license status and management</p>
      </div>

      <Card className="p-6 space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center bg-primary/10 rounded-full">
            <Key className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium">
              {stats?.has_license ? "Active License" : "No License"}
            </p>
            <p className="text-xs text-muted-foreground">
              {stats?.has_license
                ? `Expires: ${stats.license_expiry ? new Date(stats.license_expiry).toLocaleDateString() : "Unknown"}`
                : "Purchase a license to unlock all features"}
            </p>
          </div>
          <Badge variant={stats?.has_license ? "success" : "secondary"} className="ml-auto">
            {profile?.role === "premium" ? "Premium" : stats?.has_license ? "Active" : "Free"}
          </Badge>
        </div>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="p-4 space-y-3">
          <h3 className="text-sm font-medium flex items-center gap-2"><Ticket className="h-4 w-4" /> Redeem Key</h3>
          <Input placeholder="Enter license key" value={redeemKey} onChange={(e) => setRedeemKey(e.target.value)} />
          <Button onClick={() => redeem.mutate()} disabled={!redeemKey || redeem.isPending} size="sm">Redeem</Button>
          {redeem.isError && <p className="text-xs text-destructive">{(redeem.error as Error).message}</p>}
        </Card>

        <Card className="p-4 space-y-3">
          <h3 className="text-sm font-medium flex items-center gap-2"><Key className="h-4 w-4" /> Transfer License</h3>
          <Input placeholder="License key" value={transferKey} onChange={(e) => setTransferKey(e.target.value)} />
          <Input placeholder="New user ID" value={transferTo} onChange={(e) => setTransferTo(e.target.value)} />
          <Button onClick={() => transfer.mutate()} disabled={!transferKey || !transferTo || transfer.isPending} size="sm">Transfer</Button>
        </Card>
      </div>
    </div>
  );
}
