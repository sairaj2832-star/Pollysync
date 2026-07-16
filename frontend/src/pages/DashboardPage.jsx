import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getDashboardSummary, getFarms } from "../lib/api";
import BeeMap from "../components/BeeMap";
import FloweringCalendar from "../components/FloweringCalendar";
import NDVICard from "../components/NDVICard";
import PSIgauge from "../components/PSIgauge";
import PollenBar from "../components/PollenBar";
import RecommendationCard from "../components/RecommendationCard";
import WeatherCard from "../components/WeatherCard";
import WeatherTrendChart from "../components/WeatherTrendChart";
import PSIHistoryChart from "../components/PSIHistoryChart";
import { DashboardSkeleton } from "../components/LoadingSkeleton";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const requestedFarmId = searchParams.get("farm_id");
  const [data, setData] = useState(null);
  const [farmId, setFarmId] = useState(requestedFarmId || "");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hasFarms, setHasFarms] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError("");
        const farms = await getFarms();
        if (!Array.isArray(farms) || farms.length === 0) {
          setHasFarms(false);
          setData(null);
          setFarmId("");
          return;
        }

        setHasFarms(true);
        const resolvedFarmId = requestedFarmId || String(farms[0].id);
        setFarmId(resolvedFarmId);
        const result = await getDashboardSummary(resolvedFarmId);
        setData(result);
      } catch (err) {
        setError(err?.response?.data?.detail || err.message || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [requestedFarmId]);

  if (loading) return <DashboardSkeleton />;

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <span className="material-symbols-outlined text-5xl text-tertiary">error</span>
          <p className="mt-4 text-headline-sm font-bold text-tertiary">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-lg bg-primary px-6 py-2 text-label-md font-bold text-on-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data || !hasFarms) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-gutter relative overflow-y-auto min-h-[60vh]">
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "radial-gradient(var(--color-primary) 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
        <div className="relative z-10 max-w-lg w-full flex flex-col items-center text-center">
          <div className="w-48 h-48 mb-xl rounded-full bg-surface-container-high border border-outline-variant shadow-sm flex items-center justify-center overflow-hidden">
            <span className="material-symbols-outlined text-6xl text-on-surface-variant/40">agriculture</span>
          </div>
          <h2 className="font-display text-display text-on-background mb-sm">No Predictions Yet</h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant mb-2xl max-w-md">
            Your pollination forecasting dashboard is empty. Add your first farm location and crop data to generate precision pollination insights and weather impact models.
          </p>
          <button
            onClick={() => navigate("/predict")}
            className="group relative inline-flex items-center justify-center gap-sm px-xl py-lg bg-primary text-on-primary rounded-lg font-headline-sm text-headline-sm font-semibold shadow-[0_1px_3px_rgba(0,0,0,0.1)] hover:brightness-90 transition-all duration-200"
          >
            <span className="material-symbols-outlined text-[24px]">add_circle</span>
            Create First Prediction
          </button>
          <div className="mt-lg flex items-center gap-sm text-on-surface-variant/70 text-body-sm font-body-sm">
            <span className="material-symbols-outlined text-[16px]">info</span>
            <span>Need help? Check out our <span className="text-primary hover:underline cursor-pointer">Quick Start Guide</span>.</span>
          </div>
        </div>
      </div>
    );
  }

  const farm = data.farm || {};
  const weather = data.current_weather || {};
  const prediction = data.latest_prediction;
  const beeSpecies = data.bee_species || [];

  return (
    <div className="relative">
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none" style={{ backgroundImage: "radial-gradient(var(--color-primary) 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
      <div className="relative z-10 grid grid-cols-12 gap-lg">
        {/* 1. PSI GAUGE - 4 columns */}
        <div className="col-span-12 md:col-span-4 animate-fade-in-up stagger-1">
          <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col items-center justify-center text-center shadow-[0_1px_3px_rgba(0,0,0,0.05)] card-hover">
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md w-full text-left">
              Pollination Suitability Index
            </h3>
            <PSIgauge score={prediction?.psi_score} />
            <div className={`mt-sm rounded-full font-label-md text-label-md flex items-center gap-xs px-md py-xs ${
              prediction?.risk_level === "Low" ? "bg-primary-container/10 text-primary"
              : prediction?.risk_level === "Medium" ? "bg-secondary/10 text-secondary"
              : "bg-tertiary/10 text-tertiary"
            }`}>
              <span className="material-symbols-outlined text-sm">check_circle</span>
              {prediction?.risk_level || "Unknown"} Risk
            </div>
          </div>
        </div>

        {/* 2. WEATHER GRID - 5 columns */}
        <div className="col-span-12 md:col-span-5 animate-fade-in-up stagger-2">
          <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col shadow-[0_1px_3px_rgba(0,0,0,0.05)] card-hover">
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-md">Current Microclimate</h3>
            <div className="grid grid-cols-2 gap-md flex-1">
              <WeatherCard label="Temperature" value={weather.temperature ?? "--"} unit="°C" icon="temperature" trend={2} />
              <WeatherCard label="Humidity" value={weather.humidity ?? "--"} unit="%" icon="humidity" trend={-4} />
              <WeatherCard label="Rainfall" value={weather.rainfall ?? "--"} unit="mm" icon="rainfall" />
              <WeatherCard label="Wind" value={weather.wind_speed ?? "--"} unit="km/h" icon="wind" trend={-2} />
            </div>
          </div>
        </div>

        {/* 3. FARM STATUS / RISK - 3 columns */}
        <div className="col-span-12 md:col-span-3 animate-fade-in-up stagger-3">
          <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col justify-between shadow-[0_1px_3px_rgba(0,0,0,0.05)] card-hover">
            <div>
              <h3 className="font-headline-sm text-headline-sm text-on-surface mb-sm">Farm Status</h3>
              <div className={`w-full border rounded-xl p-md flex flex-col items-center justify-center mt-md text-center ${
                prediction?.risk_level === "Low" ? "bg-primary-container/10 border-primary-container/20"
                : prediction?.risk_level === "Medium" ? "bg-secondary/10 border-secondary/20"
                : "bg-tertiary/10 border-tertiary/20"
              }`}>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-sm shadow-sm ${
                  prediction?.risk_level === "Low" ? "bg-primary-container text-on-primary"
                  : prediction?.risk_level === "Medium" ? "bg-secondary text-on-secondary"
                  : "bg-tertiary text-on-tertiary"
                }`}>
                  <span className="material-symbols-outlined text-2xl">verified_user</span>
                </div>
                <span className={`font-headline-sm text-headline-sm ${
                  prediction?.risk_level === "Low" ? "text-primary"
                  : prediction?.risk_level === "Medium" ? "text-secondary"
                  : "text-tertiary"
                }`}>
                  {prediction?.risk_level || "--"} Risk
                </span>
                <span className="font-body-sm text-body-sm text-on-surface-variant mt-xs">
                  Conditions {prediction?.risk_level === "Low" ? "optimal" : prediction?.risk_level === "Medium" ? "moderate" : "challenging"} for pollination.
                </span>
              </div>
            </div>
            <div className="flex flex-col gap-sm mt-lg">
              <button className="w-full bg-surface border border-outline-variant text-on-surface font-label-md text-label-md py-sm rounded-lg hover:bg-surface-container-high transition-colors flex justify-center items-center gap-xs">
                <span className="material-symbols-outlined text-[18px]">download</span>
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* 4. FLOWERING CALENDAR - 6 columns */}
        <div className="col-span-12 md:col-span-6 animate-fade-in-up stagger-4">
          <FloweringCalendar
            start={prediction?.flowering_start}
            end={prediction?.flowering_end}
            confidence={prediction?.flowering_confidence}
          />
        </div>

        {/* 5. POLLEN INDEX - 6 columns */}
        <div className="col-span-12 md:col-span-6 animate-fade-in-up stagger-5">
          <PollenBar pollen={prediction?.pollen_summary} />
        </div>

        {/* 6. AI RECOMMENDATION - 8 columns */}
        <div className="col-span-12 md:col-span-8 animate-fade-in-up stagger-6">
          <RecommendationCard
            text={prediction?.recommendation}
            riskLevel={prediction?.risk_level}
          />
        </div>

        {/* 7. CROP HEALTH NDVI - 4 columns */}
        <div className="col-span-12 md:col-span-4 animate-fade-in-up stagger-7">
          <NDVICard value={prediction?.ndvi_value} />
        </div>

        {/* 8. CHARTS - 6+6 */}
        <div className="col-span-12 md:col-span-6 animate-fade-in-up stagger-8">
          <WeatherTrendChart farmId={farmId} />
        </div>
        <div className="col-span-12 md:col-span-6 animate-fade-in-up stagger-9">
          <PSIHistoryChart farmId={farmId} />
        </div>

        {/* 9. BEE MAP - 12 columns */}
        <div className="col-span-12 animate-fade-in">
          <BeeMap
            center={[farm.location_lat || 20, farm.location_lng || 78]}
            occurrences={(data.occurrences || []).map((o) => ({ species: o.species, lat: o.lat, lng: o.lng }))}
          />
        </div>
      </div>
    </div>
  );
}
