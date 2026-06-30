export default function WeatherCard({ label, value, unit, icon, trend }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-soft">
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        {trend && (
          <span className={`text-sm font-bold ${trend > 0 ? "text-emerald-500" : "text-red-500"}`}>
            {trend > 0 ? "↑" : "↓"}
          </span>
        )}
      </div>
      <p className="mt-3 text-2xl font-black text-slate-900">
        {value}
        <span className="ml-1 text-sm font-medium text-slate-500">{unit}</span>
      </p>
      <p className="mt-1 text-sm text-slate-500">{label}</p>
    </div>
  );
}
