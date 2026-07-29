"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost, apiDelete } from "@/lib/api";
import type { EmailMessage, EmailListResponse, WatchedListResponse, WatchResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Inbox, Eye, EyeOff, RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { EmptyState } from "@/components/empty-state";

export default function EmailsPage() {
  const qc = useQueryClient();
  const [selectedAddress, setSelectedAddress] = useState("");
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Poll watched list
  const { data: watched } = useQuery<WatchedListResponse>({
    queryKey: ["emails", "watched"],
    queryFn: () => apiFetch<WatchedListResponse>("/api/v1/emails/watched/list"),
    refetchInterval: 30000,
  });

  // Poll emails for selected address
  const { data: emails, isLoading: emailsLoading } = useQuery<EmailListResponse>({
    queryKey: ["emails", selectedAddress],
    queryFn: () => apiFetch<EmailListResponse>("/api/v1/emails/" + encodeURIComponent(selectedAddress)),
    enabled: !!selectedAddress,
    refetchInterval: selectedAddress ? 5000 : false,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Emails</h1>
        <p className="text-sm text-muted-foreground">Email monitoring and verification</p>
      </div>

      <div className="grid gap-6 md:grid-cols-[300px_1fr]">
        {/* Sidebar: watched addresses */}
        <div className="space-y-4">
          <WatchedSidebar
            watched={watched}
            selected={selectedAddress}
            onSelect={setSelectedAddress}
          />
          <WatchForm />
        </div>

        {/* Main: email list */}
        <div>
          {selectedAddress ? (
            <EmailList
              address={selectedAddress}
              emails={emails}
              isLoading={emailsLoading}
              expandedId={expandedId}
              onToggle={(id) => setExpandedId(expandedId === id ? null : id)}
            />
          ) : (
            <Card>
              <CardContent className="py-12">
                <EmptyState
                  icon={Inbox}
                  title="Select an address"
                  description="Choose a watched email address to view its inbox."
                />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function WatchedSidebar({
  watched,
  selected,
  onSelect,
}: {
  watched: WatchedListResponse | undefined;
  selected: string;
  onSelect: (addr: string) => void;
}) {
  const qc = useQueryClient();
  const unwatch = useMutation({
    mutationFn: (addr: string) => apiDelete<WatchResponse>(`/api/v1/emails/watch/${encodeURIComponent(addr)}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["emails", "watched"] });
      toast.success("Stopped watching address");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Watched Addresses</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="max-h-[400px] overflow-y-auto">
          {watched?.addresses?.length === 0 ? (
            <p className="px-4 py-4 text-xs text-muted-foreground text-center">No watched addresses</p>
          ) : (
            watched?.addresses?.map((addr) => (
              <div
                key={addr.email}
                className={`flex items-center justify-between px-4 py-2.5 border-b last:border-0 cursor-pointer text-sm hover:bg-muted/50 ${
                  selected === addr.email ? "bg-muted" : ""
                }`}
                onClick={() => onSelect(addr.email)}
              >
                <span className="truncate font-mono text-xs">{addr.email}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Stop watching ${addr.email}?`)) {
                      unwatch.mutate(addr.email);
                    }
                  }}
                  title="Unwatch"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function WatchForm() {
  const qc = useQueryClient();
  const [email, setEmail] = useState("");

  const watchMutation = useMutation({
    mutationFn: (email: string) =>
      apiPost<WatchResponse>("/api/v1/emails/watch", { email }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["emails", "watched"] });
      toast.success("Now watching address");
      setEmail("");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Card>
      <CardContent className="p-4 space-y-2">
        <p className="text-xs font-medium">Add Watched Address</p>
        <div className="flex gap-2">
          <Input
            placeholder="user@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="text-xs"
          />
          <Button
            size="sm"
            onClick={() => watchMutation.mutate(email)}
            disabled={!email.trim() || watchMutation.isPending}
          >
            Watch
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function EmailList({
  address,
  emails,
  isLoading,
  expandedId,
  onToggle,
}: {
  address: string;
  emails: EmailListResponse | undefined;
  isLoading: boolean;
  expandedId: number | null;
  onToggle: (id: number) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            Inbox: <span className="font-mono">{address}</span>
          </CardTitle>
          <Badge variant="outline">{emails?.total || 0} messages</Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <table className="w-full">
          <thead>
            <tr className="border-b text-left text-xs text-muted-foreground">
              <th className="px-4 py-3 font-medium w-8"></th>
              <th className="px-4 py-3 font-medium">Sender</th>
              <th className="px-4 py-3 font-medium">Subject</th>
              <th className="px-4 py-3 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">
                  Loading...
                </td>
              </tr>
            ) : emails?.emails?.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No emails found
                </td>
              </tr>
            ) : (
              emails?.emails?.map((email) => (
                <>
                  <tr
                    key={email.id}
                    className="border-b hover:bg-muted/50 cursor-pointer"
                    onClick={() => onToggle(email.id)}
                  >
                    <td className="px-4 py-3">
                      {expandedId === email.id ? (
                        <EyeOff className="h-3.5 w-3.5 text-muted-foreground" />
                      ) : (
                        <Eye className="h-3.5 w-3.5 text-muted-foreground" />
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium">{email.sender}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{email.subject}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">
                      {email.time ? formatDate(email.time) : "—"}
                    </td>
                  </tr>
                  {expandedId === email.id && (
                    <tr key={`${email.id}-detail`}>
                      <td colSpan={4} className="px-4 py-3 bg-muted/30 border-b">
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">From: </span>
                            <span className="font-medium">{email.sender}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Subject: </span>
                            <span>{email.subject}</span>
                          </div>
                          <div className="mt-2 whitespace-pre-wrap text-sm border-l-2 border-border pl-3">
                            {email.description}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))
            )}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
