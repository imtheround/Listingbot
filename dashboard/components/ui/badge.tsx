import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const styles: Record<string, string> = {
  default: "bg-primary text-primary-foreground",
  secondary: "bg-secondary text-secondary-foreground",
  destructive: "bg-destructive text-destructive-foreground",
  outline: "border border-border text-foreground",
  success: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  warning: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
};

export function Badge({ className, variant = "default", ...props }: HTMLAttributes<HTMLDivElement> & { variant?: string }) {
  return <div className={cn("inline-flex items-center px-2 py-0.5 text-xs font-medium", styles[variant] || styles.default, className)} {...props} />;
}
