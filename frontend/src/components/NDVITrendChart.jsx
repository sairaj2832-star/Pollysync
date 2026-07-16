import { useEffect, useState } from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
import { getPredictions } from "../lib/api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function NDVITrendChart({ farmId }) {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farmId) return;
    setError("");
    getPredictions(farmId)
      .then((data) => setItems(Array.isArray(data) ? data : []))
      .catch((err) => setError(err?.response?.data?.detail || "Unable to load NDVI trend"));
  }, [farmId]);

  const sorted = [...items].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  const labels = sorted.map((item) => new Date(item.created_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }));
  const values = sorted.map((item) => item.ndvi_value ?? 0);

  if (error) {
    return <p className="rounded-lg bg-tertiary/10 p-md text-body-sm text-tertiary">{error}</p>;
  }

  if (!values.length) {
    return <p className="rounded-lg bg-surface-container p-md text-body-sm text-on-surface-variant">Run more predictions to build an NDVI trend.</p>;
  }

  const data = {
    labels,
    datasets: [
      {
        label: "NDVI",
        data: values,
        borderColor: "#006c49",
        backgroundColor: "rgba(0,108,73,.14)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 7,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#342f2b",
        padding: 10,
        callbacks: { label: (context) => ` NDVI: ${context.parsed.y.toFixed(2)}` },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
      y: {
        min: 0,
        max: 1,
        grid: { color: "rgba(108,122,113,.18)" },
        ticks: { stepSize: 0.2 },
      },
    },
  };

  return (
    <div>
      <div className="mb-md grid grid-cols-3 gap-sm text-center">
        <div className="rounded-lg bg-surface-container p-sm">
          <p className="text-label-sm text-on-surface-variant">Latest</p>
          <p className="text-headline-sm font-headline-sm text-on-surface">{values.at(-1).toFixed(2)}</p>
        </div>
        <div className="rounded-lg bg-surface-container p-sm">
          <p className="text-label-sm text-on-surface-variant">Best</p>
          <p className="text-headline-sm font-headline-sm text-on-surface">{Math.max(...values).toFixed(2)}</p>
        </div>
        <div className="rounded-lg bg-surface-container p-sm">
          <p className="text-label-sm text-on-surface-variant">Change</p>
          <p className="text-headline-sm font-headline-sm text-on-surface">
            {(values.at(-1) - values[0] >= 0 ? "+" : "") + (values.at(-1) - values[0]).toFixed(2)}
          </p>
        </div>
      </div>
      <div className="h-72">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
