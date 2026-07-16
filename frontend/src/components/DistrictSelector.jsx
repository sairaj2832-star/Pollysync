import { useState } from "react";
import { useDistricts } from "../context/DistrictContext";

export default function DistrictSelector({ value, onChange, disabled = false }) {
  const { districts, loading, error } = useDistricts();
  const [search, setSearch] = useState("");

  const filtered = search.trim()
    ? districts.filter(
        (d) =>
          d.name.toLowerCase().includes(search.toLowerCase()) ||
          d.slug.toLowerCase().includes(search.toLowerCase())
      )
    : districts;

  const selected = districts.find((d) => d.slug === value);

  if (loading) {
    return (
      <div className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface text-body-md text-on-surface-variant">
        Loading districts...
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full px-md py-sm rounded-lg border border-error bg-error-container text-body-md text-on-error-container">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-sm">
      <label className="block font-label-md text-label-md text-on-surface-variant">
        Select District
      </label>
      <div className="relative">
        <span className="absolute left-md top-1/2 -translate-x-1/2 material-symbols-outlined text-on-surface-variant text-[18px]">
          search
        </span>
        <input
          type="text"
          placeholder="Search districts..."
          className="w-full pl-xl pr-md py-sm rounded-lg border border-outline-variant bg-surface text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          disabled={disabled}
        />
      </div>

      <div className="max-h-60 overflow-y-auto space-y-xs rounded-xl border border-outline-variant bg-surface p-xs">
                {filtered.length === 0 ? (
                  <div className="text-center py-lg">
                    <p className="text-body-sm text-on-surface-variant mb-sm">No districts match "{search}"</p>
                    <button
                      type="button"
                      onClick={() => setSearch("")}
                      className="text-primary text-body-sm font-medium hover:underline"
                    >
                      Clear search
                    </button>
                  </div>
        ) : (
          filtered.map((district) => {
            const isSelected = value === district.slug;
            return (
              <button
                key={district.slug}
                type="button"
                onClick={() => {
                  onChange(district.slug);
                  setSearch("");
                }}
                disabled={disabled}
                className={`w-full text-left px-md py-sm rounded-lg flex items-center gap-md transition-colors ${
                  isSelected
                    ? "bg-primary-container/10 text-primary font-bold"
                    : "text-on-surface hover:bg-surface-container-high"
                } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
              >
                <span
                  className={`material-symbols-outlined text-[18px] ${
                    isSelected ? "text-primary" : "text-on-surface-variant"
                  }`}
                >
                  {isSelected ? "radio_button_checked" : "location_on"}
                </span>
                <div className="flex-1">
                  <span className="font-label-md text-label-md">
                    {district.name}
                  </span>
                  <span className="text-body-sm text-on-surface-variant ml-xs">
                    ({district.state})
                  </span>
                </div>
                {isSelected && (
                  <span className="material-symbols-outlined text-[18px] text-primary">
                    check
                  </span>
                )}
              </button>
            );
          })
        )}
      </div>

      {selected && (
        <div className="bg-surface border border-outline-variant rounded-xl p-md space-y-sm">
          <div className="flex items-center gap-sm text-primary">
            <span className="material-symbols-outlined text-[18px]">
              location_on
            </span>
            <span className="font-label-md text-label-md font-bold">
              Selected District
            </span>
          </div>
          <p className="font-headline-sm text-headline-sm text-on-surface">
            {selected.name} District
          </p>
          <p className="text-body-sm text-on-surface-variant">
            {selected.state}, India
          </p>
          <div className="border-t border-outline-variant/50 pt-sm mt-sm flex gap-lg text-body-sm">
            <span className="font-mono text-on-surface-variant">
              {selected.centroid_lat.toFixed(4)} N
            </span>
            <span className="font-mono text-on-surface-variant">
              {selected.centroid_lng.toFixed(4)} E
            </span>
          </div>
          <p className="text-body-sm text-on-surface-variant">
            <span className="material-symbols-outlined text-[14px] inline mr-xs">
              radius
            </span>
            Map restricted to {selected.radius_km} km radius
          </p>
        </div>
      )}
    </div>
  );
}
