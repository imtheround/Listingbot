"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

export default function LicensesPage() {
  const { data: licenses, isLoading } = useQuery<any>({ queryKey: ["licenses"], queryFn: () => apiFetch("/api/v1/admin/licenses") });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Licenses</h1>
        <p className="text-sm text-muted-foreground">License key management</p>
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
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">Loading...</td></tr>
              ) : licenses?.licenses?.length === 0 ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">No licenses found</td></tr>
              ) : (
                licenses?.licenses?.map((lic: any) => (
                  <tr key={lic.license_key} className="border-b last:border-0 hover:bg-secondary/50">
                    <td className="px-4 py-3 text-sm font-mono">{lic.license_key}</td>
                    <td className="px-4 py-3 text-sm">{lic.user_id || "-"}</td>
                    <td className="px-4 py-3"><Badge variant={lic.is_used ? "success" : "secondary"}>{lic.is_used ? "Used" : "Available"}</Badge></td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{lic.expires_at ? formatDate(lic.expires_at) : "Never"}</td>
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
