import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
import { getPredictions } from "../lib/api";
import Card from "../components/Card";
import { MetricText, MetricTrend } from "../components/MetricDisplay";
import ChartWrapper, { exportChartData } from "../components/ChartWrapper";
import { EmptyState, DashboardSkeleton, ErrorState } from "../components/LoadingSkeleton";
import { FarmSelector } from "../components/ParameterForm";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function AnalyticsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const farmId = searchParams.get("farm_id") || "1";
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeRange, setTimeRange] = useState("3m");
  const [farms, setFarms] = useState([]);

  useEffect(() => {
    loadData();
  }, [farmId]);

  async function loadData() {
    try {
      setLoading(true);
      const data = await getPredictions(farmId);
      setPredictions(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load predictions");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <DashboardSkeleton />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  // Calculate metrics
  const sorted = [...predictions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  const avgPSI = sorted.length ? (sorted.reduce((sum, p) => sum + p.psi_score, 0) / sorted.length).toFixed(1) : 0;
  const maxPSI = sorted.length ? Math.max(...sorted.map((p) => p.psi_score)).toFixed(0) : 0;
  const minPSI = sorted.length ? Math.min(...sorted.map((p) => p.psi_score)).toFixed(0) : 0;

  // Count predictions by risk level
  const riskCounts = {
    high: sorted.filter((p) => p.risk_level === "High").length,
    medium: sorted.filter((p) => p.risk_level === "Medium").length,
    low: sorted.filter((p) => p.risk_level === "Low").length,
  };

  // Group by crop
  const cropStats = {};
  sorted.forEach((p) => {
    if (!cropStats[p.crop]) {
      cropStats[p.crop] = { count: 0, totalPSI: 0, avgPSI: 0 };
    }
    cropStats[p.crop].count += 1;
    cropStats[p.crop].totalPSI += p.psi_score;
    cropStats[p.crop].avgPSI = (cropStats[p.crop].totalPSI / cropStats[p.crop].count).toFixed(1);
  });

  // Chart data
  const labels = sorted.map((p) => {
    const d = new Date(p.created_at);
    return d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: "PSI Score",
        data: sorted.map((p) => p.psi_score),
        borderColor: "#006c49",
        backgroundColor: "rgba(0, 108, 73, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: sorted.map((p) =>
          p.psi_score >= 70 ? "#10b981" : p.psi_score >= 40 ? "#fea619" : "#b91a24"
        ),
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
        titleFont: { family: "Geist Sans", size: 12, weight: "600" },
        bodyFont: { family: "Inter", size: 12 },
        cornerRadius: 8,
        padding: 10,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { family: "Geist Sans", size: 11 } },
      },
      y: {
        grid: { color: "rgba(0,0,0,0.05)" },
        min: 0,
        max: 100,
        ticks: { font: { family: "Inter", size: 11 } },
      },
    },
  };

  function handleExport() {
    exportChartData(
      `PSI Analytics - Farm ${farmId}`,
      labels,
      chartData.datasets
    );
  }

  if (predictions.length === 0) {
    return (
      <EmptyState
        icon="analytics"
        title="No predictions yet"
        description="Run a prediction to start tracking your farm's pollination trends"
      />
    );
  }

  return (
    <div className="space-y-lg">
      {/* Header */}
      <div>
        <h1 className="font-display text-display text-on-surface">Analytics & Reports</h1>
        <p className="font-body-md text-body-md text-on-surface-variant mt-xs">
          Track PSI trends, crop performance, and pollination patterns over time
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
        <MetricText
          label="Average PSI"
          value={avgPSI}
          badge={avgPSI >= 70 ? "Good" : avgPSI >= 40 ? "Fair" : "Poor"}
          badge_color={
            avgPSI >= 70
              ? "bg-primary-container/20 text-primary"
              : avgPSI >= 40
                ? "bg-secondary/20 text-secondary"
                : "bg-tertiary/20 text-tertiary"
          }
          description="Across all predictions"
        />
        <MetricText
          label="Max PSI"
          value={maxPSI}
          description="Best prediction"
        />
        <MetricText
          label="Min PSI"
          value={minPSI}
          description="Lowest prediction"
        />
        <MetricText
          label="Total Predictions"
          value={sorted.length}
          description="Since you started"
        />
      </div>

      {/* Risk Distribution */}
      <Card header="Predictions by Risk Level">
        <div className="grid grid-cols-3 gap-md">
          <div className="text-center">
            <div className="text-4xl font-bold text-primary mb-md">{riskCounts.low}</div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Low Risk</p>
            <p className="text-sm text-on-surface-variant mt-xs">
              {((riskCounts.low / sorted.length) * 100).toFixed(0)}%
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-secondary mb-md">{riskCounts.medium}</div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Medium Risk</p>
            <p className="text-sm text-on-surface-variant mt-xs">
              {((riskCounts.medium / sorted.length) * 100).toFixed(0)}%
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-tertiary mb-md">{riskCounts.high}</div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">High Risk</p>
            <p className="text-sm text-on-surface-variant mt-xs">
              {((riskCounts.high / sorted.length) * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </Card>

      {/* PSI Trend Chart */}
      <ChartWrapper
        title="PSI Trend Over Time"
        legend={[{ label: "PSI Score", color: "#006c49" }]}
        onExport={handleExport}
      >
        <Line data={chartData} options={chartOptions} />
      </ChartWrapper>

      {/* Crop Performance */}
      <Card header="Performance by Crop">
        <div className="space-y-md">
          {Object.entries(cropStats).map(([crop, stats]) => (
            <div key={crop} className="flex items-center justify-between p-md bg-surface-container rounded-lg">
              <div>
                <p className="font-headline-sm text-headline-sm text-on-surface">{crop}</p>
                <p className="font-body-sm text-body-sm text-on-surface-variant mt-xs">
                  {stats.count} prediction{stats.count !== 1 ? "s" : ""}
                </p>
              </div>
              <div className="text-right">
                <p className="font-headline-md text-headline-md text-on-surface">
                  {stats.avgPSI}
                </p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">avg PSI</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Predictions Table */}
      <Card header="Recent Predictions">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline-variant">
                <th className="text-left py-md px-md font-label-md text-label-md text-on-surface-variant">
                  Date
                </th>
                <th className="text-left py-md px-md font-label-md text-label-md text-on-surface-variant">
                  Crop
                </th>
                <th className="text-left py-md px-md font-label-md text-label-md text-on-surface-variant">
                  PSI Score
                </th>
                <th className="text-left py-md px-md font-label-md text-label-md text-on-surface-variant">
                  Risk Level
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((pred, i) => {
                const scoreColor =
                  pred.psi_score >= 70 ? "text-primary" : pred.psi_score >= 40 ? "text-secondary" : "text-tertiary";
                const riskBg =
                  pred.risk_level === "Low"
                    ? "bg-primary-container/20 text-primary"
                    : pred.risk_level === "Medium"
                      ? "bg-secondary/20 text-secondary"
                      : "bg-tertiary/20 text-tertiary";

                return (
                  <tr key={i} className="border-b border-outline-variant/30 hover:bg-surface-container/50">
                    <td className="py-md px-md font-body-sm text-on-surface">
                      {new Date(pred.created_at).toLocaleDateString("en-IN")}
                    </td>
                    <td className="py-md px-md font-body-sm text-on-surface">{pred.crop}</td>
                    <td className={`py-md px-md font-headline-sm ${scoreColor}`}>{pred.psi_score}</td>
                    <td className="py-md px-md">
                      <span className={`px-md py-xs rounded-full font-label-xs text-label-xs font-bold ${riskBg}`}>
                        {pred.risk_level}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
