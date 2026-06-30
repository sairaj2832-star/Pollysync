const POLLEN_TYPES = [
  { key: "tree", label: "Tree", color: "bg-emerald-400" },
  { key: "grass", label: "Grass", color: "bg-amber-400" },
  { key: "weed", label: "Weed", color: "bg-red-400" },
];

export default function PollenBar({ pollen = {} }) {
  const maxLevel = 5;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
        Pollen Index
      </h3>
      {POLLEN_TYPES.map(({ key, label, color }) => {
        const level = Math.min(maxLevel, Math.max(0, pollen[key] || 0));
        return (
          <div key={key}>
            <div className="mb-1 flex justify-between text-sm">
              <span className="font-medium text-slate-700">{label}</span>
              <span className="text-slate-400">{level} / {maxLevel}</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100">
              <div
                className={`h-full rounded-full transition-all ${color}`}
                style={{ width: `${(level / maxLevel) * 100}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
