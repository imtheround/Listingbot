import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import StatsCard from "../../components/StatsCard";

export default function AdminDashboard() {
  const router = useRouter();
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [hits, setHits] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch("/api/admin/verify");
      if (response.ok) {
        const data = await response.json();
        setAdmin(data.admin);
        await fetchDashboardData();
      } else {
        router.push("/admin/login");
      }
    } catch (error) {
      router.push("/admin/login");
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const [statsRes, usersRes, hitsRes] = await Promise.all([
        fetch("/api/admin/stats"),
        fetch("/api/admin/users"),
        fetch("/api/admin/hits")
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData);
      }

      if (hitsRes.ok) {
        const hitsData = await hitsRes.json();
        setHits(hitsData);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
  };

  const logout = async () => {
    try {
      await fetch("/api/admin/logout", { method: "POST" });
      router.push("/admin/login");
    } catch (error) {
      router.push("/admin/login");
    }
  };

  const toggleUserPremium = async (userId, isPremium) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ premium: !isPremium }),
      });

      if (response.ok) {
        await fetchDashboardData();
      }
    } catch (error) {
      console.error("Error updating user:", error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard - Hits Manager">
      <div className="min-h-screen bg-black">
        {/* Admin Navigation */}
        <nav className="bg-gray-900 border-b border-gray-800">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-8">
                <h1 className="text-xl font-bold text-red-400">Admin Panel</h1>
                <div className="flex space-x-6">
                  <button
                    onClick={() => setActiveTab("overview")}
                    className={`${
                      activeTab === "overview"
                        ? "text-white border-b-2 border-red-400"
                        : "text-gray-300 hover:text-white"
                    } transition-colors duration-200 pb-4`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab("users")}
                    className={`${
                      activeTab === "users"
                        ? "text-white border-b-2 border-red-400"
                        : "text-gray-300 hover:text-white"
                    } transition-colors duration-200 pb-4`}
                  >
                    Users
                  </button>
                  <button
                    onClick={() => setActiveTab("hits")}
                    className={`${
                      activeTab === "hits"
                        ? "text-white border-b-2 border-red-400"
                        : "text-gray-300 hover:text-white"
                    } transition-colors duration-200 pb-4`}
                  >
                    All Hits
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <span className="text-gray-300">Welcome, {admin?.username}</span>
                <button
                  onClick={logout}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="container mx-auto px-4 py-8">
          {activeTab === "overview" && (
            <div>
              <h2 className="text-3xl font-bold mb-8">Dashboard Overview</h2>
              
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                  <StatsCard
                    title="Total Users"
                    value={stats.totalUsers}
                    icon="👥"
                    color="bg-blue-600"
                  />
                  <StatsCard
                    title="Premium Users"
                    value={stats.premiumUsers}
                    icon="⭐"
                    color="bg-yellow-600"
                  />
                  <StatsCard
                    title="Active Users"
                    value={stats.activeUsers}
                    icon="🟢"
                    color="bg-green-600"
                  />
                  <StatsCard
                    title="Total Hits"
                    value={stats.totalHits}
                    icon="🎯"
                    color="bg-purple-600"
                  />
                  <StatsCard
                    title="Completed Hits"
                    value={stats.completedHits}
                    icon="✅"
                    color="bg-green-600"
                  />
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-gray-900 rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-4">Recent Users</h3>
                  <div className="space-y-3">
                    {users.slice(0, 5).map((user) => (
                      <div key={user.id} className="flex items-center justify-between p-3 bg-gray-800 rounded">
                        <div>
                          <span className="font-medium">{user.user_id}</span>
                          {user.premium === "true" && (
                            <span className="ml-2 bg-yellow-600 text-black px-2 py-1 rounded text-xs">
                              PREMIUM
                            </span>
                          )}
                        </div>
                        <span className="text-gray-400 text-sm">{user.domain}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-6">
                  <h3 className="text-xl font-bold mb-4">Recent Hits</h3>
                  <div className="space-y-3">
                    {hits.slice(0, 5).map((hit) => (
                      <div key={hit.id} className="flex items-center justify-between p-3 bg-gray-800 rounded">
                        <div>
                          <span className="font-medium">{hit.target}</span>
                          <span className="ml-2 text-gray-400 text-sm">{hit.hit_type}</span>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          hit.status === "completed" ? "bg-green-600" :
                          hit.status === "pending" ? "bg-yellow-600" : "bg-red-600"
                        }`}>
                          {hit.status.toUpperCase()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "users" && (
            <div>
              <h2 className="text-3xl font-bold mb-8">User Management</h2>
              
              <div className="bg-gray-900 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          User ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Premium
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Domain
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          AutoSecure
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {users.map((user) => (
                        <tr key={user.id} className="hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                            {user.user_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {user.premium === "true" ? (
                              <span className="bg-yellow-600 text-black px-2 py-1 rounded text-xs">
                                PREMIUM
                              </span>
                            ) : (
                              <span className="bg-gray-600 text-white px-2 py-1 rounded text-xs">
                                FREE
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {user.domain}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {user.autosecureEnabled ? "Enabled" : "Disabled"}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => toggleUserPremium(user.user_id, user.premium === "true")}
                              className={`${
                                user.premium === "true"
                                  ? "bg-red-600 hover:bg-red-700"
                                  : "bg-green-600 hover:bg-green-700"
                              } text-white px-3 py-1 rounded text-xs transition-colors duration-200`}
                            >
                              {user.premium === "true" ? "Remove Premium" : "Make Premium"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "hits" && (
            <div>
              <h2 className="text-3xl font-bold mb-8">All Hits</h2>
              
              <div className="bg-gray-900 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Target
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                          Created
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {hits.map((hit) => (
                        <tr key={hit.id} className="hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                            {hit.target}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {hit.hit_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {hit.user_id}
                            {hit.premium === "true" && (
                              <span className="ml-2 bg-yellow-600 text-black px-1 py-0.5 rounded text-xs">
                                P
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            <span className={`px-2 py-1 rounded text-xs ${
                              hit.status === "completed" ? "bg-green-600" :
                              hit.status === "pending" ? "bg-yellow-600" : "bg-red-600"
                            }`}>
                              {hit.status.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {formatDate(hit.created_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

