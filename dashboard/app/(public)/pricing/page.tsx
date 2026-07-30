import { ShieldCheck, Check } from "lucide-react";
import Link from "next/link";

const plans = [
  {
    name: "Monthly",
    price: "$9.99",
    period: "/month",
    description: "Perfect for trying out AutoSecure",
    features: [
      "Full account protection",
      "Unlimited bots",
      "Email monitoring",
      "Real-time alerts",
      "Priority support",
    ],
    cta: "Start Monthly",
    popular: false,
  },
  {
    name: "Yearly",
    price: "$79.99",
    period: "/year",
    description: "Save 33% compared to monthly",
    features: [
      "Everything in Monthly",
      "Save $40/year",
      "Priority support",
      "Early access to features",
      "Dedicated IP protection",
    ],
    cta: "Start Yearly",
    popular: true,
  },
  {
    name: "Lifetime",
    price: "$199.99",
    period: "one-time",
    description: "Pay once, use forever",
    features: [
      "Everything in Yearly",
      "Lifetime updates",
      "VIP support channel",
      "Custom bot configuration",
      "API access",
    ],
    cta: "Get Lifetime",
    popular: false,
  },
];

export default function PricingPage() {
  return (
    <div className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold">Simple, Transparent Pricing</h1>
          <p className="mt-2 text-muted-foreground">
            Choose the plan that works for you. Pay with crypto, no KYC required.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative border p-6 ${
                plan.popular ? "border-primary shadow-md" : "border-border"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-[10px] font-medium px-3 py-0.5">
                  MOST POPULAR
                </div>
              )}
              <div className="mb-6">
                <h3 className="text-sm font-semibold">{plan.name}</h3>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  <span className="text-xs text-muted-foreground">{plan.period}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{plan.description}</p>
              </div>
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-xs">
                    <Check className="h-3 w-3 text-primary flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/login"
                className={`block text-center py-2 text-sm font-medium transition-colors ${
                  plan.popular
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "border border-border hover:bg-secondary"
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-xs text-muted-foreground">
            All plans include: SSL encryption, 99.9% uptime, automatic updates, and 24/7 monitoring.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Payments processed via NOWPayments. We accept BTC, ETH, USDT, SOL, and 50+ other cryptocurrencies.
          </p>
        </div>
      </div>
    </div>
  );
}
