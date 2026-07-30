"use client";

import { UserSidebar } from "@/components/user-sidebar";
import { useSSE } from "@/lib/hooks/useSSE";

export default function UserDashboardLayout({ children }: { children: React.ReactNode }) {
  useSSE();

  return (
    <div className="flex min-h-screen bg-background">
      <UserSidebar />
      <main className="flex-1 ml-56">
        <div className="h-12 border-b border-border bg-card flex items-center px-6">
          <span className="text-xs text-muted-foreground font-mono">autosecure / dashboard</span>
          <span className="ml-auto text-[10px] font-medium text-primary border border-primary/30 rounded px-1.5 py-0.5">USER</span>
        </div>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}