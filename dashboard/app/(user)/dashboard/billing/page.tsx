"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CreditCard, Crown, Star } from "lucide-react";

const plans = [
  { name: "Monthly", price: "$9.99/mo", features: ["Full account securing", "Unlimited bots", "Email monitoring", "Priority support"] },
  { name: "Yearly", price: "$79.99/yr", features: ["All Monthly features", "2 months free", "License transfer", "Bulk securing"], popular: true },
  { name: "Lifetime", price: "$199.99", features: ["All Yearly features", "Lifetime access", "Premium role", "Early access features"] },
];

export default function BillingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Billing</h1>
        <p className="text-sm text-muted-foreground">Upgrade your plan to unlock premium features</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={`p-6 space-y-4 ${plan.popular ? "border-primary ring-1 ring-primary" : ""}`}>
            {plan.popular && (
              <Badge variant="default" className="absolute -mt-10 ml-20"><Star className="h-3 w-3 mr-1" /> Popular</Badge>
            )}
            <div>
              <h3 className="text-lg font-bold">{plan.name}</h3>
              <p className="text-2xl font-bold mt-2">{plan.price}</p>
            </div>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {plan.features.map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <Crown className="h-3 w-3 text-primary" /> {f}
                </li>
              ))}
            </ul>
            <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
              <CreditCard className="h-4 w-4 mr-2" /> Upgrade to {plan.name}
            </Button>
          </Card>
        ))}
      </div>

      <p className="text-center text-xs text-muted-foreground">Payment processing coming soon. Crypto payments via NOWPayments.</p>
    </div>
  );
}
