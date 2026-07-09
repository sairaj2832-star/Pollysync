import { useEffect, useState } from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
import { getPredictions } from "../lib/api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function PSIHistoryChart({ farmId }) {
  const [predictions, setPredictions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getPredictions(farmId)
      .then((data) => setPredictions(Array.isArray(data) ? data : []))
      .catch(() => setError("Failed to load prediction history"));
  }, [farmId]);

  if (error) {
    return (
      <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <p className="font-body-sm text-tertiary">{error}</p>
      </div>
    );
  }

  if (predictions.length === 0) return null;

  const sorted = [...predictions].reverse();
  const labels = sorted.map((p) => {
    const d = new Date(p.created_at);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  });

  const data = {
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
          p.psi_score >= 70 ? "#006c49" : p.psi_score >= 40 ? "#fea619" : "#b91a24"
        ),
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: {
        backgroundColor: "#342f2b",
        titleFont: { family: "Geist Sans", size: 12, weight: "600" },
        bodyFont: { family: "Inter", size: 12 },
        cornerRadius: 8,
        padding: 10,
        callbacks: {
          afterLabel: function (context) {
            const p = sorted[context.dataIndex];
            return "Risk: " + p.risk_level;
          },
        },
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

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md">PSI History</h3>
      <div className="h-56">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
