import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function FarmSelector({ farms, selectedFarmId, onSelectFarm, showCreateAction = true }) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const selectedFarm = farms.find((farm) => String(farm.id) === String(selectedFarmId));

  if (!farms || farms.length === 0) {
    return (
      <button
        onClick={() => navigate("/farms?new=1")}
        className="flex items-center gap-sm rounded-lg bg-primary/10 px-md py-sm text-primary transition-colors hover:bg-primary/20"
      >
        <span className="material-symbols-outlined text-[18px]">add</span>
        <span className="font-label-md text-label-md">Add Farm</span>
      </button>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex min-h-11 min-w-[200px] items-center gap-sm rounded-lg bg-surface-container-high px-md py-sm text-on-surface transition-colors hover:bg-surface-container-highest"
        aria-haspopup="menu"
        aria-expanded={isOpen}
      >
        <span className="material-symbols-outlined text-[18px] text-primary">farm</span>
        <span className="font-label-md text-label-md flex-1 truncate text-left">
          {selectedFarm?.name || "Select Farm"}
        </span>
        <span className={`material-symbols-outlined text-[18px] text-on-surface-variant transition-transform ${isOpen ? "rotate-180" : ""}`}>
          expand_more
        </span>
      </button>

      {isOpen && (
        <>
          <button className="fixed inset-0 z-40 cursor-default" aria-label="Close farm menu" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-full z-50 mt-xs w-72 overflow-hidden rounded-xl border border-outline-variant bg-surface shadow-lg" role="menu">
            <div className="p-xs">
              {farms.map((farm) => {
                const active = String(farm.id) === String(selectedFarmId);
                const meta = [farm.crop_type, farm.district_slug ? farm.district_slug.charAt(0).toUpperCase() + farm.district_slug.slice(1) : null].filter(Boolean).join(" - ");

                return (
                  <button
                    key={farm.id}
                    onClick={() => {
                      onSelectFarm(farm.id);
                      setIsOpen(false);
                    }}
                    className={`flex w-full items-center gap-md rounded-lg px-md py-sm text-left transition-colors ${active ? "bg-primary-container/10 font-bold text-primary" : "text-on-surface hover:bg-surface-container-high"}`}
                    role="menuitem"
                  >
                    <span className={`material-symbols-outlined text-[18px] ${active ? "text-primary" : "text-on-surface-variant"}`}>
                      {active ? "radio_button_checked" : "radio_button_unchecked"}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-label-md text-label-md truncate">{farm.name}</p>
                      <p className="text-body-sm text-on-surface-variant truncate">{meta}</p>
                    </div>
                    {farm.is_default && <span className="text-body-sm font-label-sm text-primary">Default</span>}
                  </button>
                );
              })}
            </div>
            <div className="border-t border-outline-variant p-xs">
              <button
                onClick={() => {
                  navigate("/farms");
                  setIsOpen(false);
                }}
                className="flex w-full items-center gap-md rounded-lg px-md py-sm text-left text-on-surface-variant transition-colors hover:bg-surface-container-high"
                role="menuitem"
              >
                <span className="material-symbols-outlined text-[18px]">settings</span>
                <span className="font-label-md text-label-md">Manage Farms</span>
              </button>
              {showCreateAction && (
                <button
                  onClick={() => {
                    navigate("/farms?new=1");
                    setIsOpen(false);
                  }}
                  className="flex w-full items-center gap-md rounded-lg px-md py-sm text-left text-primary transition-colors hover:bg-primary-container/10"
                  role="menuitem"
                >
                  <span className="material-symbols-outlined text-[18px]">add</span>
                  <span className="font-label-md text-label-md">Create Farm</span>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
