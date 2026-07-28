"use client";
import { cn } from "@/lib/utils";
import { forwardRef, type ButtonHTMLAttributes } from "react";

const styles = {
  default: "bg-primary text-primary-foreground hover:bg-primary/90",
  destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
  outline: "border border-border bg-transparent hover:bg-secondary",
  ghost: "hover:bg-secondary text-muted-foreground hover:text-foreground",
  link: "text-primary underline-offset-4 hover:underline",
};

const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof styles; size?: string }>(
  ({ className, variant = "default", size = "default", ...props }, ref) => (
    <button
      className={cn(
        "inline-flex items-center justify-center text-sm font-medium transition-colors",
        "disabled:opacity-50 disabled:pointer-events-none",
        size === "sm" ? "h-8 px-3 text-xs" : size === "lg" ? "h-10 px-8" : size === "icon" ? "h-9 w-9" : "h-9 px-4",
        styles[variant] || styles.default,
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Button.displayName = "Button";
export { Button };
