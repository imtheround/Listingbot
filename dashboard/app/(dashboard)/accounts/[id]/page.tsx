"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { formatDate } from "@/lib/utils";

interface AccountDetail {
  uuid: string;
  ign: string;
  email: string;
  status: string;
  created_at: string;
  last_login: string | null;
  licenses: { id: number; type: string; status: string; expires_at: string }[];
}

export default function AccountDetailPage() {
  const params = useParams();
  const { data: account, isLoading } = useQuery<AccountDetail>({
    queryKey: ["account", params.id],
    queryFn: () => apiFetch(`/api/v1/accounts/${params.id}`),
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
    return <div className="text-sm text-muted-foreground">Account not found</div>;
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
          <h2 className="text-lg font-semibold">{account.ign}</h2>
          <p className="text-sm text-muted-foreground font-mono">{account.uuid}</p>
        </div>
        <Badge variant={account.status === "active" ? "success" : "secondary"}>
          {account.status}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Email</span>
              <span>{account.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge variant={account.status === "active" ? "success" : "secondary"}>
                {account.status}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{formatDate(account.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Last Login</span>
              <span>{account.last_login ? formatDate(account.last_login) : "Never"}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Licenses</CardTitle>
          </CardHeader>
          <CardContent>
            {account.licenses?.length ? (
              <div className="space-y-2">
                {account.licenses.map((lic) => (
                  <div key={lic.id} className="flex items-center justify-between border p-3">
                    <div>
                      <p className="text-sm font-medium">{lic.type}</p>
                      <p className="text-xs text-muted-foreground">
                        Expires {formatDate(lic.expires_at)}
                      </p>
                    </div>
                    <Badge variant={lic.status === "active" ? "success" : "secondary"}>
                      {lic.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No licenses</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}