"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPut } from "@/lib/api";
import type { UserProfileResponse, UserSettingsResponse, PasswordChangeResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function SettingsPage() {
  const qc = useQueryClient();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");

  const { data: profile, isLoading } = useQuery<UserProfileResponse>({
    queryKey: ["profile"],
    queryFn: () => apiFetch<UserProfileResponse>("/api/v1/users/me"),
  });

  const updateSettings = useMutation({
    mutationFn: (body: { showleaderboard?: boolean }) =>
      apiPut<UserSettingsResponse>(`/api/v1/users/${profile?.user_id}/settings`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Settings updated");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const changePassword = useMutation({
    mutationFn: (body: { current_password: string; new_password: string }) =>
      apiPut<PasswordChangeResponse>(`/api/v1/users/${profile?.user_id}/password`, body),
    onSuccess: () => {
      toast.success("Password changed");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function handlePasswordChange() {
    if (!currentPassword || !newPassword) {
      toast.error("Please fill in all fields");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords don't match");
      return;
    }
    if (newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    changePassword.mutate({ current_password: currentPassword, new_password: newPassword });
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse bg-muted" />
        <div className="h-64 animate-pulse bg-muted" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">User configuration</p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">User ID</span>
            <span className="font-mono">{profile?.user_id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Claiming</span>
            <span>{profile?.claiming || "none"}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Rest Split</span>
            <span>{profile?.rest_split ?? 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Role</span>
            <span>{(profile?.permissions as Record<string, unknown>)?.role || "user"}</span>
          </div>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Show Leaderboard</p>
              <p className="text-xs text-muted-foreground">Display your username on the public leaderboard</p>
            </div>
            <button
              onClick={() =>
                updateSettings.mutate({
                  showleaderboard: !(profile?.permissions as Record<string, unknown>)?.showleaderboard,
                })
              }
              disabled={updateSettings.isPending}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                (profile?.permissions as Record<string, unknown>)?.showleaderboard
                  ? "bg-primary"
                  : "bg-muted"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  (profile?.permissions as Record<string, unknown>)?.showleaderboard
                    ? "translate-x-6"
                    : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Password */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Change Password</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            type="password"
            placeholder="Current password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
          <Input
            type="password"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Confirm new password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <div className="flex justify-end">
            <Button
              onClick={handlePasswordChange}
              disabled={!currentPassword || !newPassword || !confirmPassword || changePassword.isPending}
            >
              {changePassword.isPending ? "Changing..." : "Change Password"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
