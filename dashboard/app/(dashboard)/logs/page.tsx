"use client";
import { Card, CardContent } from "@/components/ui/card";

export default function LogsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Activity Logs</h1>
        <p className="text-sm text-muted-foreground">System audit log</p>
      </div>
      <Card>
        <CardContent className="p-8 text-center text-sm text-muted-foreground">
          Log viewer coming soon.
        </CardContent>
      </Card>
    </div>
  );
}
