"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Database, Bot, Key, Mail, Settings, ScrollText, Webhook, LogOut, ShieldCheck } from "lucide-react";

const nav = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/accounts", label: "Accounts", icon: Database },
  { href: "/admin/bots", label: "Bots", icon: Bot },
  { href: "/admin/licenses", label: "Licenses", icon: Key },
  { href: "/admin/emails", label: "Emails", icon: Mail },
  { href: "/admin/logs", label: "Logs", icon: ScrollText },
  { href: "/admin/webhooks", label: "Webhooks", icon: Webhook },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

export function AdminSidebar() {
  const p = usePathname();
  const r = useRouter();
  const logout = () => { document.cookie = "auth_token=; path=/; max-age=0"; localStorage.clear(); r.push("/login"); };
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r border-border bg-card">
      <div className="flex h-12 items-center gap-2 border-b border-border px-5">
        <div className="flex h-6 w-6 items-center justify-center bg-primary">
          <ShieldCheck className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="text-sm font-semibold tracking-tight">AutoSecure</span>
        <span className="ml-auto text-[10px] font-medium text-destructive border border-destructive/30 rounded px-1.5 py-0.5">ADMIN</span>
      </div>
      <nav className="flex-1 p-3 space-y-0.5">
        {nav.map((item) => {
          const Icon = item.icon;
          const active = p === item.href;
          return (
            <Link key={item.href} href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 text-sm transition-colors",
                active ? "bg-primary text-primary-foreground font-medium" : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-border p-3 space-y-2">
        <div className="flex items-center justify-between text-[10px] text-muted-foreground">
          <span>Admin Panel</span>
          <span>v1.0.0</span>
        </div>
        <button onClick={logout} className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors w-full">
          <LogOut className="h-3 w-3" /> Sign Out
        </button>
      </div>
    </aside>
  );
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <AdminSidebar />
      <main className="flex-1 ml-56">
        <div className="h-12 border-b border-border bg-card flex items-center px-6">
          <span className="text-xs text-muted-foreground font-mono">autosecure / admin-panel</span>
          <span className="ml-auto text-[10px] font-medium text-destructive border border-destructive/30 rounded px-1.5 py-0.5">RESTRICTED</span>
        </div>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
