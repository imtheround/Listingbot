import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface BotStatusBadgeProps {
  status: string;
  className?: string;
}

export function BotStatusBadge({ status, className }: BotStatusBadgeProps) {
  const variant = status === "running" ? "success" : "secondary";
  return (
    <Badge variant={variant} className={cn("flex items-center gap-1.5 w-fit", className)}>
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          status === "running" ? "bg-emerald-400 animate-pulse" : "bg-muted-foreground"
        )}
      />
      {status}
    </Badge>
  );
}
