export default function PSIgauge({ score = 0, size = "lg" }) {
  const clamped = Math.max(0, Math.min(100, score));
  const circumference = 283;
  const offset = circumference - (clamped / 100) * circumference;
  const color =
    clamped >= 70 ? "#10b981"
    : clamped >= 40 ? "#fea619"
    : "#b91a24";

  return (
    <div className="relative w-40 h-40 flex items-center justify-center my-md">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" fill="none" r="45" stroke="#E2E8F0" strokeWidth="8" />
        <circle
          cx="50"
          cy="50"
          fill="none"
          r="45"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-in-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-display text-on-surface">{clamped}</span>
        <span className="font-label-sm text-label-sm text-on-surface-variant">/ 100</span>
      </div>
    </div>
  );
}
