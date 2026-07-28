import Head from "next/head";
import { useSession } from "next-auth/react";
import { useRouter } from "next/router";

export default function Layout({ children, title = "Hits Manager" }) {
  const { data: session } = useSession();
  const router = useRouter();

  const isActive = (path) => router.pathname === path;

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Discord-integrated hits management platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-black text-white">
        {/* Navigation */}
        {session && (
          <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40 backdrop-blur-sm bg-gray-900/95">
            <div className="container-responsive">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center space-x-8">
                  <a href="/" className="text-xl font-bold text-gradient hover-glow">
                    Hits Manager
                  </a>
                  <div className="hidden md:flex space-x-6">
                    <a
                      href="/"
                      className={`nav-link ${isActive('/') ? 'active' : ''}`}
                    >
                      Dashboard
                    </a>
                    <a
                      href="/hits"
                      className={`nav-link ${isActive('/hits') ? 'active' : ''}`}
                    >
                      All Hits
                    </a>
                    <a
                      href="/profile"
                      className={`nav-link ${isActive('/profile') ? 'active' : ''}`}
                    >
                      Profile
                    </a>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {session.user.premium && (
                    <span className="status-premium px-2 py-1 rounded text-sm font-semibold animate-pulse-slow">
                      PREMIUM
                    </span>
                  )}
                  <div className="flex items-center space-x-2">
                    <img
                      src={session.user.image}
                      alt={session.user.name}
                      className="w-8 h-8 rounded-full ring-2 ring-gray-700 hover:ring-blue-500 transition-all duration-200"
                    />
                    <span className="hidden md:block text-sm">{session.user.name}</span>
                  </div>
                </div>
              </div>
            </div>
          </nav>
        )}

        {/* Main Content */}
        <main className="flex-1 min-h-screen">
          <div className="animate-fade-in">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-gray-900 border-t border-gray-800 py-8 mt-auto">
          <div className="container-responsive">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
              <div className="text-center md:text-left">
                <p className="text-gray-400">
                  &copy; 2025 Hits Manager. Powered by Discord integration.
                </p>
              </div>
              <div className="flex space-x-6 text-sm text-gray-400">
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Privacy Policy
                </a>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Terms of Service
                </a>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Support
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

