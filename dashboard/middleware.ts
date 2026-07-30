import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const publicPaths = ["/", "/pricing", "/faq", "/tos", "/privacy", "/status"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow auth, API, static files
  if (pathname.startsWith("/auth") || pathname.startsWith("/api") || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  // Allow public paths
  if (publicPaths.includes(pathname)) {
    return NextResponse.next();
  }

  const token = request.cookies.get("auth_token")?.value;

  // Login page: redirect to /admin if already logged in
  if (pathname === "/login") {
    if (token) return NextResponse.redirect(new URL("/admin", request.url));
    return NextResponse.next();
  }

  // Protected routes: redirect to /login if no token
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|api|favicon.ico).*)"],
};
