export default function NDVICard({ value = 0 }) {
  const clamped = Math.max(0, Math.min(1, value));
  const health = clamped >= 0.7 ? "Healthy" : clamped >= 0.4 ? "Moderate" : "Poor";
  const color = clamped >= 0.7 ? "text-emerald-600"
    : clamped >= 0.4 ? "text-amber-600"
    : "text-red-600";

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-soft">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
        Crop Health (NDVI)
      </h3>
      <p className={`mt-3 text-5xl font-black ${color}`}>
        {clamped.toFixed(2)}
      </p>
      <p className="mt-1 text-lg font-semibold text-slate-700">{health}</p>
      <p className="mt-2 text-xs text-slate-400">Based on satellite imagery</p>
    </div>
  );
}
