import { useState, useEffect } from "react";
import { useToast } from "../context/ToastContext";
import InteractiveGoogleMap from "../components/InteractiveGoogleMap";
import { LOCATION_LIST } from "../components/ParameterForm";
import {
  updateFarm,
  getNotificationPreferences,
  updateNotificationPreferences,
} from "../lib/api";
import { useAuth } from "../context/AuthContext";
import Select from "../components/Select";

const TABS = [
  { key: "general", label: "General", icon: "info" },
  { key: "alerts", label: "Alerts & Notifications", icon: "notifications_active" },
];

const SOIL_TYPES = [
  { value: "alluvial", label: "Alluvial" },
  { value: "black", label: "Black Soil (Regur)" },
  { value: "red", label: "Red and Yellow" },
  { value: "laterite", label: "Laterite" },
  { value: "sandy", label: "Sandy" },
  { value: "clay", label: "Clay" },
];

const CROP_OPTIONS = [
  { value: "mustard", label: "Mustard (Brassica juncea)", icon: "eco" },
  { value: "sunflower", label: "Sunflower (Helianthus annuus)", icon: "local_florist" },
  { value: "cotton", label: "Cotton (Gossypium)", icon: "filter_drama" },
];

const VARIETY_OPTIONS = [
  { value: "variety1", label: "Varuna (RH-30)" },
  { value: "variety2", label: "Pusa Jaikisan" },
  { value: "variety3", label: "Kranti" },
  { value: "variety4", label: "Pusa Agrani" },
];

