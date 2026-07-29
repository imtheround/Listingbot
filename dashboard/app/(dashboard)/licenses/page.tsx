"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost } from "@/lib/api";
import type {
  AdminLicenseResponse,
  AdminLicenseListResponse,
  LicenseGenerateRequest,
  LicenseGenerateResponse,
  LicenseResponse,
} from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Plus, Search, ArrowRightLeft, Key } from "lucide-react";
import { toast } from "sonner";

function getLicenseStatus(lic: AdminLicenseResponse): "active" | "expired" | "available" {
  if (!lic.is_used) return "available";
  if (!lic.expires_at) return "active";
  const now = new Date();
  const exp = new Date(lic.expires_at);
  if (exp < now) return "expired";
  const warningMs = 7 * 24 * 60 * 60 * 1000;
  if (exp.getTime() - now.getTime() < warningMs) return "active";
  return "active";
}

function statusBadge(status: string) {
  switch (status) {
    case "active":
      return <Badge variant="success">Active</Badge>;
    case "expired":
      return <Badge variant="destructive">Expired</Badge>;
    case "available":
      return <Badge variant="secondary">Available</Badge>;
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
}

export default function LicensesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showGenerate, setShowGenerate] = useState(false);
  const [showRedeem, setShowRedeem] = useState(false);
  const [transferKey, setTransferKey] = useState<string | null>(null);
  const [transferTarget, setTransferTarget] = useState("");

  const { data, isLoading } = useQuery<AdminLicenseListResponse>({
    queryKey: ["licenses"],
    queryFn: () => apiFetch<AdminLicenseListResponse>("/api/v1/admin/licenses"),
  });

  const generateMutation = useMutation({
    mutationFn: (body: LicenseGenerateRequest) =>
      apiPost<LicenseGenerateResponse>("/api/v1/admin/licenses/generate", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["licenses"] });
      toast.success(`Generated ${data.count} license keys`);
      setShowGenerate(false);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const transferMutation = useMutation({
    mutationFn: ({ key, new_user_id }: { key: string; new_user_id: string }) =>
      apiPost<LicenseResponse>(`/api/v1/licenses/transfer?license_key=${encodeURIComponent(key)}`, { new_user_id }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["licenses"] });
      toast.success("License transferred");
      setTransferKey(null);
      setTransferTarget("");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const filtered = data?.licenses?.filter(
    (lic) =>
      lic.license_key.toLowerCase().includes(search.toLowerCase()) ||
      (lic.user_id && lic.user_id.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Licenses</h1>
          <p className="text-sm text-muted-foreground">License key management</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowRedeem(!showRedeem)}>
            <Key className="mr-2 h-4 w-4" /> Redeem
          </Button>
          <Button onClick={() => setShowGenerate(!showGenerate)}>
            <Plus className="mr-2 h-4 w-4" /> Generate
          </Button>
        </div>
      </div>

      {showGenerate && (
        <GenerateForm
          onSubmit={(count, expiry) => generateMutation.mutate({ count, expiry })}
          loading={generateMutation.isPending}
          onCancel={() => setShowGenerate(false)}
        />
      )}

      {showRedeem && <RedeemForm onCancel={() => setShowRedeem(false)} />}

      {transferKey && (
        <Card>
          <CardContent className="p-4 space-y-3">
            <p className="text-sm font-medium">
              Transfer License: <span className="font-mono text-xs">{transferKey}</span>
            </p>
            <div className="flex gap-2">
              <Input
                placeholder="Target user ID"
                value={transferTarget}
                onChange={(e) => setTransferTarget(e.target.value)}
              />
              <Button
                onClick={() => transferMutation.mutate({ key: transferKey, new_user_id: transferTarget })}
                disabled={!transferTarget.trim() || transferMutation.isPending}
              >
                {transferMutation.isPending ? "Transferring..." : "Transfer"}
              </Button>
              <Button variant="ghost" onClick={() => { setTransferKey(null); setTransferTarget(""); }}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by key or user..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-4 py-3 font-medium">License Key</th>
                <th className="px-4 py-3 font-medium">User</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Expires</th>
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
              ) : filtered?.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-muted-foreground">
                    No licenses found
                  </td>
                </tr>
              ) : (
                filtered?.map((lic) => {
                  const status = getLicenseStatus(lic);
                  return (
                    <tr key={lic.license_key} className="border-b last:border-0 hover:bg-muted/50">
                      <td className="px-4 py-3 text-sm font-mono">{lic.license_key}</td>
                      <td className="px-4 py-3 text-sm">{lic.user_id || "—"}</td>
                      <td className="px-4 py-3">{statusBadge(status)}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {lic.expires_at ? formatDate(lic.expires_at) : "Never"}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {lic.is_used && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setTransferKey(lic.license_key);
                              setTransferTarget("");
                            }}
                          >
                            <ArrowRightLeft className="h-4 w-4" />
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

function GenerateForm({
  onSubmit,
  loading,
  onCancel,
}: {
  onSubmit: (count: number, expiry: string) => void;
  loading: boolean;
  onCancel: () => void;
}) {
  const [count, setCount] = useState(1);
  const [expiry, setExpiry] = useState("30d");

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">Generate Licenses</p>
        <div className="flex gap-2">
          <Input
            type="number"
            min={1}
            max={100}
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value) || 1)}
            placeholder="Count"
            className="w-24"
          />
          <Input
            value={expiry}
            onChange={(e) => setExpiry(e.target.value)}
            placeholder="Expiry (e.g. 30d, 24h)"
            className="w-40"
          />
        </div>
        <p className="text-xs text-muted-foreground">
          Expiry format: number + unit (d=days, h=hours). Example: 30d = 30 days.
        </p>
        <div className="flex gap-2 justify-end">
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={() => onSubmit(count, expiry)} disabled={loading}>
            {loading ? "Generating..." : "Generate"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function RedeemForm({ onCancel }: { onCancel: () => void }) {
  const qc = useQueryClient();
  const [key, setKey] = useState("");

  const redeemMutation = useMutation({
    mutationFn: (license_key: string) =>
      apiPost<LicenseResponse>("/api/v1/licenses/redeem", { license_key }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["licenses"] });
      toast.success(`License redeemed for user ${data.user_id}`);
      onCancel();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        <p className="text-sm font-medium">Redeem License Key</p>
        <div className="flex gap-2">
          <Input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="ASC-XXXXXXXX-XXXXXXXX"
            className="font-mono text-xs"
          />
          <Button onClick={() => redeemMutation.mutate(key)} disabled={!key.trim() || redeemMutation.isPending}>
            {redeemMutation.isPending ? "Redeeming..." : "Redeem"}
          </Button>
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          Enter a valid license key. Keys can be generated from the Generate button above.
        </p>
      </CardContent>
    </Card>
  );
}
