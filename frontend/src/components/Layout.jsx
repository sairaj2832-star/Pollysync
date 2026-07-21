import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { useState, useEffect } from "react";
import FarmSelector from "./FarmSelector";
import { useFarm } from "../context/FarmContext";

const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard", icon: "dashboard" },
  { path: "/predict", label: "New Prediction", icon: "add_circle" },
  { path: "/predictions", label: "History", icon: "history" },
  { path: "/reports", label: "Analytics", icon: "analytics" },
  { path: "/farms", label: "My Farms", icon: "agriculture" },
  { path: "/crops", label: "Crop Guide", icon: "info" },
  { path: "/chat", label: "AI Assistant", icon: "smart_toy" },
  { path: "/settings", label: "Settings", icon: "settings" },
];

const PAGE_TITLES = {
  "/dashboard": "Dashboard",
  "/predict": "New Prediction",
  "/predictions": "Prediction History",
  "/chat": "AI Assistant",
  "/settings": "Settings",
  "/account": "Account",
  "/support": "Help & Support",
  "/farms": "Farm Management",
  "/notifications": "Notifications",
  "/crops": "Crop Suitability Guide",
  "/reports": "Analytics & Reports",
};

const BOTTOM_NAV = [
  { path: "/support", label: "Support", icon: "help" },
  { path: "/account", label: "Account", icon: "person" },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const { farms, selectedFarmId, selectFarm, loadingFarms } = useFarm();

  useEffect(() => {
    if (user && !user.has_onboarded && location.pathname !== "/onboarding") {
      navigate("/onboarding");
    }
  }, [user, location.pathname, navigate]);

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === "Escape") { setMobileOpen(false); setMoreOpen(false); }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  function isActive(path) {
    return location.pathname.startsWith(path);
  }

  function NavLink({ path, label, icon, isBottom }) {
    const active = isActive(path);
    const base = "flex items-center gap-md rounded-lg px-md py-sm transition-all duration-200";
    const style = active
      ? "bg-primary-container/10 text-primary font-bold sidebar-link-active"
      : `${isBottom ? "" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"}`;
    return (
      <Link
        to={path}
        className={`${base} ${style} ${isBottom && !active ? "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high" : ""}`}
        onClick={() => { setMobileOpen(false); setMoreOpen(false); }}
      >
        <span className={`material-symbols-outlined text-xl transition-transform duration-200 ${active ? "scale-110" : ""}`}>{icon}</span>
        <span className="font-label-md text-label-md">{label}</span>
      </Link>
    );
  }

  if (user && !user.has_onboarded && location.pathname !== "/onboarding") {
    return null;
  }

  return (
    <div className="text-on-surface bg-background flex h-screen overflow-hidden">
      <aside className={`bg-surface/90 backdrop-blur-md border-r border-outline-variant h-screen w-64 fixed left-0 top-0 flex flex-col overflow-hidden p-md z-20 transition-transform lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center gap-sm px-sm mb-lg">
          <img src="/PS.png" alt="PolliSync logo" className="h-9 w-9 rounded-lg object-contain" />
          <div className="flex flex-col">
            <span className="font-headline-md text-headline-md font-bold text-primary">PolliSync</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant">Agrotech Analytics</span>
          </div>
        </div>

        <div className="hide-scrollbar min-h-0 flex-1 overflow-y-auto pr-1">
          <div className="flex flex-col gap-sm">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.path} {...item} />
            ))}
          </div>

          <div className="mt-md border-t border-outline-variant pt-md">
            {BOTTOM_NAV.map((item) => (
              <NavLink key={item.path} {...item} isBottom />
            ))}
            <button
              onClick={logout}
              className="mt-md flex w-full items-center gap-md rounded-lg px-md py-sm text-left text-on-surface-variant transition-colors duration-200 hover:bg-surface-container-high hover:text-on-surface"
            >
              <span className="material-symbols-outlined text-xl">logout</span>
              <span className="font-label-md text-label-md">Logout</span>
            </button>
          </div>
        </div>

        <button aria-label="Close navigation" className="lg:hidden absolute top-4 right-4 min-h-11 min-w-11 p-2 rounded-lg hover:bg-surface-container" onClick={() => setMobileOpen(false)}>
          <span className="material-symbols-outlined">close</span>
        </button>
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-10 bg-black/30 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      <main className="ml-0 lg:ml-64 flex-1 flex flex-col h-screen overflow-y-auto bg-background pb-20 lg:pb-0">
        <header className="bg-surface/80 backdrop-blur-md border-b border-outline-variant flex justify-between items-center h-16 px-xl w-full sticky top-0 z-30">
          <div className="flex items-center gap-sm">
            <button aria-label="Open navigation" className="lg:hidden min-h-11 min-w-11 p-2 rounded-lg hover:bg-surface-container mr-2" onClick={() => setMobileOpen(true)}>
              <span className="material-symbols-outlined text-on-surface">menu</span>
            </button>
            <span className="font-label-md text-label-md text-on-surface-variant hidden sm:block">
              {PAGE_TITLES[location.pathname] || "Dashboard"}
            </span>
            <span className="material-symbols-outlined text-outline text-sm hidden sm:block">chevron_right</span>
            {!loadingFarms && (
              <FarmSelector
                farms={farms}
                selectedFarmId={selectedFarmId}
                onSelectFarm={selectFarm}
              />
            )}
          </div>
          <div className="flex items-center gap-md">
            <button
              onClick={toggle}
              className="text-on-surface-variant hover:text-primary transition-colors p-sm rounded-full hover:bg-surface-container-highest"
              aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
              title={dark ? "Switch to light mode" : "Switch to dark mode"}
            >
              <span className="material-symbols-outlined">{dark ? "light_mode" : "dark_mode"}</span>
            </button>
            <button 
              onClick={() => navigate("/notifications")}
              className="relative text-on-surface-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 p-sm rounded-full hover:bg-surface-container-highest"
              aria-label="Notifications"
              title="Notifications"
            >
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-tertiary rounded-full animate-pulse-dot" />
            </button>
          </div>
        </header>
        <div className="p-md sm:p-xl flex-1 max-w-[1600px] mx-auto w-full">
          {children}
        </div>
      </main>

      <nav aria-label="Primary mobile navigation" className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-surface/95 backdrop-blur border-t border-outline-variant px-1 pb-[env(safe-area-inset-bottom)]">
        <div className="grid grid-cols-5 max-w-lg mx-auto">
          {[...NAV_ITEMS.slice(0, 3), NAV_ITEMS[6]].map((item) => {
            const active = isActive(item.path);
            return <Link key={item.path} to={item.path} className={`min-h-16 flex flex-col items-center justify-center gap-1 text-[11px] ${active ? "text-primary font-bold" : "text-on-surface-variant"}`}>
              <span className="material-symbols-outlined text-[22px]">{item.icon}</span>{item.label === "New Prediction" ? "Predict" : item.label === "AI Assistant" ? "Assistant" : item.label}
            </Link>;
          })}
          <button aria-label="Open more navigation options" aria-expanded={moreOpen} onClick={() => setMoreOpen(true)} className="min-h-16 flex flex-col items-center justify-center gap-1 text-[11px] text-on-surface-variant">
            <span className="material-symbols-outlined text-[22px]">more_horiz</span>More
          </button>
        </div>
      </nav>
      {moreOpen && <div className="lg:hidden fixed inset-0 z-50 bg-black/40 flex items-end" onClick={() => setMoreOpen(false)}>
        <section role="dialog" aria-modal="true" aria-label="More navigation" className="w-full bg-surface rounded-t-2xl p-lg pb-8 animate-fade-in-up" onClick={(event) => event.stopPropagation()}>
          <div className="w-10 h-1 bg-outline-variant rounded-full mx-auto mb-lg" />
          <div className="grid grid-cols-2 gap-sm">
            {[...NAV_ITEMS.slice(3, 6), ...NAV_ITEMS.slice(7), ...BOTTOM_NAV].map((item) => <NavLink key={item.path} {...item} />)}
            <button onClick={logout} className="min-h-11 flex items-center gap-md rounded-lg px-md py-sm text-left text-on-surface-variant hover:bg-surface-container-high"><span className="material-symbols-outlined">logout</span>Logout</button>
          </div>
        </section>
      </div>}
    </div>
  );
}
