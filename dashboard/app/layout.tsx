import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/app/providers";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AutoSecure",
  description: "Account Security Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={inter.className}>
        <Providers>
          <div className="flex min-h-screen bg-background">
            <Sidebar />
            <main className="flex-1 pl-56">
              <div className="h-12 border-b border-border bg-card flex items-center px-6">
                <span className="text-xs text-muted-foreground font-mono">autosecure.api</span>
              </div>
              <div className="p-6">{children}</div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
