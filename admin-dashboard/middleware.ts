import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/auth") || pathname.startsWith("/api") || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  const token = request.cookies.get("auth_token")?.value;

  if (pathname === "/login") {
    if (token) return NextResponse.redirect(new URL("/admin", request.url));
    return NextResponse.next();
  }

  if (pathname === "/") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|api|favicon.ico).*)"],
};
