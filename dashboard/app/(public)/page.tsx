import Link from "next/link";
import { ShieldCheck, Lock, Eye, Zap, Bot, CreditCard } from "lucide-react";

const features = [
  {
    icon: Lock,
    title: "Account Security",
    description: "Automatically secure your Microsoft accounts with recovery codes, session management, and real-time monitoring.",
  },
  {
    icon: Bot,
    title: "Automated Bots",
    description: "Deploy Discord bots that monitor, protect, and manage your accounts 24/7 with zero downtime.",
  },
  {
    icon: Eye,
    title: "Email Monitoring",
    description: "Real-time email watching for security alerts, verification codes, and suspicious activity notifications.",
  },
  {
    icon: Zap,
    title: "Instant Actions",
    description: "Quick-respond to threats with one-click account locking, session revoking, and password resets.",
  },
  {
    icon: CreditCard,
    title: "Crypto Payments",
    description: "Pay with Bitcoin, Ethereum, USDT, and more. No KYC, no middlemen, fully anonymous.",
  },
  {
    icon: ShieldCheck,
    title: "Enterprise Grade",
    description: "Built with industry-standard encryption, audit logging, and compliance in mind.",
  },
];

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/5" />
        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center bg-primary text-primary-foreground">
            <ShieldCheck className="h-8 w-8" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Protect Your <span className="text-primary">Digital Assets</span>
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            AutoSecure is a comprehensive security platform for Microsoft and Minecraft accounts.
            Automated protection, real-time monitoring, and instant threat response.
          </p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <Link
              href="/login"
              className="bg-primary text-primary-foreground px-6 py-3 text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="/pricing"
              className="border border-border px-6 py-3 text-sm font-medium hover:bg-secondary transition-colors"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-2xl font-bold text-center mb-12">Everything You Need</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="border border-border p-6 hover:bg-secondary/50 transition-colors">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-sm font-semibold mb-2">{feature.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 border-t border-border">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Secure Your Accounts?</h2>
          <p className="text-muted-foreground mb-8">
            Join thousands of users who trust AutoSecure to protect their digital assets.
          </p>
          <Link
            href="/login"
            className="bg-primary text-primary-foreground px-8 py-3 text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            Sign In with Google
          </Link>
        </div>
      </section>
    </div>
  );
}
