import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function FarmSelector({ farms, selectedFarmId, onSelectFarm }) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  if (!farms || farms.length === 0) {
    return (
      <button
        onClick={() => navigate("/predict")}
        className="flex items-center gap-sm bg-primary/10 text-primary hover:bg-primary/20 px-md py-sm rounded-lg transition-colors"
      >
        <span className="material-symbols-outlined text-[18px]">add</span>
        <span className="font-label-md text-label-md">Create Farm</span>
      </button>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface px-md py-sm rounded-lg transition-colors min-w-[200px]"
      >
        <span className="material-symbols-outlined text-[18px] text-primary">
          farm
        </span>
        <span className="font-label-md text-label-md truncate flex-1 text-left">
          {selectedFarm?.name || "Select Farm"}
        </span>
        <span
          className={`material-symbols-outlined text-[18px] text-on-surface-variant transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        >
          expand_more
        </span>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-xs w-72 bg-surface border border-outline-variant rounded-xl shadow-lg z-50 overflow-hidden">
            <div className="p-xs">
              {farms.map((farm) => (
                <button
                  key={farm.id}
                  onClick={() => {
                    onSelectFarm(farm.id);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-md py-sm rounded-lg flex items-center gap-md transition-colors ${
                    farm.id === selectedFarmId
                      ? "bg-primary-container/10 text-primary font-bold"
                      : "text-on-surface hover:bg-surface-container-high"
                  }`}
                >
                  <span
                    className={`material-symbols-outlined text-[18px] ${
                      farm.id === selectedFarmId
                        ? "text-primary"
                        : "text-on-surface-variant"
                    }`}
                  >
                    {farm.id === selectedFarmId
                      ? "radio_button_checked"
                      : "radio_button_unchecked"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-label-md text-label-md truncate">
                      {farm.name}
                    </p>
                    <p className="text-body-sm text-on-surface-variant truncate">
                      {farm.crop_type}
                      {farm.district_slug &&
                        ` • ${farm.district_slug.charAt(0).toUpperCase() + farm.district_slug.slice(1)}`}
                    </p>
                  </div>
                  {farm.is_default && (
                    <span className="text-body-sm text-primary font-label-sm">
                      Default
                    </span>
                  )}
                </button>
              ))}
            </div>
            <div className="border-t border-outline-variant p-xs">
              <button
                onClick={() => {
                  navigate("/farms");
                  setIsOpen(false);
                }}
                className="w-full text-left px-md py-sm rounded-lg flex items-center gap-md text-on-surface-variant hover:bg-surface-container-high transition-colors"
              >
                <span className="material-symbols-outlined text-[18px]">
                  settings
                </span>
                <span className="font-label-md text-label-md">
                  Manage Farms
                </span>
              </button>
              <button
                onClick={() => {
                  navigate("/predict");
                  setIsOpen(false);
                }}
                className="w-full text-left px-md py-sm rounded-lg flex items-center gap-md text-primary hover:bg-primary-container/10 transition-colors"
              >
                <span className="material-symbols-outlined text-[18px]">
                  add
                </span>
                <span className="font-label-md text-label-md">
                  Add New Farm
                </span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