export default function SettingsPage() {
  const toast = useToast();
  const { user } = useAuth();
  const [tab, setTab] = useState("general");
  const [saving, setSaving] = useState(false);
  const [loadingPrefs, setLoadingPrefs] = useState(false);
  const [form, setForm] = useState({
    farmName: "Nashik Mustard Farm",
    location: "Nashik, Maharashtra",
    lat: 19.9975,
    lng: 73.7898,
    acreage: "125.5",
    soilType: "alluvial",
    elevation: "600m ASL",
    crop: "mustard",
    variety: "variety1",
    irrigationMethod: "",
    plantingDate: "2023-11-15",
    harvestDate: "2024-03-20",
  });

  const handleMapLocationSelect = (coords) => {
    update("lat", coords.lat);
    update("lng", coords.lng);
  };

  function getClosestLocation(lat, lng) {
    let closest = LOCATION_LIST[0];
    let minDist = Infinity;
    for (const loc of LOCATION_LIST) {
      const dist = Math.hypot(loc.lat - lat, loc.lng - lng);
      if (dist < minDist) {
        minDist = dist;
        closest = loc;
      }
    }
    return closest;
  }

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
        update("lat", coords.lat);
        update("lng", coords.lng);
        const closest = getClosestLocation(coords.lat, coords.lng);
        update("location", `${closest.district}, ${closest.state}`);
        toast.success("Location updated successfully!");
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

  const [notifications, setNotifications] = useState({
    pushCritical: true,
    pushDaily: true,
    pushSystem: false,
    emailWeekly: true,
    emailBilling: true,
    whatsappUrgent: false,
    smsAlerts: true,
  });

  useEffect(() => {
    handleDetectLocation();
  }, []);

  useEffect(() => {
    async function fetchPrefs() {
      setLoadingPrefs(true);
      try {
        const data = await getNotificationPreferences();
        setNotifications({
          pushCritical: data.push_critical,
          pushDaily: data.push_daily,
          pushSystem: data.push_system,
          emailWeekly: data.email_weekly,
          emailBilling: data.email_billing,
          whatsappUrgent: data.whatsapp_urgent,
          smsAlerts: data.sms_alerts,
        });
      } catch {
        // ignore, use defaults
      } finally {
        setLoadingPrefs(false);
      }
    }
    fetchPrefs();
  }, []);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function toggleNotif(key) {
    setNotifications((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const { getApiErrorMessage } = await import("../lib/api");
      if (tab === "alerts") {
        await updateNotificationPreferences({
          push_critical: notifications.pushCritical,
          push_daily: notifications.pushDaily,
          push_system: notifications.pushSystem,
          email_weekly: notifications.emailWeekly,
          email_billing: notifications.emailBilling,
          whatsapp_urgent: notifications.whatsappUrgent,
          sms_alerts: notifications.smsAlerts,
        });
      } else {
        await updateFarm(1, {
          name: form.farmName,
          crop_type: form.crop,
          variety: form.variety || undefined,
          irrigation_method: form.irrigationMethod || undefined,
          planting_date: form.plantingDate || undefined,
          harvest_date: form.harvestDate || undefined,
          location_name: form.location,
          location_lat: form.lat,
          location_lng: form.lng,
          area_acres: form.acreage ? parseFloat(form.acreage) : undefined,
          soil_type: form.soilType,
        });
      }
      toast.success("Settings saved successfully.");
    } catch (err) {
      const { getApiErrorMessage } = await import("../lib/api");
      toast.error(getApiErrorMessage(err, "Failed to save settings"));
    } finally {
      setSaving(false);
    }
  }

  function handleDiscard() {
    setForm({
      farmName: "Nashik Mustard Farm",
      location: "Nashik, Maharashtra",
      lat: 19.9975,
      lng: 73.7898,
      acreage: "125.5",
      soilType: "alluvial",
      elevation: "600m ASL",
      crop: "mustard",
      variety: "variety1",
      irrigationMethod: "",
      plantingDate: "2023-11-15",
      harvestDate: "2024-03-20",
    });
    setNotifications({
      pushCritical: true,
      pushDaily: true,
      pushSystem: false,
      emailWeekly: true,
      emailBilling: true,
      whatsappUrgent: false,
      smsAlerts: true,
    });
  }

  return (
    <div className="max-w-6xl mx-auto pb-2xl">
      <div className="mb-xl">
        <h1 className="font-headline-lg text-headline-lg font-bold text-on-surface">Farm Settings</h1>
        <p className="text-on-surface-variant font-body-md mt-xs">
          Manage parameters for <span className="font-semibold text-primary">Nashik Mustard Farm</span>
        </p>
      </div>

      <div className="flex gap-lg border-b border-outline-variant mb-xl overflow-x-auto">
        {TABS.map((t) => {
          const active = tab === t.key;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-sm py-md font-label-md whitespace-nowrap flex items-center gap-sm border-b-2 transition-colors ${active
                  ? "text-primary border-primary"
                  : "text-on-surface-variant hover:text-on-surface border-transparent"
                }`}
            >
              <span className="material-symbols-outlined text-[20px]">{t.icon}</span>
              {t.label}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSave}>
        {tab === "general" && (
          <div className="grid grid-cols-12 gap-lg items-start">
            <div className="col-span-12 lg:col-span-7 space-y-lg">
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">badge</span>
                  <div>
                    <h2 className="font-headline-sm text-headline-sm">Farm Identity</h2>
                    <p className="text-body-sm text-on-surface-variant">Core farm details for your prediction model and dashboard.</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-lg mb-lg">
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Farm Name</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="text"
                      value={form.farmName}
                      onChange={(e) => update("farmName", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Location / District</label>
                    <div className="flex gap-sm">
                      <input
                        className="flex-1 bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                        type="text"
                        value={form.location}
                        onChange={(e) => update("location", e.target.value)}
                      />
                      <button
                        type="button"
                        onClick={handleDetectLocation}
                        className="flex items-center gap-xs bg-surface-container-high hover:bg-surface-container-highest text-primary border border-outline-variant rounded-lg px-md py-sm transition-colors text-label-sm font-label-sm font-bold active:scale-[0.98]"
                        title="Detect GPS from browser"
                      >
                        <span className="material-symbols-outlined text-[20px]">my_location</span>
                        GPS
                      </button>
                    </div>
                  </div>
                </div>

                <div className="relative w-full h-48 rounded-xl overflow-hidden border border-outline-variant mb-md bg-surface-container-highest flex">
                  <InteractiveGoogleMap
                    center={{ lat: form.lat || 19.9975, lng: form.lng || 73.7898 }}
                    zoom={10}
                    onLocationSelect={handleMapLocationSelect}
                  />
                </div>

                <div className="flex flex-col gap-md p-md bg-surface-container-low rounded-lg border border-outline-variant/50">
                  <div className="flex items-center justify-between gap-sm">
                    <div className="flex items-center gap-sm">
                      <span className="material-symbols-outlined text-on-surface-variant text-[20px]">explore</span>
                      <span className="font-label-md text-on-surface-variant uppercase">Coordinates</span>
                    </div>
                    <div className="font-body-sm font-mono text-on-surface">
                      {form.lat ? `${form.lat.toFixed(4)}° N` : "19.9975° N"}, {form.lng ? `${form.lng.toFixed(4)}° E` : "73.7898° E"}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-lg">
                    <div>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">Coordinates</p>
                      <p className="font-body-sm text-body-sm text-on-surface mt-xs">Lat: {form.lat.toFixed(4)}, Lng: {form.lng.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">Detected region</p>
                      <p className="font-body-sm text-body-sm text-on-surface mt-xs">{form.location}</p>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            <div className="col-span-12 lg:col-span-5 space-y-lg">
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">potted_plant</span>
                  <div>
                    <h2 className="font-headline-sm text-headline-sm">Farm Parameters</h2>
                    <p className="text-body-sm text-on-surface-variant">Crop and production settings used for your predictions.</p>
                  </div>
                </div>
                <div className="space-y-lg">
                  <Select
                    label="Crop"
                    value={form.crop}
                    onChange={(v) => update("crop", v)}
                    options={CROP_OPTIONS}
                    placeholder="Choose a crop"
                  />
                  <Select
                    label="Variety / Cultivar"
                    value={form.variety}
                    onChange={(v) => update("variety", v)}
                    options={VARIETY_OPTIONS}
                    placeholder="Choose variety"
                  />
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-lg">
                    <div>
                      <label className="block font-label-md text-on-surface-variant mb-sm">Planting Date</label>
                      <div className="relative">
                        <input
                          className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                          type="date"
                          value={form.plantingDate}
                          onChange={(e) => update("plantingDate", e.target.value)}
                        />
                        <span className="material-symbols-outlined absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">calendar_month</span>
                      </div>
                    </div>
                    <div>
                      <label className="block font-label-md text-on-surface-variant mb-sm">Expected Harvest</label>
                      <div className="relative">
                        <input
                          className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                          type="date"
                          value={form.harvestDate}
                          onChange={(e) => update("harvestDate", e.target.value)}
                        />
                        <span className="material-symbols-outlined absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">event_available</span>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">data_usage</span>
                  <div>
                    <h2 className="font-headline-sm text-headline-sm">Production Details</h2>
                    <p className="text-body-sm text-on-surface-variant">Key metrics for farm performance and crop yield.</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Total Acreage (ha)</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="number"
                      value={form.acreage}
                      onChange={(e) => update("acreage", e.target.value)}
                    />
                  </div>
                  <div>
                    <Select
                      label="Soil Type"
                      value={form.soilType}
                      onChange={(v) => update("soilType", v)}
                      options={SOIL_TYPES}
                      placeholder="Select soil type"
                    />
                  </div>
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Elevation</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="text"
                      value={form.elevation}
                      onChange={(e) => update("elevation", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Irrigation Method</label>
                    <Select
                      value={form.irrigationMethod}
                      onChange={(v) => update("irrigationMethod", v)}
                      options={[
                        { value: "drip", label: "Drip Irrigation" },
                        { value: "sprinkler", label: "Sprinkler" },
                        { value: "flood", label: "Flood Irrigation" },
                        { value: "rainfed", label: "Rainfed (no irrigation)" },
                      ]}
                      placeholder="Select method"
                    />
                  </div>
                </div>
              </section>
            </div>
          </div>
        )}

        {tab === "alerts" && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-lg">
            <div className="lg:col-span-3 space-y-lg">
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">notifications_active</span>
                  <h2 className="font-headline-sm text-headline-sm">Push Notifications</h2>
                  <span className="text-body-sm text-on-surface-variant ml-auto">Mobile & Web Browser</span>
                </div>
                <div className="space-y-md">
                  <ToggleSwitch
                    label="Critical Risk Alerts"
                    desc="Immediate alerts for pollination drops or pest spikes"
                    checked={notifications.pushCritical}
                    onChange={() => toggleNotif("pushCritical")}
                  />
                  <ToggleSwitch
                    label="Daily Summary"
                    desc="A morning briefing of today's pollination forecast"
                    checked={notifications.pushDaily}
                    onChange={() => toggleNotif("pushDaily")}
                  />
                  <ToggleSwitch
                    label="System Updates"
                    desc="New feature announcements and app maintenance"
                    checked={notifications.pushSystem}
                    onChange={() => toggleNotif("pushSystem")}
                  />
                </div>
              </section>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-lg">
                <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                  <div className="flex items-center gap-sm mb-md">
                    <span className="material-symbols-outlined text-primary">mail</span>
                    <h3 className="font-headline-sm text-headline-sm">Email Alerts</h3>
                  </div>
                  <div className="space-y-md">
                    <ToggleSwitch
                      label="Weekly Reports"
                      checked={notifications.emailWeekly}
                      onChange={() => toggleNotif("emailWeekly")}
                    />
                    <ToggleSwitch
                      label="Billing & Legal"
                      checked={notifications.emailBilling}
                      onChange={() => toggleNotif("emailBilling")}
                    />
                  </div>
                </section>

                <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                  <div className="flex items-center gap-sm mb-md">
                    <span className="material-symbols-outlined text-primary">chat</span>
                    <h3 className="font-headline-sm text-headline-sm">WhatsApp</h3>
                  </div>
                  <ToggleSwitch
                    label="Urgent Risk Escalation"
                    desc="Secondary channel for critical failures"
                    checked={notifications.whatsappUrgent}
                    onChange={() => toggleNotif("whatsappUrgent")}
                  />
                </section>
              </div>

              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm">
                  <div className="p-sm rounded-lg bg-primary-container/10 text-primary">
                    <span className="material-symbols-outlined">sms</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-headline-sm text-headline-sm">SMS Notifications</h3>
                    <p className="text-body-sm text-on-surface-variant">Real-time weather alerts via mobile carrier</p>
                  </div>
                  <ToggleSwitch
                    checked={notifications.smsAlerts}
                    onChange={() => toggleNotif("smsAlerts")}
                  />
                </div>
              </section>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm sticky top-4">
                <div className="flex items-center gap-sm mb-md">
                  <span className="px-md py-xs rounded-full bg-primary-container/10 text-primary font-label-sm text-label-sm">Live Preview</span>
                </div>
                <div className="rounded-2xl overflow-hidden border-2 border-outline-variant bg-[#1f1b17] shadow-lg mx-auto max-w-[260px]">
                  <div className="bg-[#1f1b17] px-md pt-lg pb-sm">
                    <div className="flex justify-between items-center mb-lg">
                      <span className="text-white/80 text-body-sm font-bold">9:41</span>
                      <div className="flex gap-xs text-white/60">
                        <span className="material-symbols-outlined text-[14px]">signal_cellular_alt</span>
                        <span className="material-symbols-outlined text-[14px]">wifi</span>
                        <span className="material-symbols-outlined text-[14px]">battery_full</span>
                      </div>
                    </div>
                    <div className="rounded-xl overflow-hidden" style={{ background: "linear-gradient(135deg, #2d5a27 0%, #8b6f3a 50%, #c4a265 100%)" }}>
                      <div className="px-md py-lg min-h-[280px] flex flex-col justify-end">
                        <div className="bg-white/95 backdrop-blur-sm rounded-xl p-md shadow-lg animate-[bounceIn_0.5s_ease-out]">
                          <div className="flex items-center gap-sm mb-xs">
                            <span className="material-symbols-outlined text-[16px] text-primary">eco</span>
                            <span className="text-label-sm text-primary font-bold">PolliSync</span>
                          </div>
                          <p className="text-body-sm text-on-surface font-medium">
                            High Pollination Risk detected in Sector B. Immediate action recommended.
                          </p>
                          <p className="text-label-xs text-on-surface-variant mt-xs">now</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between px-lg py-sm">
                      <span className="material-symbols-outlined text-white/60 text-[18px]">flashlight_on</span>
                      <span className="material-symbols-outlined text-white/60 text-[18px]">camera</span>
                    </div>
                  </div>
                </div>
                <p className="text-body-xs text-on-surface-variant text-center mt-md">
                  Example of an urgent risk escalation alert appearing on your lock screen.
                </p>
              </div>
            </div>
          </div>
        )}


        <div className="flex items-center justify-end gap-md mt-xl pt-lg border-t border-outline-variant">
          <button
            type="button"
            onClick={handleDiscard}
            className="px-xl py-sm font-label-md text-on-surface-variant hover:text-on-surface transition-colors active:scale-95"
          >
            Discard Changes
          </button>
          <button
            type="submit"
            disabled={saving}
            className="bg-primary text-on-primary px-xl py-sm rounded-lg font-label-md shadow-md hover:bg-opacity-90 transition-all active:scale-95 flex items-center gap-sm disabled:opacity-60"
          >
            {saving ? (
              <>
                <svg className="animate-spin h-5 w-5 text-on-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[20px]">save</span>
                Save Settings
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

function ToggleSwitch({ label, desc, checked, onChange }) {
  return (
    <label className="flex items-center justify-between gap-md cursor-pointer group">
      <div className="flex-1">
        <p className="font-label-md text-label-md text-on-surface">{label}</p>
        {desc && <p className="text-body-sm text-on-surface-variant">{desc}</p>}
      </div>
      <div className="relative">
        <input
          type="checkbox"
          className="sr-only peer"
          checked={checked}
          onChange={onChange}
        />
        <div className="w-11 h-6 rounded-full border border-outline-variant bg-surface-container-high peer-checked:bg-primary peer-checked:border-primary transition-colors cursor-pointer peer-focus:ring-2 peer-focus:ring-primary/20" />
        <div className="absolute top-[2px] left-[2px] w-5 h-5 rounded-full bg-white border border-outline-variant peer-checked:border-primary peer-checked:translate-x-5 transition-all shadow-sm pointer-events-none" />
      </div>
    </label>
  );
}
