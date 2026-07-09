import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useToast } from "../context/ToastContext";
import { createFarm, createPrediction, generateRecommendation, getApiErrorMessage } from "../lib/api";

const CROPS = [
  { value: "Mustard", icon: "eco", desc: "Brassica juncea. High sensitivity to temperature fluctuations during bloom.", bg: "bg-secondary-container/20", color: "text-secondary-container" },
  { value: "Wheat", icon: "grass", desc: "Triticum aestivum. Predominantly wind-pollinated, moderate data density.", bg: "bg-surface-container-high", color: "text-secondary" },
  { value: "Sunflower", icon: "local_florist", desc: "Helianthus annuus. Highly dependent on bee activity and direct sunlight metrics.", bg: "bg-surface-container-high", color: "text-secondary" },
  { value: "Rice", icon: "water_drop", desc: "Oryza sativa. Requires detailed humidity and standing water analysis.", bg: "bg-surface-container-high", color: "text-on-surface-variant" },
  { value: "Cotton", icon: "filter_drama", desc: "Gossypium. Complex pollination cycle requiring hybrid meteorological models.", bg: "bg-surface-container-high", color: "text-on-surface-variant" },
];

const LOCATIONS = [
  { name: "Nashik", lat: 19.9975, lng: 73.7898 },
  { name: "Punjab", lat: 30.9, lng: 75.8573 },
  { name: "Haryana", lat: 29.0588, lng: 76.0856 },
  { name: "Gujarat", lat: 23.0225, lng: 72.5714 },
  { name: "Madhya Pradesh", lat: 23.2599, lng: 77.4126 },
  { name: "Maharashtra", lat: 19.7515, lng: 75.7139 },
  { name: "Rajasthan", lat: 27.0238, lng: 74.2179 },
  { name: "Uttar Pradesh", lat: 26.8467, lng: 80.9462 },
  { name: "Bihar", lat: 25.0961, lng: 85.3131 },
  { name: "Karnataka", lat: 15.3173, lng: 75.7139 },
  { name: "Andhra Pradesh", lat: 15.9129, lng: 79.7399 },
  { name: "Telangana", lat: 17.1232, lng: 79.2089 },
  { name: "Odisha", lat: 20.9517, lng: 85.0985 },
  { name: "West Bengal", lat: 22.9868, lng: 87.855 },
  { name: "Tamil Nadu", lat: 11.1271, lng: 78.6569 },
  { name: "Kerala", lat: 10.8505, lng: 76.2711 },
  { name: "Assam", lat: 26.2006, lng: 92.9376 },
  { name: "Jharkhand", lat: 23.6102, lng: 85.2799 },
  { name: "Chhattisgarh", lat: 21.2787, lng: 81.8661 },
  { name: "Uttarakhand", lat: 30.0668, lng: 79.0193 },
];

const LOADING_MESSAGES = [
  "Fetching weather data...",
  "Analyzing crop health...",
  "Checking bee activity...",
  "Calculating pollination score...",
  "Consulting the AI...",
  "Generating recommendation...",
];

