import { redirect } from "next/navigation";
import { headers } from "next/headers";
import Link from "next/link";
import { ShieldCheck, Lock, Eye, Zap, Bot, CreditCard } from "lucide-react";

export default async function RootPage() {
  const hostList = await headers();
  const host = hostList.get("host") || "";
  if (host.includes(":3000")) {
    redirect("/login");
  }

  const features = [
    { icon: Lock, title: "Account Security", description: "Automatically secure your Microsoft accounts with recovery codes, session management, and real-time monitoring." },
    { icon: Eye, title: "Email Monitoring", description: "Monitor incoming emails, intercept verification codes, and protect your accounts." },
    { icon: Zap, title: "Bulk Operations", description: "Process multiple accounts at once with bulk securing and recovery workflows." },
    { icon: Bot, title: "Bot Automation", description: "Create automated bots with per-user isolation and configurable event handling." },
    { icon: ShieldCheck, title: "Hypixel Stats", description: "Track your Minecraft stats, leaderboards, and account net worth in real-time." },
    { icon: CreditCard, title: "Flexible Plans", description: "Choose monthly, yearly, or lifetime plans to match your usage needs." },
  ];

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 h-14">
          <Link href="/" className="flex items-center gap-2">
            <div className="sb-gradient flex h-6 w-6 items-center justify-center">
              <ShieldCheck className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-semibold">AutoSecure</span>
          </Link>
          <nav className="flex items-center gap-4 text-xs text-muted-foreground">
            <Link href="/pricing">Pricing</Link>
            <Link href="/faq">FAQ</Link>
            <Link href="/status">Status</Link>
            <Link href="/login" className="text-primary font-medium">Sign In</Link>
          </nav>
        </div>
      </header>
      <main>
        <section className="py-24 text-center">
          <h1 className="text-4xl font-bold tracking-tight">Secure Your Minecraft Accounts</h1>
          <p className="mt-4 max-w-lg mx-auto text-sm text-muted-foreground">
            All-in-one platform for securing Microsoft accounts. Automated recovery, email monitoring, and Hypixel stats tracking.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Link href="/login" className="inline-flex h-10 items-center px-6 text-sm font-medium bg-primary text-primary-foreground rounded-md">Get Started</Link>
            <Link href="/pricing" className="inline-flex h-10 items-center px-6 text-sm font-medium border border-border rounded-md">View Plans</Link>
          </div>
        </section>
        <section className="py-16 border-t border-border">
          <div className="mx-auto max-w-6xl px-6">
            <h2 className="text-2xl font-bold text-center mb-12">Everything you need</h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => (
                <div key={f.title} className="p-6 border border-border rounded-lg">
                  <f.icon className="h-8 w-8 text-primary mb-3" />
                  <h3 className="text-sm font-semibold mb-1">{f.title}</h3>
                  <p className="text-xs text-muted-foreground">{f.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
      <footer className="border-t border-border py-8 text-center text-xs text-muted-foreground">
        <div className="flex justify-center gap-4 mb-2">
          <Link href="/tos">Terms</Link>
          <Link href="/privacy">Privacy</Link>
          <Link href="/status">Status</Link>
        </div>
        <p>&copy; 2026 AutoSecure. All rights reserved.</p>
      </footer>
    </div>
  );
}
