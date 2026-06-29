import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api";

const CROPS = ["Mustard", "Wheat", "Sunflower", "Rice", "Cotton"];
const LOCATIONS = [
  { name: "Nashik", lat: 19.9975, lng: 73.7898 },
  { name: "Punjab", lat: 30.9000, lng: 75.8573 },
  { name: "Haryana", lat: 29.0588, lng: 76.0856 },
  { name: "Gujarat", lat: 23.0225, lng: 72.5714 },
  { name: "Madhya Pradesh", lat: 23.2599, lng: 77.4126 },
  { name: "Maharashtra", lat: 19.7515, lng: 75.7139 },
  { name: "Rajasthan", lat: 27.0238, lng: 74.2179 },
  { name: "Uttar Pradesh", lat: 26.8467, lng: 80.9462 },
  { name: "Bihar", lat: 25.0961, lng: 85.3131 },
  { name: "Karnataka", lat: 15.3173, lng: 75.7139 },
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
  const [crop, setCrop] = useState("");
  const [location, setLocation] = useState("");
  const [farmName, setFarmName] = useState("");
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadMsg, setLoadMsg] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit() {
    setError("");
    setLoading(true);
    setStep(1);

    const selected = LOCATIONS.find((l) => l.name === location);
    if (!selected) {
      setError("Please select a location");
      setLoading(false);
      return;
    }

    try {
      setLoadMsg(LOADING_MESSAGES[0]);
      await new Promise((r) => setTimeout(r, 800));

      setLoadMsg(LOADING_MESSAGES[1]);
      const farmRes = await api.post("/api/farms", {
        name: farmName || `${crop} Farm`,
        crop_type: crop,
        location_lat: selected.lat,
        location_lng: selected.lng,
      });
      const farm = farmRes.data;

      setLoadMsg(LOADING_MESSAGES[2]);
      await new Promise((r) => setTimeout(r, 600));

      setLoadMsg(LOADING_MESSAGES[3]);
      const predRes = await api.post("/api/predictions", { farm_id: farm.id });
      const prediction = predRes.data;

      setLoadMsg(LOADING_MESSAGES[4]);
      await api.post("/api/recommendations/generate", {
        farm_id: farm.id,
        prediction_id: prediction.id,
      });

      setLoadMsg(LOADING_MESSAGES[5]);
      await new Promise((r) => setTimeout(r, 500));

      navigate(`/dashboard?farm_id=${farm.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Prediction failed");
      setLoading(false);
      setStep(0);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-leaf-200 border-t-leaf-700" />
          <p className="mt-6 text-xl font-bold text-slate-700">{loadMsg}</p>
          <div className="mt-2 h-2 w-48 overflow-hidden rounded-full bg-slate-200 mx-auto">
            <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-pollen to-leaf-500 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl py-12">
      <h1 className="text-3xl font-black text-slate-900">New Prediction</h1>
      <p className="mt-2 text-slate-500">
        Select a crop and location to get pollination insights.
      </p>

      {error && (
        <div className="mt-6 rounded-xl bg-red-50 p-4 text-sm font-medium text-red-600">
          {error}
        </div>
      )}

      <div className="mt-8 space-y-6">
        <div>
          <label className="text-sm font-bold text-slate-700">Farm Name</label>
          <input
            type="text"
            placeholder="e.g. North Field"
            className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-leaf-500 focus:ring-2 focus:ring-leaf-200"
            value={farmName}
            onChange={(e) => setFarmName(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm font-bold text-slate-700">Crop Type</label>
          <select
            className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-leaf-500 focus:ring-2 focus:ring-leaf-200"
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
          >
            <option value="">Select a crop</option>
            {CROPS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm font-bold text-slate-700">Location</label>
          <select
            className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-leaf-500 focus:ring-2 focus:ring-leaf-200"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            <option value="">Select a location</option>
            {LOCATIONS.map((l) => (
              <option key={l.name} value={l.name}>{l.name}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!crop || !location}
          className="w-full rounded-xl bg-leaf-700 py-3 font-bold text-white transition hover:bg-leaf-800 disabled:opacity-50"
        >
          Run Prediction
        </button>
      </div>
    </div>
  );
}
