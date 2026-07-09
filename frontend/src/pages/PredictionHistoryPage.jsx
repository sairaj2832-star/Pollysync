import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFarms, getPredictions } from "../lib/api";

const RISK_STYLES = {
  low: "bg-primary-container/10 text-primary",
  medium: "bg-secondary/10 text-secondary",
  high: "bg-tertiary/10 text-tertiary",
};

export default function PredictionHistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        setError("");
        const farms = await getFarms();
        const safeFarms = Array.isArray(farms) ? farms : [];
        const predictionGroups = await Promise.all(
          safeFarms.map(async (farm) => {
            const rows = await getPredictions(farm.id);
            const safeRows = Array.isArray(rows) ? rows : [];
            return safeRows.map((prediction) => ({
              ...prediction,
              farm,
            }));
          })
        );
        const flattened = predictionGroups
          .flat()
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setPredictions(flattened);
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to load prediction history");
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  const filtered = filter === "all"
    ? predictions
    : predictions.filter((p) => (p.risk_level || "").toLowerCase() === filter);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <p className="font-body-md text-tertiary">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1100px] mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-md mb-xl">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Prediction History</h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-xs">View all your past pollination forecasts.</p>
        </div>
        <Link
          to="/predict"
          className="inline-flex items-center justify-center gap-sm bg-primary text-on-primary font-label-md text-label-md px-lg py-sm rounded-lg hover:bg-[#005a3c] transition-colors"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Prediction
        </Link>
      </div>

      <div className="flex gap-sm mb-lg overflow-x-auto pb-2">
        {["all", "low", "medium", "high"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-md py-xs rounded-full font-label-sm text-label-sm whitespace-nowrap transition-colors ${
              filter === f
                ? "bg-primary text-on-primary"
                : "bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest"
            }`}
          >
            {f === "all" ? "All" : `${f.charAt(0).toUpperCase() + f.slice(1)} Risk`}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-3xl text-center">
          <span className="material-symbols-outlined text-6xl text-on-surface-variant/30 mb-lg">history</span>
          <h2 className="font-headline-sm text-headline-sm text-on-surface mb-sm">No predictions found</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mb-xl max-w-md">
            {filter === "all"
              ? "You haven't created any predictions yet. Start by selecting a crop and location."
              : `No ${filter} predictions found. Try a different filter.`}
          </p>
          <Link
            to="/predict"
            className="bg-primary text-on-primary font-label-md text-label-md px-lg py-sm rounded-lg hover:bg-[#005a3c] transition-colors"
          >
            Create First Prediction
          </Link>
        </div>
      ) : (
        <div className="space-y-md">
          {filtered.map((p) => (
            <div
              key={p.id}
              className="bg-surface border border-outline-variant rounded-xl p-lg hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-md">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-sm mb-xs">
                    <span className="material-symbols-outlined text-primary text-[20px]">agriculture</span>
                    <span className="font-headline-sm text-headline-sm text-on-surface truncate">
                      {p.farm?.name || "Farm"}
                    </span>
                    <span className={`px-sm py-[2px] rounded-full font-label-sm text-label-sm ${RISK_STYLES[(p.risk_level || "high").toLowerCase()] || RISK_STYLES.high}`}>
                      {p.risk_level || "Unknown"} Risk
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-md text-body-sm text-on-surface-variant">
                    <span className="flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[16px]">calendar_today</span>
                      {p.created_at ? new Date(p.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "--"}
                    </span>
                    <span className="flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[16px]">eco</span>
                      {p.farm?.crop_type || "Crop"}
                    </span>
                    {p.psi_score != null && (
                      <span className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-[16px]">speed</span>
                        PSI: {p.psi_score}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-sm">
                  {p.risk_level && (
                    <span className={`px-md py-xs rounded-full font-label-sm text-label-sm ${
                      p.risk_level === "Low"
                        ? "bg-primary-container/10 text-primary"
                        : p.risk_level === "Medium"
                        ? "bg-secondary/10 text-secondary"
                        : "bg-tertiary/10 text-tertiary"
                    }`}>
                      {p.risk_level} Risk
                    </span>
                  )}
                </div>
              </div>
              {p.recommendation && (
                <div className="mt-md pt-md border-t border-outline-variant/50">
                  <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2">
                    {p.recommendation.replace(/[#*\n]/g, " ").slice(0, 150)}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
