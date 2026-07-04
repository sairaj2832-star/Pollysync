export default function NDVICard({ value = 0 }) {
  const clamped = Math.max(0, Math.min(1, value));
  const health = clamped >= 0.7 ? "Healthy" : clamped >= 0.4 ? "Moderate" : "Poor";
  const color = clamped >= 0.7 ? "text-primary"
    : clamped >= 0.4 ? "text-secondary"
    : "text-tertiary";
  const badgeBg = clamped >= 0.7 ? "bg-primary-container/10 text-primary"
    : clamped >= 0.4 ? "bg-secondary/10 text-secondary"
    : "bg-tertiary/10 text-tertiary";

  const sparkPoints = "M0,25 L10,22 L20,24 L30,18 L40,15 L50,19 L60,12 L70,10 L80,5 L90,8 L100,2";

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col justify-between shadow-[0_1px_3px_rgba(0,0,0,0.05)] h-full">
      <div className="flex justify-between items-start mb-md">
        <h3 className="font-headline-sm text-headline-sm text-on-surface">Crop Health (NDVI)</h3>
        <span className={`${badgeBg} px-sm py-xs rounded-full font-label-sm text-label-sm`}>
          {health}
        </span>
      </div>
      <div>
        <span className={`font-display text-display block mb-xs ${color}`}>
          {clamped.toFixed(2)}
        </span>
        <span className="font-body-sm text-body-sm text-on-surface-variant">
          Average index across all zones. Up 0.04 from last week.
        </span>
      </div>
      <div className="mt-md h-16 w-full">
        <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 30">
          <path d={sparkPoints} fill="none" stroke="#10B981" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d={`${sparkPoints} L100,30 L0,30 Z`} fill="url(#sparkGradient)" opacity="0.2" />
          <defs>
            <linearGradient id="sparkGradient" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
}
