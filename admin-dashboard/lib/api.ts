function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem("access_token");
  } catch {
    return null;
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = "Bearer " + token;

  const url = path.startsWith("http") ? path : path;
  const res = await fetch(url, { ...options, headers });

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("access_token");
      document.cookie = "auth_token=; path=/; max-age=0";
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || body.message || "Request failed: " + res.status);
  }

  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function apiPut<T>(path: string, body?: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function apiDelete<T>(path: string): Promise<T> {
  return apiFetch<T>(path, { method: "DELETE" });
}
