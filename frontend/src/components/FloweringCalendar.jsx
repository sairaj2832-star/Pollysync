export default function FloweringCalendar({ start, end, confidence = 0 }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-soft">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
        Predicted Flowering Window
      </h3>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-2xl font-black text-leaf-700">{start}</span>
        <span className="text-slate-400">→</span>
        <span className="text-2xl font-black text-leaf-700">{end}</span>
      </div>
      <div className="mt-3 flex items-center gap-3">
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
          {Math.round(confidence * 100)}% confident
        </span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-gradient-to-r from-pollen to-leaf-500"
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
    </div>
  );
}
