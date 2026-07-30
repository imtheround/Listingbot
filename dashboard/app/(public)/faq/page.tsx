"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const faqs = [
  {
    q: "What is AutoSecure?",
    a: "AutoSecure is a comprehensive security platform for Microsoft and Minecraft accounts. It provides automated account protection, real-time monitoring, email watching, and instant threat response through Discord bots.",
  },
  {
    q: "How does account protection work?",
    a: "AutoSecure monitors your accounts 24/7. When suspicious activity is detected (login from new location, password change, session hijack), it automatically takes protective action like revoking sessions, locking accounts, or alerting you via Discord.",
  },
  {
    q: "Is my data safe?",
    a: "Yes. All sensitive data is encrypted at rest using Fernet encryption. We use industry-standard security practices, and your credentials are never stored in plain text. We also support hCaptcha to prevent bot abuse.",
  },
  {
    q: "What cryptocurrencies do you accept?",
    a: "We accept Bitcoin (BTC), Ethereum (ETH), USDT, Solana (SOL), and 50+ other cryptocurrencies through NOWPayments. No KYC is required.",
  },
  {
    q: "Can I cancel my subscription?",
    a: "Yes. You can cancel anytime from your dashboard. Monthly and yearly plans will remain active until the end of the billing period. Lifetime plans are non-refundable.",
  },
  {
    q: "How do I set up AutoSecure?",
    a: "1. Sign in with Google OAuth. 2. Purchase a license key. 3. Redeem the key in your dashboard. 4. Add your Discord bot. 5. Configure your account protection settings. It takes less than 5 minutes.",
  },
  {
    q: "Do you offer a free trial?",
    a: "Yes! New users get an 8-hour trial period to test all features before purchasing a license.",
  },
  {
    q: "What happens if AutoSecure goes down?",
    a: "We maintain 99.9% uptime with redundant infrastructure. If the service goes down, your accounts remain safe — we just can't actively monitor them until the service is restored. Check our status page for real-time updates.",
  },
];

export default function FAQPage() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <div className="py-20">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold">Frequently Asked Questions</h1>
          <p className="mt-2 text-muted-foreground">
            Can&apos;t find what you&apos;re looking for? Contact us on Discord.
          </p>
        </div>

        <div className="space-y-2">
          {faqs.map((faq, i) => (
            <div key={i} className="border border-border">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between p-4 text-left text-sm font-medium hover:bg-secondary/50 transition-colors"
              >
                {faq.q}
                <ChevronDown
                  className={cn(
                    "h-4 w-4 text-muted-foreground transition-transform",
                    open === i && "rotate-180"
                  )}
                />
              </button>
              {open === i && (
                <div className="px-4 pb-4 text-xs text-muted-foreground leading-relaxed">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
