"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, Lock } from "lucide-react";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError("Email and password are required"); return; }
    setLoading(true);
    setError("");
    try {
      const resp = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.detail || "Invalid credentials");
      }
      const data = await resp.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      document.cookie = `auth_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
      router.push("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center bg-primary text-primary-foreground">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-lg font-bold">AutoSecure</h1>
          <p className="text-sm text-muted-foreground mt-1">Admin Panel</p>
        </div>

        <div className="border border-border p-6">
          <div className="flex items-center gap-2 mb-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            <Lock className="h-3 w-3" /> Administrator Login
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full"
                placeholder="admin@autosecure.me"
                autoFocus
              />
            </div>
            <div>
              <label className="block text-xs text-muted-foreground mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full"
                placeholder="••••••••"
              />
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-10 flex items-center justify-center text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
        </div>

        <p className="text-[10px] text-muted-foreground text-center mt-6">
          Authorized personnel only &bull; All access is logged
        </p>
      </div>
    </div>
  );
}
