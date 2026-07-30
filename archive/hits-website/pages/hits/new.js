import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";

export default function NewHit() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [formData, setFormData] = useState({
    target: "",
    hit_type: "",
    notes: "",
  });
  const [loading, setLoading] = useState(false);

  const hitTypes = [
    "Website",
    "API",
    "Database",
    "Server",
    "Application",
    "Network",
    "Other"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("/api/user/hits", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        router.push("/");
      } else {
        alert("Error creating hit");
      }
    } catch (error) {
      console.error("Error creating hit:", error);
      alert("Error creating hit");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
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
    router.push("/");
    return null;
  }

  return (
    <Layout title="New Hit - Hits Manager">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center mb-8">
            <button
              onClick={() => router.back()}
              className="text-gray-400 hover:text-white mr-4"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-3xl font-bold">Create New Hit</h1>
          </div>

          <div className="bg-gray-900 rounded-lg p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="target" className="block text-sm font-medium text-gray-300 mb-2">
                  Target *
                </label>
                <input
                  type="text"
                  id="target"
                  name="target"
                  value={formData.target}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter target name or URL"
                />
              </div>

              <div>
                <label htmlFor="hit_type" className="block text-sm font-medium text-gray-300 mb-2">
                  Hit Type *
                </label>
                <select
                  id="hit_type"
                  name="hit_type"
                  value={formData.hit_type}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select hit type</option>
                  {hitTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-300 mb-2">
                  Notes
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Additional notes or details about this hit"
                />
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => router.back()}
                  className="px-6 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Creating..." : "Create Hit"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}

