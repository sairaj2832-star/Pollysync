import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../lib/api";
import BeeMap from "../components/BeeMap";
import FloweringCalendar from "../components/FloweringCalendar";
import NDVICard from "../components/NDVICard";
import PSIgauge from "../components/PSIgauge";
import PollenBar from "../components/PollenBar";
import RecommendationCard from "../components/RecommendationCard";
import WeatherCard from "../components/WeatherCard";
import { DashboardSkeleton } from "../components/LoadingSkeleton";

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const farmId = searchParams.get("farm_id") || "1";
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await api.get(`/api/predictions/dashboard/summary?farm_id=${farmId}`);
        setData(res.data);
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [farmId]);

  if (loading) return <DashboardSkeleton />;

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-bold text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-xl bg-leaf-700 px-6 py-2 font-bold text-white"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-bold text-slate-500">No predictions yet. Create one!</p>
        </div>
      </div>
    );
  }

  const farm = data.farm || {};
  const weather = data.current_weather || {};
  const prediction = data.latest_prediction;
  const beeSpecies = data.bee_species || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-black text-slate-900">{farm.name || "Farm"}</h1>
        {farm.crop_type && (
          <span className="rounded-full bg-leaf-100 px-3 py-1 text-sm font-bold text-leaf-700">
            {farm.crop_type}
          </span>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="relative flex items-center justify-center rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
          <PSIgauge score={prediction?.psi_score} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <WeatherCard label="Temperature" value={weather.temperature ?? "--"} unit="°C" icon="🌡️" />
          <WeatherCard label="Humidity" value={weather.humidity ?? "--"} unit="%" icon="💧" />
          <WeatherCard label="Rainfall" value={weather.rainfall ?? "--"} unit="mm" icon="🌧️" />
          <WeatherCard label="Wind" value={weather.wind_speed ?? "--"} unit="km/h" icon="💨" />
        </div>

        <div className="flex flex-col gap-3">
          <div className={`rounded-2xl border p-5 text-center shadow-soft ${
            prediction?.risk_level === "Low" ? "border-emerald-100 bg-emerald-50"
            : prediction?.risk_level === "Medium" ? "border-amber-100 bg-amber-50"
            : "border-red-100 bg-red-50"
          }`}>
            <p className="text-sm font-bold uppercase tracking-wider text-slate-500">Risk Level</p>
            <p className={`mt-2 text-3xl font-black ${
              prediction?.risk_level === "Low" ? "text-emerald-600"
              : prediction?.risk_level === "Medium" ? "text-amber-600"
              : "text-red-600"
            }`}>
              {prediction?.risk_level || "--"}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <FloweringCalendar
          start={prediction?.flowering_start}
          end={prediction?.flowering_end}
          confidence={prediction?.flowering_confidence}
        />
        <PollenBar pollen={prediction?.pollen_summary} />
      </div>

      <RecommendationCard
        text={prediction?.recommendation}
        riskLevel={prediction?.risk_level}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <NDVICard value={prediction?.ndvi_value} />
        <BeeMap
          center={[farm.location_lat, farm.location_lng]}
          occurrences={beeSpecies.map((s) => ({ species: s, lat: farm.location_lat, lng: farm.location_lng }))}
        />
      </div>
    </div>
  );
}
