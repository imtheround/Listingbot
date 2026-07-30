import { ShieldCheck } from "lucide-react";

async function getStatus() {
  try {
    const res = await fetch("http://127.0.0.1:8000/health", { cache: "no-store" });
    if (!res.ok) return { status: "down", uptime: 0 };
    const data = await res.json();
    return { status: "ok", uptime: data.uptime || 0 };
  } catch {
    return { status: "down", uptime: 0 };
  }
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  if (days > 0) return `${days}d ${hours}h ${mins}m`;
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

export default async function StatusPage() {
  const { status, uptime } = await getStatus();

  return (
    <div className="py-20">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold">System Status</h1>
          <p className="mt-2 text-muted-foreground">
            Real-time status of all AutoSecure services.
          </p>
        </div>

        <div className="space-y-3">
          {[
            { name: "API Server", port: 8000 },
            { name: "Admin Dashboard", port: 3001 },
          ].map((service) => (
            <div key={service.name} className="flex items-center justify-between border border-border p-4">
              <div className="flex items-center gap-3">
                <div className={`h-2 w-2 rounded-full ${status === "ok" ? "bg-green-500" : "bg-red-500"}`} />
                <div>
                  <p className="text-sm font-medium">{service.name}</p>
                  <p className="text-[10px] text-muted-foreground">Port {service.port}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-xs font-medium ${status === "ok" ? "text-green-500" : "text-red-500"}`}>
                  {status === "ok" ? "Operational" : "Down"}
                </p>
                {service.port === 8000 && status === "ok" && (
                  <p className="text-[10px] text-muted-foreground">Uptime: {formatUptime(uptime)}</p>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <p className="text-[10px] text-muted-foreground">
            Last checked: {new Date().toUTCString()}
          </p>
          <p className="text-[10px] text-muted-foreground mt-1">
            Auto-refreshes on page load.
          </p>
        </div>
      </div>
    </div>
  );
}
