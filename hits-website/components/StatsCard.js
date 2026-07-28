export default function StatsCard({ title, value, icon, color = "bg-gray-600" }) {
  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`${color} rounded-full p-3 text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

