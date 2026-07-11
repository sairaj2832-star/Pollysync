import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useToast } from "../context/ToastContext";
import { createFarm, createPrediction, generateRecommendation, getApiErrorMessage } from "../lib/api";
import InteractiveGoogleMap from "../components/InteractiveGoogleMap";

const CROPS = [
  { value: "Mustard", icon: "eco", desc: "Brassica juncea. High sensitivity to temperature fluctuations during bloom.", bg: "bg-secondary-container/20", color: "text-secondary-container" },
  { value: "Wheat", icon: "grass", desc: "Triticum aestivum. Predominantly wind-pollinated, moderate data density.", bg: "bg-surface-container-high", color: "text-secondary" },
  { value: "Sunflower", icon: "local_florist", desc: "Helianthus annuus. Highly dependent on bee activity and direct sunlight metrics.", bg: "bg-surface-container-high", color: "text-secondary" },
  { value: "Rice", icon: "water_drop", desc: "Oryza sativa. Requires detailed humidity and standing water analysis.", bg: "bg-surface-container-high", color: "text-on-surface-variant" },
  { value: "Cotton", icon: "filter_drama", desc: "Gossypium. Complex pollination cycle requiring hybrid meteorological models.", bg: "bg-surface-container-high", color: "text-on-surface-variant" },
];

const LOCATIONS = [
  { name: "Nashik", district: "Nashik", state: "Maharashtra", lat: 19.9975, lng: 73.7898 },
  { name: "Pune", district: "Pune", state: "Maharashtra", lat: 18.5204, lng: 73.8567 },
  { name: "Punjab", district: "Ludhiana", state: "Punjab", lat: 30.9, lng: 75.8573 },
  { name: "Haryana", district: "Karnal", state: "Haryana", lat: 29.0588, lng: 76.0856 },
  { name: "Gujarat", district: "Ahmedabad", state: "Gujarat", lat: 23.0225, lng: 72.5714 },
  { name: "Madhya Pradesh", district: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lng: 77.4126 },
  { name: "Maharashtra", district: "Mumbai", state: "Maharashtra", lat: 19.7515, lng: 75.7139 },
  { name: "Rajasthan", district: "Jaipur", state: "Rajasthan", lat: 27.0238, lng: 74.2179 },
  { name: "Uttar Pradesh", district: "Lucknow", state: "Uttar Pradesh", lat: 26.8467, lng: 80.9462 },
  { name: "Bihar", district: "Patna", state: "Bihar", lat: 25.0961, lng: 85.3131 },
  { name: "Karnataka", district: "Bengaluru", state: "Karnataka", lat: 15.3173, lng: 75.7139 },
  { name: "Andhra Pradesh", district: "Amaravati", state: "Andhra Pradesh", lat: 15.9129, lng: 79.7399 },
  { name: "Telangana", district: "Hyderabad", state: "Telangana", lat: 17.1232, lng: 79.2089 },
  { name: "Odisha", district: "Bhubaneswar", state: "Odisha", lat: 20.9517, lng: 85.0985 },
  { name: "West Bengal", district: "Kolkata", state: "West Bengal", lat: 22.9868, lng: 87.855 },
  { name: "Tamil Nadu", district: "Chennai", state: "Tamil Nadu", lat: 11.1271, lng: 78.6569 },
  { name: "Kerala", district: "Thiruvananthapuram", state: "Kerala", lat: 10.8505, lng: 76.2711 },
  { name: "Assam", district: "Guwahati", state: "Assam", lat: 26.2006, lng: 92.9376 },
  { name: "Jharkhand", district: "Ranchi", state: "Jharkhand", lat: 23.6102, lng: 85.2799 },
  { name: "Chhattisgarh", district: "Raipur", state: "Chhattisgarh", lat: 21.2787, lng: 81.8661 },
  { name: "Uttarakhand", district: "Dehradun", state: "Uttarakhand", lat: 30.0668, lng: 79.0193 },
];

