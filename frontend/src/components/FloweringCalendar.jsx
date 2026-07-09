export default function FloweringCalendar({ start, end, confidence = 0 }) {
  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)] h-full">
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md">Predicted Flowering Window</h3>
      <div className="flex items-center gap-md">
        <div className="flex-1 bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-md text-center">
          <span className="font-label-sm text-label-sm text-on-surface-variant block">Start</span>
          <span className="font-headline-md text-headline-md text-primary mt-xs block">{start || "--"}</span>
        </div>
        <span className="material-symbols-outlined text-outline">arrow_forward</span>
        <div className="flex-1 bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-md text-center">
          <span className="font-label-sm text-label-sm text-on-surface-variant block">End</span>
          <span className="font-headline-md text-headline-md text-primary mt-xs block">{end || "--"}</span>
        </div>
      </div>
      <div className="mt-md flex items-center justify-between">
        <span className="rounded-full bg-primary-container/10 text-primary px-md py-xs font-label-sm text-label-sm">
          {Math.round(confidence * 100)}% confident
        </span>
        <span className="font-body-sm text-body-sm text-on-surface-variant">
          {start && end ? `${Math.ceil((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24))} day window` : ""}
        </span>
      </div>
      <div className="mt-md h-2 w-full bg-surface-variant rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-secondary to-primary transition-all duration-700"
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
    </div>
  );
}
