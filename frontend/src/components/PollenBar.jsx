const POLLEN_TYPES = [
  { key: "tree", label: "Tree", color: "bg-primary" },
  { key: "grass", label: "Grass", color: "bg-secondary" },
  { key: "weed", label: "Weed", color: "bg-tertiary" },
];

export default function PollenBar({ pollen = {} }) {
  const maxLevel = 5;

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)] h-full">
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md">Pollen Index</h3>
      <div className="space-y-md">
        {POLLEN_TYPES.map(({ key, label, color }) => {
          const level = Math.min(maxLevel, Math.max(0, pollen[key] || 0));
          return (
            <div key={key}>
              <div className="flex justify-between font-body-sm text-body-sm mb-xs">
                <span className="text-on-surface font-medium">{label}</span>
                <span className="text-on-surface-variant">{level} / {maxLevel}</span>
              </div>
              <div className="h-3 w-full bg-surface-variant rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${color}`}
                  style={{ width: `${(level / maxLevel) * 100}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
