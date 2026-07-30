import { useSession, signIn, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import StatsCard from "../components/StatsCard";
import HitsList from "../components/HitsList";

export default function Dashboard() {
  const { data: session, status } = useSession();
  const [stats, setStats] = useState(null);
  const [hits, setHits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (session) {
      fetchUserData();
    }
  }, [session]);

  const fetchUserData = async () => {
    try {
      const [statsRes, hitsRes] = await Promise.all([
        fetch("/api/user/stats"),
        fetch("/api/user/hits")
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      if (hitsRes.ok) {
        const hitsData = await hitsRes.json();
        setHits(hitsData);
      }
    } catch (error) {
      console.error("Error fetching user data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (status === "loading") {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
        </div>
      </Layout>
    );
  }

  if (!session) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-screen text-center">
          <h1 className="text-4xl font-bold mb-8">Welcome to Hits Manager</h1>
          <p className="text-xl text-gray-300 mb-8">
            Manage your hits and view your stats with our Discord-integrated platform
          </p>
          <button
            onClick={() => signIn("discord")}
            className="bg-[#5865F2] hover:bg-[#4752C4] text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            Login with Discord
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Welcome back, {session.user.name}</h1>
            <p className="text-gray-400 mt-2">
              {session.user.premium ? "Premium User" : "Free User"} • 
              {session.user.autosecureEnabled ? " AutoSecure Enabled" : " AutoSecure Disabled"}
            </p>
          </div>
          <button
            onClick={() => signOut()}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
          >
            Sign Out
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatsCard
                  title="Total Hits"
                  value={stats.total}
                  icon="📊"
                  color="bg-blue-600"
                />
                <StatsCard
                  title="Completed"
                  value={stats.completed}
                  icon="✅"
                  color="bg-green-600"
                />
                <StatsCard
                  title="Pending"
                  value={stats.pending}
                  icon="⏳"
                  color="bg-yellow-600"
                />
                <StatsCard
                  title="Failed"
                  value={stats.failed}
                  icon="❌"
                  color="bg-red-600"
                />
              </div>
            )}

            {/* Hits List */}
            <div className="bg-gray-900 rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Your Hits</h2>
                <button
                  onClick={() => window.location.href = "/hits/new"}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                >
                  + New Hit
                </button>
              </div>
              <HitsList hits={hits} onUpdate={fetchUserData} />
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}

