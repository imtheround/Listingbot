"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatDate } from "@/lib/utils";

export default function EmailsPage() {
  const qc = useQueryClient();
  const [address, setAddress] = useState("");
  const [watchAddr, setWatchAddr] = useState("");

  const { data: emails, isLoading } = useQuery<any>({
    queryKey: ["emails", address],
    queryFn: () => apiFetch("/api/v1/emails/" + encodeURIComponent(address)),
    enabled: !!address,
  });

  const watchEmail = useMutation({
    mutationFn: () => apiPost("/api/v1/emails/watch", { address: watchAddr }),
    onSuccess: () => { setAddress(watchAddr); setWatchAddr(""); qc.invalidateQueries({ queryKey: ["emails"] }); },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Emails</h1>
        <p className="text-sm text-muted-foreground">Email monitoring and verification</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Watch Email</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input placeholder="Email address" value={watchAddr} onChange={(e) => setWatchAddr(e.target.value)} />
              <Button onClick={() => watchEmail.mutate()} disabled={!watchAddr || watchEmail.isPending}>Watch</Button>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>View Emails</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input placeholder="Registered email address" value={address} onChange={(e) => setAddress(e.target.value)} />
              <Button onClick={() => setAddress(address)} disabled={!address}>Fetch</Button>
            </div>
          </CardContent>
        </Card>
      </div>
      {address && (
        <Card>
          <CardContent className="p-0">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="px-4 py-3 font-medium">Sender</th>
                  <th className="px-4 py-3 font-medium">Subject</th>
                  <th className="px-4 py-3 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={3} className="px-4 py-8 text-center text-sm text-muted-foreground">Loading...</td></tr>
                ) : emails?.emails?.length === 0 ? (
                  <tr><td colSpan={3} className="px-4 py-8 text-center text-sm text-muted-foreground">No emails found</td></tr>
                ) : (
                  emails?.emails?.map((e: any) => (
                    <tr key={e.id} className="border-b last:border-0 hover:bg-secondary/50">
                      <td className="px-4 py-3 text-sm">{e.sender}</td>
                      <td className="px-4 py-3 text-sm">{e.subject}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{e.time ? formatDate(e.time) : "-"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
