/**
 * MetricDisplay component with multiple variants
 * Supports: gauge (circular), bar (linear), trend (comparison), text (simple value)
 */
import Card from "./Card";

export function MetricGauge({ score = 0, label = "", description = "" }) {
  const clamped = Math.max(0, Math.min(100, score));
  const circumference = 283;
  const offset = circumference - (clamped / 100) * circumference;
  const color =
    clamped >= 70
      ? "#10b981"
      : clamped >= 40
        ? "#fea619"
        : "#b91a24";

  return (
    <Card header={label}>
      <div className="relative w-40 h-40 flex items-center justify-center mx-auto">
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
      {description && (
        <p className="text-center font-body-sm text-body-sm text-on-surface-variant mt-md">
          {description}
        </p>
      )}
    </Card>
  );
}

export function MetricBar({ value = 0, label = "", max = 100, description = "", unit = "%" }) {
  const clamped = Math.max(0, Math.min(max, value));
  const percentage = (clamped / max) * 100;
  const color =
    percentage >= 70
      ? "bg-primary"
      : percentage >= 40
        ? "bg-secondary"
        : "bg-tertiary";

  return (
    <Card header={label}>
      <div className="space-y-sm">
        <div className="flex justify-between items-baseline">
          <span className="font-headline-md text-headline-md text-on-surface">
            {clamped.toFixed(1)}{unit}
          </span>
          <span className="font-label-sm text-label-sm text-on-surface-variant">
            max {max}{unit}
          </span>
        </div>
        <div className="w-full bg-surface-container rounded-full overflow-hidden h-2">
          <div className={`${color} h-full transition-all duration-500`} style={{ width: `${percentage}%` }} />
        </div>
        {description && (
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-sm">{description}</p>
        )}
      </div>
    </Card>
  );
}

export function MetricTrend({
  label = "",
  value = 0,
  trend = 0,
  description = "",
  unit = "",
  icon = "trending_up",
}) {
  const isPositive = trend > 0;
  const trendColor = isPositive ? "text-primary" : "text-tertiary";
  const trendIcon = isPositive ? "trending_up" : "trending_down";

  return (
    <Card header={label}>
      <div className="space-y-sm">
        <div className="flex justify-between items-center">
          <span className="font-headline-md text-headline-md text-on-surface">
            {value.toFixed(2)}{unit}
          </span>
          <div className={`flex items-center gap-xs ${trendColor}`}>
            <span className="material-symbols-outlined">{trendIcon}</span>
            <span className="font-label-sm text-label-sm">{Math.abs(trend).toFixed(1)}%</span>
          </div>
        </div>
        {description && (
          <p className="font-body-sm text-body-sm text-on-surface-variant">{description}</p>
        )}
      </div>
    </Card>
  );
}

export function MetricText({
  label = "",
  value = "—",
  description = "",
  badge,
  badge_color = "bg-primary-container/10 text-primary",
}) {
  return (
    <Card
      header={label}
      badge={
        badge ? (
          <span className={`${badge_color} px-sm py-xs rounded-full font-label-sm text-label-sm`}>
            {badge}
          </span>
        ) : null
      }
    >
      <div className="space-y-sm">
        <span className="font-headline-md text-headline-md text-on-surface block">{value}</span>
        {description && (
          <p className="font-body-sm text-body-sm text-on-surface-variant">{description}</p>
        )}
      </div>
    </Card>
  );
}
