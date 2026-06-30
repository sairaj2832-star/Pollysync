export default function PSIgauge({ score = 0, size = "lg" }) {
  const clamped = Math.max(0, Math.min(100, score));
  const color =
    clamped >= 70 ? "text-emerald-600 stroke-emerald-500"
    : clamped >= 40 ? "text-amber-600 stroke-amber-500"
    : "text-red-600 stroke-red-500";

  const radius = size === "sm" ? 48 : 64;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={radius * 2.5} height={radius * 2.5} className="-rotate-90">
        <circle
          cx={radius * 1.25}
          cy={radius * 1.25}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={12}
        />
        <circle
          cx={radius * 1.25}
          cy={radius * 1.25}
          r={radius}
          fill="none"
          className={color}
          strokeWidth={12}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-5xl font-black">{clamped}</span>
        <span className="text-sm font-semibold text-slate-500">/ 100</span>
      </div>
      <span className="text-sm font-bold uppercase tracking-wider text-slate-500">
        Pollination Suitability
      </span>
    </div>
  );
}
