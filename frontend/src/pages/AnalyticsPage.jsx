import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
import { getPredictions } from "../lib/api";
import { useFarm } from "../context/FarmContext";
import ChartWrapper, { exportChartData } from "../components/ChartWrapper";
import { EmptyState, DashboardSkeleton, ErrorState } from "../components/LoadingSkeleton";
import FarmSelector from "../components/FarmSelector";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

const ranges = { "7D": 7, "30D": 30, Season: 120, All: Infinity };

export default function AnalyticsPage() {
  const [params, setParams] = useSearchParams();
  const { farms, selectedFarm, selectedFarmId, loadingFarms, selectFarm } = useFarm();
  const requestedFarmId = params.get("farm_id");
  const farmId = requestedFarmId || selectedFarmId;
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [range, setRange] = useState("30D");
  const [tab, setTab] = useState("trends");

  useEffect(() => {
    if (requestedFarmId) selectFarm(requestedFarmId);
  }, [requestedFarmId, selectFarm]);

  useEffect(() => {
    if (loadingFarms) return;
    if (!farmId) {
      setPredictions([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    getPredictions(farmId)
      .then((data) => setPredictions(Array.isArray(data) ? data : []))
      .catch((err) => setError(err?.response?.data?.detail || "Failed to load analytics"))
      .finally(() => setLoading(false));
  }, [farmId, loadingFarms]);

  const filtered = useMemo(() => {
    const cutoff = Date.now() - ranges[range] * 86400000;
    return [...predictions]
      .filter((item) => range === "All" || new Date(item.created_at).getTime() >= cutoff)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  }, [predictions, range]);

  const labels = filtered.map((item) => new Date(item.created_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }));
  const scores = filtered.map((item) => item.psi_score);
  const ndviScores = filtered.map((item) => item.ndvi_value ?? null);
  const average = scores.length ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1) : "-";
  const delta = scores.length > 1 ? (scores.at(-1) - scores[0]).toFixed(0) : 0;
  const highRisk = filtered.filter((item) => item.risk_level === "High").length;
  const lowRisk = filtered.filter((item) => item.risk_level === "Low").length;
  const mediumRisk = filtered.length - lowRisk - highRisk;

  const chartData = {
    labels,
    datasets: [
      {
        label: "PSI score",
        data: scores,
        borderColor: "#006c49",
        backgroundColor: "rgba(0,108,73,.12)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointBackgroundColor: scores.map((score) => score >= 70 ? "#10b981" : score >= 40 ? "#fea619" : "#b91a24"),
      },
      {
        label: "NDVI x100",
        data: ndviScores.map((value) => value == null ? null : Math.round(value * 100)),
        borderColor: "#4f46e5",
        backgroundColor: "rgba(79,70,229,.08)",
        fill: false,
        tension: 0.35,
        pointRadius: 3,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#342f2b",
        padding: 10,
        callbacks: {
          label: (context) => context.dataset.label === "NDVI x100" ? ` NDVI: ${(context.parsed.y / 100).toFixed(2)}` : ` PSI: ${context.parsed.y}/100`,
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
      y: { min: 0, max: 100, grid: { color: "rgba(108,122,113,.18)" }, ticks: { stepSize: 20 } },
    },
  };

  function changeFarm(id) {
    selectFarm(id);
    setParams({ farm_id: String(id) }, { replace: true });
  }

  if (loading || loadingFarms) return <DashboardSkeleton />;
  if (error) return <ErrorState error={error} onRetry={() => window.location.reload()} />;

  if (!farmId || predictions.length === 0) {
    return (
      <div className="space-y-lg">
        {farms.length ? <div className="max-w-xs"><FarmSelector farms={farms} selectedFarmId={farmId} onSelectFarm={changeFarm} showCreateAction={false} /></div> : null}
        <EmptyState
          icon="analytics"
          title={farms.length ? "No predictions in this farm" : "No farm selected"}
          description="Run a prediction from a farm workspace to build trend and risk analytics."
        />
      </div>
    );
  }

  return (
    <div className="space-y-lg pb-lg">
      <header className="flex flex-col gap-md lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-label-sm text-primary font-bold uppercase tracking-wide">Farm intelligence</p>
          <h1 className="mt-1 font-display text-display text-on-surface">Analytics</h1>
          <p className="mt-1 text-body-md text-on-surface-variant">Track PSI movement and risk concentration for the selected farm.</p>
        </div>
        <div className="min-w-[220px]"><FarmSelector farms={farms} selectedFarmId={farmId} onSelectFarm={changeFarm} showCreateAction={false} /></div>
      </header>

      <div className="sticky top-0 z-20 -mx-md border-y border-outline-variant bg-background/95 px-md py-sm backdrop-blur sm:static sm:mx-0 sm:rounded-xl sm:border sm:bg-surface sm:p-sm">
        <div className="flex gap-xs overflow-x-auto" role="tablist" aria-label="Analytics time range">
          {Object.keys(ranges).map((item) => (
            <button key={item} onClick={() => setRange(item)} className={`min-h-11 shrink-0 rounded-lg px-md text-label-sm ${range === item ? "bg-primary text-on-primary font-bold" : "text-on-surface-variant hover:bg-surface-container"}`}>
              {item}
            </button>
          ))}
        </div>
      </div>

      <section className="grid grid-cols-2 gap-sm lg:grid-cols-4">
        {[["Average PSI", average, Number(average) >= 70 ? "Favorable" : "Needs attention"], ["Trend", `${delta > 0 ? "+" : ""}${delta}`, "vs. first result"], ["High-risk days", highRisk, "in selected range"], ["Predictions", filtered.length, `${lowRisk} low-risk`]].map(([label, value, hint]) => (
          <article key={label} className="rounded-xl border border-outline-variant bg-surface p-md shadow-sm">
            <p className="text-label-sm text-on-surface-variant">{label}</p>
            <p className="mt-xs text-headline-lg font-headline-lg text-on-surface">{value}</p>
            <p className="mt-1 text-body-sm text-on-surface-variant">{hint}</p>
          </article>
        ))}
      </section>

      <div className="flex gap-xs overflow-x-auto border-b border-outline-variant" role="tablist" aria-label="Analytics sections">
        {[["trends", "Trends"], ["risk", "Risk"]].map(([id, label]) => (
          <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)} className={`min-h-11 shrink-0 border-b-2 px-md text-label-md ${tab === id ? "border-primary text-primary font-bold" : "border-transparent text-on-surface-variant"}`}>
            {label}
          </button>
        ))}
      </div>

      {tab === "trends" && (
        <ChartWrapper
          title="PSI and NDVI Trend"
          legend={[{ label: "PSI score", color: "#006c49" }, { label: "NDVI x100", color: "#4f46e5" }]}
          onExport={() => exportChartData(`Trends-${selectedFarm?.name || farmId}-${range}`, labels, chartData.datasets)}
        >
          <Line data={chartData} options={chartOptions} />
        </ChartWrapper>
      )}

      {tab === "risk" && (
        <article className="rounded-xl border border-outline-variant bg-surface p-lg">
          <h2 className="text-headline-sm font-headline-sm text-on-surface">Risk distribution</h2>
          <p className="mt-xs text-body-md text-on-surface-variant">{highRisk ? `${highRisk} high-risk prediction${highRisk > 1 ? "s" : ""} need closer planning in this range.` : "No high-risk predictions in this range."}</p>
          <div className="mt-lg flex h-5 overflow-hidden rounded-full bg-surface-container-high">
            {[["Low", lowRisk, "bg-primary"], ["Medium", mediumRisk, "bg-secondary"], ["High", highRisk, "bg-tertiary"]].map(([label, count, color]) => Number(count) > 0 && <div key={label} title={`${label}: ${count}`} className={color} style={{ width: `${(Number(count) / filtered.length) * 100}%` }} />)}
          </div>
          <div className="mt-md grid grid-cols-3 text-center">
            {[["Low", lowRisk], ["Medium", mediumRisk], ["High", highRisk]].map(([label, count]) => (
              <div key={label}>
                <p className="text-headline-md font-headline-md text-on-surface">{count}</p>
                <p className="text-body-sm text-on-surface-variant">{label} risk</p>
              </div>
            ))}
          </div>
        </article>
      )}
    </div>
  );
}
