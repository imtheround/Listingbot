"use client";
import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  const [userId, setUserId] = useState("");

  useEffect(() => {
    if (!userId) return;
    apiFetch("/api/v1/users/" + userId).catch(() => {});
  }, [userId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">User configuration</p>
      </div>
      <Card>
        <CardHeader><CardTitle>User Settings</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input placeholder="User ID" value={userId} onChange={(e) => setUserId(e.target.value)} />
          </div>
          <div className="border-t pt-4">
            <p className="text-sm text-muted-foreground">
              Enter a User ID above to load and edit settings.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
