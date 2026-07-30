"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Database,
  Bot,
  Key,
  Mail,
  Link2,
  Settings,
  CreditCard,
  LogOut,
} from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/accounts", label: "My Accounts", icon: Database },
  { href: "/dashboard/bots", label: "My Bots", icon: Bot },
  { href: "/dashboard/license", label: "License", icon: Key },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/emails", label: "Emails", icon: Mail },
  { href: "/dashboard/webhooks", label: "Webhooks", icon: Link2 },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function UserSidebar() {
  const p = usePathname();
  const r = useRouter();

  const logout = () => {
    document.cookie = "auth_token=; path=/; max-age=0";
    localStorage.clear();
    r.push("/login");
  };

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r border-border bg-card">
      <div className="flex h-12 items-center gap-2 border-b border-border px-5">
        <div className="sb-gradient flex h-6 w-6 items-center justify-center">
          <Key className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-semibold tracking-tight">AutoSecure</span>
        <span className="ml-auto text-[10px] font-medium text-primary border border-primary/30 rounded px-1.5 py-0.5">USER</span>
      </div>
      <nav className="flex-1 p-3 space-y-0.5">
        {nav.map((item) => {
          const Icon = item.icon;
          const active = p === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary text-primary-foreground font-medium"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
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
          <span>User Dashboard</span>
          <span>v1.0.0</span>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors w-full"
        >
          <LogOut className="h-3 w-3" /> Sign Out
        </button>
      </div>
    </aside>
  );
}