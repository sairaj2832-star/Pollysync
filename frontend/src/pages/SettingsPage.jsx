import { useState } from "react";
import { useToast } from "../context/ToastContext";

const TABS = [
  { key: "general", label: "General", icon: "info" },
  { key: "crop", label: "Crop Configuration", icon: "psychology" },
  { key: "alerts", label: "Alerts & Notifications", icon: "notifications_active" },
  { key: "team", label: "Team", icon: "group" },
];

export default function SettingsPage() {
  const toast = useToast();
  const [tab, setTab] = useState("general");
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    farmName: "Nashik Mustard Farm",
    location: "Nashik, Maharashtra",
    acreage: "125.5",
    soilType: "alluvial",
    elevation: "600m ASL",
    crop: "mustard",
    plantingDate: "2023-11-15",
    harvestDate: "2024-03-20",
  });

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    // TODO: connect to backend
    await new Promise((r) => setTimeout(r, 1200));
    setSaving(false);
    toast.success("Settings saved successfully.");
  }

  function handleDiscard() {
    setForm({
      farmName: "Nashik Mustard Farm",
      location: "Nashik, Maharashtra",
      acreage: "125.5",
      soilType: "alluvial",
      elevation: "600m ASL",
      crop: "mustard",
      plantingDate: "2023-11-15",
      harvestDate: "2024-03-20",
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

      {/* Tabs */}
      <div className="flex gap-lg border-b border-outline-variant mb-xl overflow-x-auto">
        {TABS.map((t) => {
          const active = tab === t.key;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-sm py-md font-label-md whitespace-nowrap flex items-center gap-sm border-b-2 transition-colors ${
                active
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
            <div className="col-span-12 lg:col-span-8 space-y-lg">
              {/* Farm Identity */}
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">badge</span>
                  <h2 className="font-headline-sm text-headline-sm">Farm Identity</h2>
                </div>
                <div className="grid grid-cols-2 gap-lg mb-lg">
                  <div className="col-span-2 md:col-span-1">
                    <label className="block font-label-md text-on-surface-variant mb-sm">Farm Name</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="text"
                      value={form.farmName}
                      onChange={(e) => update("farmName", e.target.value)}
                    />
                  </div>
                  <div className="col-span-2 md:col-span-1">
                    <label className="block font-label-md text-on-surface-variant mb-sm">Location/District</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="text"
                      value={form.location}
                      onChange={(e) => update("location", e.target.value)}
                    />
                  </div>
                </div>
                <div className="relative w-full h-48 rounded-xl overflow-hidden border border-outline-variant mb-md bg-surface-container-highest flex items-center justify-center">
                  <div className="flex flex-col items-center text-on-surface-variant/60">
                    <span className="material-symbols-outlined text-4xl">map</span>
                    <span className="font-body-sm text-body-sm mt-xs">Map view</span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-md bg-surface-container-low rounded-lg border border-outline-variant/50">
                  <div className="flex items-center gap-sm">
                    <span className="material-symbols-outlined text-on-surface-variant text-[20px]">explore</span>
                    <span className="font-label-md text-on-surface-variant uppercase">Coordinates</span>
                  </div>
                  <div className="font-body-sm font-mono text-on-surface">20.0050° N, 73.7900° E</div>
                </div>
              </section>

              {/* Site Metadata */}
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">data_usage</span>
                  <h2 className="font-headline-sm text-headline-sm">Site Metadata</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Total Acreage (ha)</label>
                    <div className="relative">
                      <input
                        className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all pr-xl"
                        type="number"
                        value={form.acreage}
                        onChange={(e) => update("acreage", e.target.value)}
                      />
                      <span className="absolute right-md top-1/2 -translate-y-1/2 text-outline font-label-sm">ha</span>
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Soil Type</label>
                    <select
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all appearance-none cursor-pointer"
                      value={form.soilType}
                      onChange={(e) => update("soilType", e.target.value)}
                    >
                      <option value="black">Black Soil (Regur)</option>
                      <option value="alluvial">Alluvial</option>
                      <option value="red">Red and Yellow</option>
                      <option value="laterite">Laterite</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Elevation (m)</label>
                    <input
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                      type="text"
                      value={form.elevation}
                      onChange={(e) => update("elevation", e.target.value)}
                    />
                  </div>
                </div>
              </section>
            </div>

            {/* Right Column */}
            <div className="col-span-12 lg:col-span-4 space-y-lg">
              <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
                <div className="flex items-center gap-sm mb-lg">
                  <span className="material-symbols-outlined text-primary">potted_plant</span>
                  <h2 className="font-headline-sm text-headline-sm">Crop Configuration</h2>
                </div>
                <div className="space-y-md">
                  <div>
                    <label className="block font-label-md text-on-surface-variant mb-sm">Select Crop</label>
                    <select
                      className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-sm font-body-md focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all appearance-none cursor-pointer"
                      value={form.crop}
                      onChange={(e) => update("crop", e.target.value)}
                    >
                      <option value="mustard">Mustard (Brassica juncea)</option>
                      <option value="sunflower">Sunflower</option>
                      <option value="wheat">Wheat</option>
                      <option value="cotton">Cotton</option>
                    </select>
                  </div>
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
              </section>
            </div>
          </div>
        )}

        {tab === "crop" && (
          <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm text-center py-3xl">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">psychology</span>
            <p className="font-body-md text-body-md text-on-surface-variant mt-md">Crop configuration settings</p>
          </div>
        )}

        {tab === "alerts" && (
          <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm text-center py-3xl">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">notifications_active</span>
            <p className="font-body-md text-body-md text-on-surface-variant mt-md">Alert and notification preferences</p>
          </div>
        )}

        {tab === "team" && (
          <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm text-center py-3xl">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">group</span>
            <p className="font-body-md text-body-md text-on-surface-variant mt-md">Team management</p>
          </div>
        )}

        {/* Bottom Actions */}
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
