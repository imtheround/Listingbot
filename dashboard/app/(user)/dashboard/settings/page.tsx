"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPut } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings, Shield } from "lucide-react";

export default function SettingsPage() {
  const qc = useQueryClient();

  const { data: profile } = useQuery<{ user_id: string; email: string | null; name: string; role: string; created_at: string }>({
    queryKey: ["my-profile"],
    queryFn: () => apiFetch("/auth/me"),
  });

  const { data: userSettings } = useQuery<{ showleaderboard: boolean; dm_notifications: boolean }>({
    queryKey: ["my-settings"],
    queryFn: () => apiFetch(`/api/v1/users/${profile?.user_id || "me"}/settings`),
    enabled: !!profile?.user_id,
  });

  const updateSettings = useMutation({
    mutationFn: (body: Record<string, unknown>) => apiPut(`/api/v1/users/${profile?.user_id || "me"}/settings`, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-settings"] }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">Manage your profile and preferences</p>
      </div>

      <Card className="p-6 space-y-4">
        <h3 className="text-sm font-medium flex items-center gap-2"><Shield className="h-4 w-4" /> Profile</h3>
        <div className="grid gap-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">User ID</span><span className="font-mono text-xs">{profile?.user_id}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Email</span><span>{profile?.email || "—"}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Name</span><span>{profile?.name || "—"}</span></div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Role</span>
            <Badge variant="outline">{profile?.role}</Badge>
          </div>
          <div className="flex justify-between"><span className="text-muted-foreground">Joined</span><span>{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : "—"}</span></div>
        </div>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-sm font-medium flex items-center gap-2"><Settings className="h-4 w-4" /> Preferences</h3>
        <div className="space-y-3">
          <label className="flex items-center justify-between">
            <span className="text-sm">Show on Leaderboard</span>
            <input
              type="checkbox"
              checked={!!(userSettings as Record<string, unknown>)?.showleaderboard}
              onChange={(e) => updateSettings.mutate({ showleaderboard: e.target.checked })}
              className="h-4 w-4"
            />
          </label>
          <label className="flex items-center justify-between">
            <span className="text-sm">DM Notifications</span>
            <input
              type="checkbox"
              checked={!!(userSettings as Record<string, unknown>)?.dm_notifications}
              onChange={(e) => updateSettings.mutate({ dm_notifications: e.target.checked })}
              className="h-4 w-4"
            />
          </label>
        </div>
      </Card>
    </div>
  );
}
