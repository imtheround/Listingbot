import { useState } from "react";

export default function HitsList({ hits, onUpdate }) {
  const [selectedHit, setSelectedHit] = useState(null);

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "bg-green-600";
      case "pending":
        return "bg-yellow-600";
      case "failed":
        return "bg-red-600";
      default:
        return "bg-gray-600";
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

  const updateHitStatus = async (hitId, newStatus) => {
    try {
      const response = await fetch(`/api/hits/${hitId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error("Error updating hit status:", error);
    }
  };

  if (!hits || hits.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 text-lg">No hits found</p>
        <p className="text-gray-500 mt-2">Create your first hit to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {hits.map((hit) => (
        <div
          key={hit.id}
          className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors duration-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h3 className="font-semibold text-lg">{hit.target}</h3>
                <span
                  className={`${getStatusColor(
                    hit.status
                  )} text-white px-2 py-1 rounded text-sm font-medium`}
                >
                  {hit.status.toUpperCase()}
                </span>
                <span className="text-gray-400 text-sm">{hit.hit_type}</span>
              </div>
              <p className="text-gray-400 mt-1">
                Created: {formatDate(hit.created_at)}
                {hit.completed_at && (
                  <span className="ml-4">
                    Completed: {formatDate(hit.completed_at)}
                  </span>
                )}
              </p>
              {hit.notes && (
                <p className="text-gray-300 mt-2 text-sm">{hit.notes}</p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {hit.status === "pending" && (
                <>
                  <button
                    onClick={() => updateHitStatus(hit.id, "completed")}
                    className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                  >
                    Complete
                  </button>
                  <button
                    onClick={() => updateHitStatus(hit.id, "failed")}
                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                  >
                    Mark Failed
                  </button>
                </>
              )}
              <button
                onClick={() =>
                  setSelectedHit(selectedHit === hit.id ? null : hit.id)
                }
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                  />
                </svg>
              </button>
            </div>
          </div>

          {selectedHit === hit.id && (
            <div className="mt-4 pt-4 border-t border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Hit ID:</span>
                  <span className="ml-2">{hit.id}</span>
                </div>
                <div>
                  <span className="text-gray-400">Type:</span>
                  <span className="ml-2">{hit.hit_type}</span>
                </div>
                <div>
                  <span className="text-gray-400">Status:</span>
                  <span className="ml-2">{hit.status}</span>
                </div>
                <div>
                  <span className="text-gray-400">Target:</span>
                  <span className="ml-2">{hit.target}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