export default function PredictPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [crop, setCrop] = useState("");
  const [location, setLocation] = useState("");
  const [farmName, setFarmName] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadMsg, setLoadMsg] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit() {
    setError("");
    setLoading(true);

    const selected = LOCATIONS.find((l) => l.name === location);
    if (!selected) {
      setError("Please select a location");
      setLoading(false);
      return;
    }

    try {
      setLoadMsg(LOADING_MESSAGES[0]);
      const farm = await createFarm({
        name: farmName || `${crop} Farm`,
        crop_type: crop,
        location: selected.name,
        location_lat: selected.lat,
        location_lng: selected.lng,
      });

      setLoadMsg(LOADING_MESSAGES[1]);
      const prediction = await createPrediction(farm.id);

      setLoadMsg(LOADING_MESSAGES[5]);
      await generateRecommendation(farm.id, prediction.id);

      toast.success("Prediction complete! Redirecting to dashboard...");
      navigate(`/dashboard?farm_id=${farm.id}`);
    } catch (err) {
      const message = getApiErrorMessage(err, "Prediction failed");
      toast.error(message);
      setError(message);
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
          <p className="mt-6 text-headline-sm font-bold text-on-surface">{loadMsg}</p>
          <div className="mt-4 h-2 w-48 overflow-hidden rounded-full bg-surface-container mx-auto">
            <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-secondary to-primary animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[640px] py-8">
      <div className="mb-lg">
        <nav className="flex items-center gap-sm text-on-surface-variant font-body-sm text-body-sm mb-md">
          <Link to="/dashboard" className="hover:text-primary transition-colors">Predictions</Link>
          <span className="material-symbols-outlined text-[16px]">chevron_right</span>
          <span className="text-on-surface">New Prediction</span>
        </nav>
        <h1 className="font-headline-lg text-headline-lg text-on-background mb-xs">Select Crop Type</h1>
        <p className="font-body-md text-body-md text-on-surface-variant">Choose the primary crop for this pollination forecast.</p>
      </div>

      <div className="mb-xl flex items-center gap-sm">
        <div className="h-2 flex-1 bg-primary rounded-full relative overflow-hidden">
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
        <div className="h-2 flex-1 bg-surface-container-high rounded-full" />
        <div className="h-2 flex-1 bg-surface-container-high rounded-full" />
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-error-container p-4 text-body-sm font-medium text-on-error-container">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-md">
        {CROPS.map((item) => {
          const selected = crop === item.value;
          return (
            <label key={item.value} className="relative block cursor-pointer group">
              <input
                type="radio"
                name="crop_selection"
                className="peer sr-only"
                checked={selected}
                onChange={() => setCrop(item.value)}
              />
              <div className={`bg-surface rounded-xl p-md flex items-center gap-md transition-all relative overflow-hidden ${
                selected
                  ? "border-2 border-primary shadow-[0_4px_12px_rgba(16,185,129,0.1)]"
                  : "border border-outline-variant shadow-[0_1px_3px_rgba(0,0,0,0.05)] hover:border-primary/50 hover:shadow-[0_4px_12px_rgba(0,0,0,0.05)] group-hover:bg-surface-container-low"
              }`}>
                {selected && (
                  <div className="absolute right-0 top-0 w-32 h-32 bg-secondary-container/10 rounded-bl-full -mr-8 -mt-8 pointer-events-none" />
                )}
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 relative z-10 transition-colors ${
                  selected
                    ? "bg-secondary-container/20 text-secondary-container"
                    : `${item.bg} ${item.color} group-hover:bg-secondary/10`
                }`}>
                  <span className="material-symbols-outlined" style={selected ? { fontVariationSettings: "'FILL' 1" } : undefined}>{item.icon}</span>
                </div>
                <div className="flex-1 relative z-10">
                  <h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">{item.value}</h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">{item.desc}</p>
                </div>
                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center relative z-10 transition-colors ${
                  selected
                    ? "border-primary bg-primary"
                    : "border-outline-variant group-hover:border-primary/50"
                }`}>
                  <span className={`material-symbols-outlined text-[16px] font-bold ${
                    selected ? "text-white" : "text-transparent"
                  }`}>check</span>
                </div>
              </div>
            </label>
          );
        })}
      </div>

      <div className="mt-xl space-y-6">
        <div>
          <label className="font-label-md text-label-md font-bold text-on-surface">Location</label>
          <select
            className="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-4 py-2.5 text-body-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            <option value="">Select a location</option>
            {LOCATIONS.map((l) => (
              <option key={l.name} value={l.name}>{l.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="font-label-md text-label-md font-bold text-on-surface">Farm Name</label>
          <input
            type="text"
            placeholder="e.g. North Field"
            className="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-4 py-2.5 text-body-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            value={farmName}
            onChange={(e) => setFarmName(e.target.value)}
          />
        </div>
      </div>

      <div className="mt-xl flex justify-between items-center pt-md border-t border-outline-variant">
        <Link to="/dashboard" className="px-md py-2 font-label-md text-label-md text-on-surface-variant hover:text-on-surface transition-colors">
          Cancel
        </Link>
        <button
          onClick={handleSubmit}
          disabled={!crop || !location}
          className="bg-primary hover:bg-[#005a3c] text-on-primary font-label-md text-label-md py-2 px-xl rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-sm"
        >
          Next Step
          <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}
