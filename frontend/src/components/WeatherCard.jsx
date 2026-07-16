const CONFIG = {
  temperature: { icon: "thermostat", bg: "bg-secondary-container/20", color: "text-secondary-container" },
  humidity: { icon: "water_drop", bg: "bg-primary-container/20", color: "text-primary-container" },
  rainfall: { icon: "rainy", bg: "bg-primary-container/15", color: "text-primary" },
  wind: { icon: "air", bg: "bg-surface-container-high", color: "text-on-surface-variant" },
};

export default function WeatherCard({ label, value, unit, icon = "temperature", trend }) {
  const cfg = CONFIG[icon] || CONFIG.temperature;

  function TrendIcon() {
    if (trend === undefined || trend === null) return null;
    if (trend > 0) {
      return (
        <span className="text-tertiary text-xs flex items-center">
          <span className="material-symbols-outlined text-[14px]">arrow_upward</span>
          {trend}{unit}
        </span>
      );
    }
    if (trend < 0) {
      return (
        <span className="text-primary text-xs flex items-center">
          <span className="material-symbols-outlined text-[14px]">arrow_downward</span>
          {Math.abs(trend)}{unit}
        </span>
      );
    }
    return (
      <span className="text-on-surface-variant text-xs flex items-center">
        <span className="material-symbols-outlined text-[14px]">horizontal_rule</span>
        {trend}
      </span>
    );
  }

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-sm flex items-start gap-md">
      <div className={`${cfg.bg} ${cfg.color} p-sm rounded-md`}>
        <span className="material-symbols-outlined">{cfg.icon}</span>
      </div>
      <div>
        <span className="font-label-sm text-label-sm text-on-surface-variant block">{label}</span>
        <div className="flex items-baseline gap-xs">
          <span className="font-headline-md text-headline-md text-on-surface">
            {value}{unit}
          </span>
          <TrendIcon />
        </div>
      </div>
    </div>
  );
}
