import { useState, useRef, useEffect } from "react";

export default function Select({
  value,
  onChange,
  options = [],
  placeholder = "Select...",
  disabled = false,
  className = "",
  label,
  icon,
  error,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selected = options.find((o) => (o.value ?? o) === value);

  return (
    <div className={`relative ${className}`} ref={ref}>
      {label && (
        <label className="block font-label-md text-label-md text-on-surface-variant mb-sm">
          {label}
        </label>
      )}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen(!open)}
        className={`w-full flex items-center gap-md px-md py-sm rounded-lg border text-body-md text-left transition-all outline-none ${
          error
            ? "border-tertiary focus:ring-2 focus:ring-tertiary/20"
            : "border-outline-variant focus:ring-2 focus:ring-primary/20 focus:border-primary"
        } ${
          selected
            ? "bg-surface text-on-surface"
            : "bg-surface text-on-surface-variant/60"
        } ${
          disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:border-primary/50"
        }`}
      >
        {icon && selected && (
          <span className="material-symbols-outlined text-[18px] text-on-surface-variant">
            {icon}
          </span>
        )}
        <span className="flex-1 truncate">
          {selected ? (selected.label ?? selected.value ?? selected) : placeholder}
        </span>
        <span className={`material-symbols-outlined text-[18px] text-on-surface-variant transition-transform ${open ? "rotate-180" : ""}`}>
          expand_more
        </span>
      </button>
      {open && (
        <div className="absolute z-50 mt-xs w-full bg-surface border border-outline-variant rounded-xl shadow-[0_4px_16px_rgba(0,0,0,0.1)] py-xs max-h-60 overflow-y-auto">
          <button
            type="button"
            onClick={() => {
              onChange("");
              setOpen(false);
            }}
            className={`w-full text-left px-md py-sm text-body-md transition-colors ${
              !value
                ? "bg-primary-container/10 text-primary font-bold"
                : "text-on-surface-variant hover:bg-surface-container-high"
            }`}
          >
            {placeholder}
          </button>
          {options.map((opt) => {
            const optValue = opt.value ?? opt;
            const optLabel = opt.label ?? opt;
            const optIcon = opt.icon;
            const isSelected = optValue === value;
            return (
              <button
                key={optValue}
                type="button"
                onClick={() => {
                  onChange(optValue);
                  setOpen(false);
                }}
                className={`w-full flex items-center gap-md text-left px-md py-sm text-body-md transition-colors ${
                  isSelected
                    ? "bg-primary-container/10 text-primary font-bold"
                    : "text-on-surface hover:bg-surface-container-high"
                }`}
              >
                {optIcon && (
                  <span className="material-symbols-outlined text-[18px] text-on-surface-variant">
                    {optIcon}
                  </span>
                )}
                <span className="flex-1 truncate">{optLabel}</span>
                {isSelected && (
                  <span className="material-symbols-outlined text-[18px] text-primary">check</span>
                )}
              </button>
            );
          })}
        </div>
      )}
      {error && (
        <p className="mt-xs text-body-sm text-tertiary">{error}</p>
      )}
    </div>
  );
}
