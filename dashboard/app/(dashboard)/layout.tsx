"use client";

import { Sidebar } from "@/components/sidebar";
import { useSSE } from "@/lib/hooks/useSSE";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  useSSE();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 pl-56">
        <div className="h-12 border-b border-border bg-card flex items-center px-6">
          <span className="text-xs text-muted-foreground font-mono">autosecure.api</span>
        </div>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