const LOADING_MESSAGES = [
  "Initiating Prediction Matrix...",
  "Fetching localized weather models...",
  "Analyzing historical bee populations...",
  "Cross-referencing farm topographies...",
  "Calculating pollination probabilities...",
  "Generating yield forecasts...",
  "Applying machine learning models...",
  "Finalizing prediction matrix...",
];

export default function PredictPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [step, setStep] = useState(1);
  const [crop, setCrop] = useState("");
  const [location, setLocation] = useState("");
  const [customCoords, setCustomCoords] = useState(null);
  const [farmName, setFarmName] = useState("");
  const [locationSearch, setLocationSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadMsgIndex, setLoadMsgIndex] = useState(0);
  const [error, setError] = useState("");

  const msgInterval = useRef(null);

  function getClosestLocation(lat, lng) {
    let closest = LOCATIONS[0];
    let minDist = Infinity;
    for (const loc of LOCATIONS) {
      const dist = Math.hypot(loc.lat - lat, loc.lng - lng);
      if (dist < minDist) {
        minDist = dist;
        closest = loc;
      }
    }
    return closest;
  }

  const handleMapLocationSelect = (coords) => {
    setCustomCoords(coords);
    const closest = getClosestLocation(coords.lat, coords.lng);
    setLocation(closest.name);
    setFarmName(`${closest.name} ${crop} Farm`);
  };

  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation is not supported by your browser");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        handleMapLocationSelect(coords);
        toast.success("Location detected successfully!");
      },
      (err) => {
        console.error("Geolocation error:", err);
        let msg = "Failed to detect location.";
        if (err.code === 1) {
          msg = "Location access denied. Please click the site settings icon (lock/sliders) in your browser address bar next to the URL, change Location to 'Allow', and try again.";
        } else if (err.code === 2) {
          msg = "Position unavailable. Please ensure your device location services are enabled.";
        } else if (err.code === 3) {
          msg = "Location request timed out. Please try again.";
        } else {
          msg = `Error: ${err.message}`;
        }
        toast.error(msg);
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  };

  useEffect(() => {
    if (step === 2 && !location) {
      handleDetectLocation();
    }
  }, [step, location]);

  useEffect(() => {
    if (loading) {
      msgInterval.current = setInterval(() => {
        setLoadMsgIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
      }, 3000);
    } else {
      clearInterval(msgInterval.current);
      setLoadMsgIndex(0);
    }
    return () => clearInterval(msgInterval.current);
  }, [loading]);

  const filteredLocations = LOCATIONS.filter(
    (l) =>
      l.name.toLowerCase().includes(locationSearch.toLowerCase()) ||
      l.district.toLowerCase().includes(locationSearch.toLowerCase()) ||
      l.state.toLowerCase().includes(locationSearch.toLowerCase())
  );

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
      setLoadMsgIndex(0);
      const farm = await createFarm({
        name: farmName || `${crop} Farm`,
        crop_type: crop,
        location: selected.name,
        location_lat: customCoords ? customCoords.lat : selected.lat,
        location_lng: customCoords ? customCoords.lng : selected.lng,
      });

      setLoadMsgIndex(2);
      const prediction = await createPrediction(farm.id);

      setLoadMsgIndex(6);
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
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background" style={{ backgroundImage: "radial-gradient(var(--color-primary) 1px, transparent 1px)", backgroundSize: "24px 24px" }}>
        <div className="flex flex-col items-center gap-lg max-w-md text-center">
          <div className="flex items-center gap-sm mb-md">
            <span className="material-symbols-outlined text-primary text-[32px]">agriculture</span>
            <span className="font-headline-lg text-headline-lg text-primary font-bold">PolliSync</span>
          </div>

          <div className="relative w-40 h-40 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-2 border-outline-variant/20 animate-[spin_4s_linear_infinite]" style={{ borderTopColor: "transparent", borderRightColor: "transparent" }} />
            <div className="absolute inset-2 rounded-full border-4 border-t-primary border-r-transparent border-b-transparent border-l-transparent animate-spin" />
            <div className="relative w-16 h-16 rounded-full bg-surface flex items-center justify-center shadow-sm">
              <span className="material-symbols-outlined text-primary text-[40px] animate-pulse">analytics</span>
            </div>
          </div>

          <p className="font-headline-sm text-headline-sm text-on-surface font-bold transition-all duration-500 h-8">
            {LOADING_MESSAGES[loadMsgIndex]}
          </p>

          <div className="flex gap-[3px] w-64">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="h-1.5 flex-1 rounded-full bg-surface-container-high overflow-hidden"
              >
                <div
                  className="h-full rounded-full bg-primary transition-all duration-700"
                  style={{
                    animation: `pulse-progress 1.5s ease-in-out ${i * 0.25}s infinite`,
                  }}
                />
              </div>
            ))}
          </div>

          <p className="font-body-sm text-body-sm text-on-surface-variant mt-md">
            Compiling multi-variate environmental data. This may take a few moments.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[640px] py-8">
      {step === 1 && (
        <>
          <div className="mb-lg">
            <nav className="flex items-center gap-sm text-on-surface-variant font-body-sm text-body-sm mb-md">
              <Link to="/dashboard" className="hover:text-primary transition-colors">Predictions</Link>
              <span className="material-symbols-outlined text-[16px]">chevron_right</span>
              <span className="text-on-surface">New Prediction</span>
            </nav>
            <h1 className="font-headline-lg text-headline-lg text-on-background mb-xs">Select Crop Type</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Step 1 of 3: Choose the primary crop for this pollination forecast.</p>
          </div>

          <div className="mb-xl flex items-center gap-sm">
            <div className="h-2 flex-1 bg-primary rounded-full" />
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

          <div className="mt-xl flex justify-between items-center pt-md border-t border-outline-variant">
            <Link to="/dashboard" className="px-md py-2 font-label-md text-label-md text-on-surface-variant hover:text-on-surface transition-colors">
              Cancel
            </Link>
            <button
              onClick={() => { setError(""); setStep(2); }}
              disabled={!crop}
              className="bg-primary hover:brightness-90 text-on-primary font-label-md text-label-md py-2 px-xl rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-sm"
            >
              Next Step
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </>
      )}

      {step === 2 && (
        <>
          <button
            onClick={() => setStep(1)}
            className="flex items-center gap-sm text-on-surface-variant hover:text-primary transition-colors font-body-sm mb-lg"
          >
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Back to Crop Type
          </button>

          <div className="mb-xl">
            <div className="inline-flex items-center gap-xs px-md py-xs rounded-full bg-primary-container/10 text-primary font-label-sm text-label-sm mb-md">
              <span className="material-symbols-outlined text-[16px]">checklist</span>
              Step 2 of 3
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-background mb-xs">Where is your farm located?</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Select your district or use the map to pinpoint your farm's exact location for precise weather and pollination modeling.
            </p>
          </div>

          <div className="mb-xl flex items-center gap-sm">
            <div className="h-2 flex-1 bg-primary rounded-full" />
            <div className="h-2 flex-1 bg-primary rounded-full" />
            <div className="h-2 flex-1 bg-surface-container-high rounded-full" />
          </div>

          {error && (
            <div className="mb-6 rounded-lg bg-error-container p-4 text-body-sm font-medium text-on-error-container">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
            <div className="space-y-lg">
              <div className="space-y-md">
                <div>
                  <label className="block font-label-md text-label-md text-on-surface-variant mb-sm">Search District</label>
                  <div className="relative">
                    <span className="absolute left-md top-1/2 -translate-x-1/2 material-symbols-outlined text-on-surface-variant text-[18px]">search</span>
                    <input
                      type="text"
                      placeholder="Search districts..."
                      className="w-full pl-xl pr-md py-sm rounded-lg border border-outline-variant bg-surface text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                      value={locationSearch}
                      onChange={(e) => setLocationSearch(e.target.value)}
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleDetectLocation}
                  className="w-full flex items-center justify-center gap-sm bg-surface-container-high hover:bg-surface-container-highest text-primary border border-outline-variant rounded-lg py-sm px-md transition-colors text-label-md font-label-md font-semibold active:scale-[0.98]"
                >
                  <span className="material-symbols-outlined text-[20px]">my_location</span>
                  Detect My Location (GPS)
                </button>
              </div>

              <div className="max-h-60 overflow-y-auto space-y-xs rounded-xl border border-outline-variant bg-surface p-xs">
                {filteredLocations.length === 0 ? (
                  <p className="text-body-sm text-on-surface-variant text-center py-lg">No districts found</p>
                ) : (
                  filteredLocations.map((loc) => {
                    const selected = location === loc.name;
                    return (
                      <button
                        key={loc.name}
                        type="button"
                        onClick={() => {
                          setLocation(loc.name);
                          setCustomCoords({ lat: loc.lat, lng: loc.lng });
                          setFarmName(`${loc.name} ${crop} Farm`);
                        }}
                        className={`w-full text-left px-md py-sm rounded-lg flex items-center gap-md transition-colors ${
                          selected
                            ? "bg-primary-container/10 text-primary font-bold"
                            : "text-on-surface hover:bg-surface-container-high"
                        }`}
                      >
                        <span className={`material-symbols-outlined text-[18px] ${selected ? "text-primary" : "text-on-surface-variant"}`}>
                          {selected ? "radio_button_checked" : "location_on"}
                        </span>
                        <div className="flex-1">
                          <span className="font-label-md text-label-md">{loc.district}</span>
                          <span className="text-body-sm text-on-surface-variant ml-xs">({loc.state})</span>
                        </div>
                        {selected && (
                          <span className="material-symbols-outlined text-[18px] text-primary">check</span>
                        )}
                      </button>
                    );
                  })
                )}
              </div>

              {location && (() => {
                const sel = LOCATIONS.find((l) => l.name === location);
                if (!sel) return null;
                const displayLat = customCoords ? customCoords.lat : sel.lat;
                const displayLng = customCoords ? customCoords.lng : sel.lng;
                return (
                  <div className="bg-surface border border-outline-variant rounded-xl p-md space-y-sm">
                    <div className="flex items-center gap-sm text-primary">
                      <span className="material-symbols-outlined text-[18px]">location_on</span>
                      <span className="font-label-md text-label-md font-bold">Selected Location</span>
                    </div>
                    <p className="font-headline-sm text-headline-sm text-on-surface">{sel.district} District</p>
                    <p className="text-body-sm text-on-surface-variant">{sel.state}, India</p>
                    <div className="border-t border-outline-variant/50 pt-sm mt-sm flex gap-lg text-body-sm">
                      <span className="font-mono text-on-surface-variant">{displayLat.toFixed(4)} N</span>
                      <span className="font-mono text-on-surface-variant">{displayLng.toFixed(4)} E</span>
                    </div>
                  </div>
                );
              })()}
            </div>

            <div className="relative w-full h-[400px] rounded-xl overflow-hidden border border-outline-variant bg-surface-container-higher flex flex-col">
              {(() => {
                const sel = LOCATIONS.find((l) => l.name === location) || LOCATIONS[0];
                const mapCenter = customCoords || { lat: sel.lat, lng: sel.lng };
                return (
                  <InteractiveGoogleMap
                    center={mapCenter}
                    zoom={10}
                    onLocationSelect={handleMapLocationSelect}
                  />
                );
              })()}
              {location && (() => {
                const sel = LOCATIONS.find((l) => l.name === location);
                if (!sel) return null;
                return (
                  <div className="absolute bottom-md left-1/2 -translate-x-1/2 bg-surface/90 backdrop-blur-sm border border-outline-variant rounded-full px-md py-xs flex items-center gap-sm shadow-md z-[1000] pointer-events-none">
                    <span className="material-symbols-outlined text-primary text-[18px]">my_location</span>
                    <span className="font-label-sm text-label-sm text-on-surface">{sel.district}, {sel.state}</span>
                  </div>
                );
              })()}
            </div>
          </div>

          <div className="mt-xl flex justify-between items-center pt-md border-t border-outline-variant">
            <span />
            <button
              onClick={() => { setError(""); setStep(3); }}
              disabled={!location}
              className="bg-primary hover:brightness-90 text-on-primary font-label-md text-label-md py-2 px-xl rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-sm"
            >
              Continue
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </>
      )}

      {step === 3 && (
        <>
          <button
            onClick={() => setStep(2)}
            className="flex items-center gap-sm text-on-surface-variant hover:text-primary transition-colors font-body-sm mb-lg"
          >
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Back to Location
          </button>

          <div className="mb-xl">
            <div className="flex items-center gap-sm text-body-sm text-on-surface-variant mb-md">
              <span className="hover:text-primary transition-colors cursor-pointer" onClick={() => setStep(1)}>Select Crop</span>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
              <span className="hover:text-primary transition-colors cursor-pointer" onClick={() => setStep(2)}>Choose Location</span>
              <span className="material-symbols-outlined text-[14px]">chevron_right</span>
              <span className="text-primary font-bold">Review</span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-background mb-xs">Review & Predict</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Confirm your details before initiating the machine learning analysis.</p>
          </div>

          <div className="mb-xl flex items-center gap-sm">
            <div className="h-2 flex-1 bg-primary rounded-full" />
            <div className="h-2 flex-1 bg-primary rounded-full" />
            <div className="h-2 flex-1 bg-primary rounded-full" />
          </div>

          {error && (
            <div className="mb-6 rounded-lg bg-error-container p-4 text-body-sm font-medium text-on-error-container">
              {error}
            </div>
          )}

          <div className="bg-surface border border-outline-variant rounded-xl p-xl shadow-sm relative overflow-hidden">
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "radial-gradient(var(--color-primary) 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
            <div className="relative z-10 space-y-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-md">
                  <span className="material-symbols-outlined text-[24px] text-primary">eco</span>
                  <div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">Crop Type</span>
                    <p className="font-headline-sm text-headline-sm text-on-surface">{crop}</p>
                  </div>
                </div>
                <div className="px-md py-xs rounded-full bg-primary-container/10 text-primary font-label-sm text-label-sm flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">eco</span>
                  {crop}
                </div>
              </div>

              {location && (() => {
                const sel = LOCATIONS.find((l) => l.name === location);
                if (!sel) return null;
                return (
                  <div className="flex items-start gap-md pt-md border-t border-outline-variant/50">
                    <span className="material-symbols-outlined text-[24px] text-on-surface-variant">location_on</span>
                    <div>
                      <span className="font-label-sm text-label-sm text-on-surface-variant">Location</span>
                      <p className="font-headline-sm text-headline-sm text-on-surface">{sel.district}, {sel.state}</p>
                      <p className="font-body-sm font-mono text-on-surface-variant mt-xs">
                        {sel.lat.toFixed(4)} N, {sel.lng.toFixed(4)} E
                      </p>
                    </div>
                  </div>
                );
              })()}

              <div className="pt-md border-t border-outline-variant/50">
                <div className="flex items-center gap-md">
                  <span className="material-symbols-outlined text-[24px] text-on-surface-variant">badge</span>
                  <div>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">Farm Name</span>
                    <p className="font-headline-sm text-headline-sm text-on-surface">{farmName || `${crop} Farm`}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-lg p-md rounded-lg bg-surface-container-low border border-outline-variant/50 flex items-start gap-md">
            <span className="material-symbols-outlined text-[18px] text-on-surface-variant flex-shrink-0 mt-[2px]">info</span>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Analysis typically takes 15-30 seconds. This will consume 1 prediction credit from your account.
            </p>
          </div>

          <div className="mt-xl flex justify-between items-center pt-md border-t border-outline-variant">
            <span />
            <button
              onClick={handleSubmit}
              className="bg-primary hover:brightness-90 text-on-primary font-label-md text-label-md py-2 px-xl rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] flex items-center gap-sm"
            >
              <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
              Predict Pollination
            </button>
          </div>
        </>
      )}
    </div>
  );
}
