import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getFarms, createFarm, deleteFarm } from "../lib/api";
import { useToast } from "../context/ToastContext";
import Card from "../components/Card";
import { CropSelector, LocationSelector } from "../components/ParameterForm";
import { EmptyState, ErrorState, DashboardSkeleton } from "../components/LoadingSkeleton";

const CROP_ICONS = {
  Mustard: "eco",
  Sunflower: "local_florist",
  Cotton: "filter_drama",
};

export default function FarmManagementPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const toast = useToast();
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    crop: "",
    location: "",
    area_acres: "",
    soil_type: "loamy",
    planting_date: "",
    harvest_date: "",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadFarms();
  }, []);

  useEffect(() => {
    if (searchParams.get("new") === "1") {
      setShowForm(true);
    }
  }, [searchParams]);

  async function loadFarms() {
    try {
      setLoading(true);
      const data = await getFarms();
      setFarms(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load farms");
    } finally {
      setLoading(false);
    }
  }

  async function handleAddFarm(e) {
    e.preventDefault();

    if (!form.name || !form.crop || !form.location || !form.area_acres) {
      toast.error("Please fill in all fields");
      return;
    }

    try {
      setSubmitting(true);
      await createFarm({
        name: form.name,
        crop: form.crop,
        location: form.location,
        area_acres: parseFloat(form.area_acres),
        soil_type: form.soil_type,
        planting_date: form.planting_date || null,
        harvest_date: form.harvest_date || null,
      });

      toast.success(`Farm "${form.name}" added successfully!`);
      setForm({ name: "", crop: "", location: "", area_acres: "", soil_type: "loamy", planting_date: "", harvest_date: "" });
      setShowForm(false);
      await loadFarms();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to add farm");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeleteFarm(farmId, farmName) {
    if (!confirm(`Delete farm "${farmName}"? This cannot be undone.`)) return;

    try {
      await deleteFarm(farmId);
      toast.success("Farm deleted");
      setFarms(farms.filter((f) => f.id !== farmId));
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to delete farm");
    }
  }

  if (loading) return <DashboardSkeleton />;
  if (error) return <ErrorState error={error} onRetry={loadFarms} />;

  return (
    <div className="space-y-lg">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-display text-display text-on-surface">Farm Management</h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-xs">
            Manage your farms and select one to view predictions
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-lg py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-bold hover:bg-primary/90 transition flex items-center gap-sm"
        >
          <span className="material-symbols-outlined">add</span>
          New Farm
        </button>
      </div>

      {/* Add Farm Form */}
      {showForm && (
        <Card header="Add New Farm">
          <form onSubmit={handleAddFarm} className="space-y-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              <div className="space-y-sm">
                <label className="block font-label-md text-label-md font-bold text-on-surface">
                  Farm Name
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g., South Plot, Organic Zone"
                  className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-on-surface font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  disabled={submitting}
                />
              </div>

              <div className="space-y-sm">
                <label className="block font-label-md text-label-md font-bold text-on-surface">
                  Area (acres)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={form.area_acres}
                  onChange={(e) => setForm({ ...form, area_acres: e.target.value })}
                  placeholder="e.g., 5.5"
                  className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-on-surface font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  disabled={submitting}
                />
              </div>
            </div>

            <CropSelector value={form.crop} onChange={(crop) => setForm({ ...form, crop })} disabled={submitting} />

            <LocationSelector value={form.location} onChange={(loc) => setForm({ ...form, location: loc })} disabled={submitting} />

            <div className="space-y-sm">
              <label className="block font-label-md text-label-md font-bold text-on-surface">
                Soil Type
              </label>
              <select
                value={form.soil_type}
                onChange={(e) => setForm({ ...form, soil_type: e.target.value })}
                disabled={submitting}
                className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-on-surface font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              >
                <option value="loamy">Loamy (balanced)</option>
                <option value="sandy">Sandy (well-draining)</option>
                <option value="clay">Clay (heavy)</option>
                <option value="silty">Silty (fertile)</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              <div className="space-y-sm">
                <label className="block font-label-md text-label-md font-bold text-on-surface">
                  Planting Date <span className="font-body-sm text-body-sm font-normal text-on-surface-variant">(optional)</span>
                </label>
                <input
                  type="date"
                  value={form.planting_date}
                  onChange={(e) => setForm({ ...form, planting_date: e.target.value })}
                  className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-on-surface font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  disabled={submitting}
                />
              </div>
              <div className="space-y-sm">
                <label className="block font-label-md text-label-md font-bold text-on-surface">
                  Expected Harvest <span className="font-body-sm text-body-sm font-normal text-on-surface-variant">(optional)</span>
                </label>
                <input
                  type="date"
                  value={form.harvest_date}
                  onChange={(e) => setForm({ ...form, harvest_date: e.target.value })}
                  className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-on-surface font-body-md focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                  disabled={submitting}
                />
              </div>
            </div>

            <div className="flex gap-md">
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 px-lg py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-bold hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? "Creating..." : "Create Farm"}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                disabled={submitting}
                className="flex-1 px-lg py-sm rounded-lg bg-surface-container text-on-surface font-label-md text-label-md font-bold hover:bg-surface-container/80 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
            </div>
          </form>
        </Card>
      )}

      {/* Farms Grid */}
      {farms.length === 0 ? (
        <EmptyState
          icon="agriculture"
          title="No farms yet"
          description="Create your first farm to start predicting pollination suitability"
          action={() => setShowForm(true)}
          actionLabel="Add Farm"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
          {farms.map((farm) => (
            <Card
              key={farm.id}
              variant="elevated"
              header={
                <div className="flex items-start gap-md w-full">
                  <div className={`p-md rounded-lg bg-primary-container/20 text-primary-container`}>
                    <span className="material-symbols-outlined">{CROP_ICONS[farm.crop] || "eco"}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-headline-sm text-headline-sm text-on-surface">{farm.name}</h3>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">{farm.crop}</p>
                  </div>
                </div>
              }
            >
              <div className="space-y-md">
                <div className="grid grid-cols-2 gap-md">
                  <div>
                    <p className="font-label-sm text-label-sm text-on-surface-variant">Location</p>
                    <p className="font-body-md text-body-md text-on-surface mt-xs">{farm.location}</p>
                  </div>
                  <div>
                    <p className="font-label-sm text-label-sm text-on-surface-variant">Area</p>
                    <p className="font-body-md text-body-md text-on-surface mt-xs">
                      {farm.area_acres} acres
                    </p>
                  </div>
                  <div>
                    <p className="font-label-sm text-label-sm text-on-surface-variant">Soil Type</p>
                    <p className="font-body-md text-body-md text-on-surface mt-xs capitalize">
                      {farm.soil_type}
                    </p>
                  </div>
                  <div>
                    <p className="font-label-sm text-label-sm text-on-surface-variant">PSI</p>
                    <p className="font-body-md text-body-md text-on-surface mt-xs">
                      {farm.latest_psi ? farm.latest_psi.toFixed(0) : "—"}
                    </p>
                  </div>
                </div>

                <div className="flex gap-md pt-md border-t border-outline-variant/50">
                  <button
                    onClick={() => navigate(`/dashboard?farm_id=${farm.id}`)}
                    className="flex-1 px-md py-sm rounded-lg bg-primary text-on-primary font-label-sm text-label-sm font-bold hover:bg-primary/90 transition flex items-center justify-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[18px]">dashboard</span>
                    View
                  </button>
                  <button
                    onClick={() => navigate(`/predict?farm_id=${farm.id}`)}
                    className="flex-1 px-md py-sm rounded-lg bg-secondary-container text-on-surface font-label-sm text-label-sm font-bold hover:bg-secondary-container/90 transition flex items-center justify-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[18px]">bolt</span>
                    Predict
                  </button>
                  <button
                    onClick={() => handleDeleteFarm(farm.id, farm.name)}
                    className="px-md py-sm rounded-lg bg-tertiary/10 text-tertiary font-label-sm text-label-sm font-bold hover:bg-tertiary/20 transition"
                    title="Delete farm"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
