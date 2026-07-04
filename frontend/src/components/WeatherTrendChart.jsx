import { useEffect, useState } from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from "chart.js";
import { Line } from "react-chartjs-2";
import { getWeatherForecast } from "../lib/api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function WeatherTrendChart({ farmId }) {
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getWeatherForecast(farmId, 7)
      .then((data) => setForecast(data.forecast || []))
      .catch(() => setError("Failed to load forecast"));
  }, [farmId]);

  if (error) {
    return (
      <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <p className="font-body-sm text-tertiary">{error}</p>
      </div>
    );
  }

  if (forecast.length === 0) return null;

  const labels = forecast.map((d) => {
    const date = new Date(d.date);
    return date.toLocaleDateString("en-IN", { weekday: "short", day: "numeric" });
  });

  const data = {
    labels,
    datasets: [
      {
        label: "Max Temp",
        data: forecast.map((d) => d.temp_max),
        borderColor: "#006c49",
        backgroundColor: "rgba(0, 108, 73, 0.08)",
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: "Min Temp",
        data: forecast.map((d) => d.temp_min),
        borderColor: "#fea619",
        backgroundColor: "rgba(254, 166, 25, 0.08)",
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
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
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { family: "Geist Sans", size: 11 } },
      },
      y: {
        grid: { color: "rgba(0,0,0,0.05)" },
        ticks: {
          font: { family: "Inter", size: 11 },
          callback: (v) => v + "°C",
        },
      },
    },
  };

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md">7-Day Temperature Forecast</h3>
      <div className="h-56">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
