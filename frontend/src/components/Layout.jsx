import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard", icon: "dashboard" },
  { path: "/predict", label: "New Prediction", icon: "add_circle" },
  { path: "/predictions", label: "History", icon: "history" },
  { path: "/chat", label: "AI Assistant", icon: "smart_toy" },
];

const PAGE_TITLES = {
  "/dashboard": "Dashboard",
  "/predict": "New Prediction",
  "/predictions": "Prediction History",
  "/chat": "AI Assistant",
};

const BOTTOM_NAV = [
  { path: "/support", label: "Support", icon: "help" },
  { path: "/account", label: "Account", icon: "person" },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  function isActive(path) {
    return location.pathname.startsWith(path);
  }

  function NavLink({ path, label, icon, isBottom }) {
    const active = isActive(path);
    const base = "flex items-center gap-md rounded-lg px-md py-sm transition-colors duration-200";
    const style = active
      ? "bg-primary-container/10 text-primary font-bold"
      : `${isBottom ? "" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"}`;
    return (
      <Link
        to={path}
        className={`${base} ${style} ${isBottom && !active ? "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high" : ""}`}
        onClick={() => setMobileOpen(false)}
      >
        <span className="material-symbols-outlined text-xl">{icon}</span>
        <span className="font-label-md text-label-md">{label}</span>
      </Link>
    );
  }

  return (
    <div className="text-on-surface bg-background flex h-screen overflow-hidden">
      <aside className={`bg-surface border-r border-outline-variant h-screen w-64 fixed left-0 top-0 flex flex-col p-md z-20 transition-transform lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center gap-sm px-sm mb-lg">
          <span className="material-symbols-outlined text-primary text-3xl filled">eco</span>
          <div className="flex flex-col">
            <span className="font-headline-md text-headline-md font-bold text-primary">PolliSync</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant">Agrotech Analytics</span>
          </div>
        </div>

        <Link
          to="/predict"
          className="bg-primary-container text-on-primary font-label-md text-label-md py-sm px-md rounded-lg flex items-center justify-center gap-sm mb-lg hover:bg-primary transition-colors"
          onClick={() => setMobileOpen(false)}
        >
          <span className="material-symbols-outlined">add</span>
          New Analysis
        </Link>

        <div className="flex flex-col gap-sm flex-1">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.path} {...item} />
          ))}
        </div>

        <div className="flex flex-col gap-sm border-t border-outline-variant pt-md mt-auto">
          {BOTTOM_NAV.map((item) => (
            <NavLink key={item.path} {...item} isBottom />
          ))}
          <button
            onClick={logout}
            className="flex items-center gap-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg px-md py-sm transition-colors duration-200 w-full text-left"
          >
            <span className="material-symbols-outlined text-xl">logout</span>
            <span className="font-label-md text-label-md">Logout</span>
          </button>
        </div>

        <button className="lg:hidden absolute top-4 right-4 p-1 rounded-lg hover:bg-surface-container" onClick={() => setMobileOpen(false)}>
          <span className="material-symbols-outlined">close</span>
        </button>
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-10 bg-black/30 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      <main className="ml-0 lg:ml-64 flex-1 flex flex-col h-screen overflow-y-auto bg-background">
        <header className="bg-surface/80 backdrop-blur-md border-b border-outline-variant flex justify-between items-center h-16 px-xl w-full sticky top-0 z-10">
          <div className="flex items-center gap-sm">
            <button className="lg:hidden p-2 rounded-lg hover:bg-surface-container mr-2" onClick={() => setMobileOpen(true)}>
              <span className="material-symbols-outlined text-on-surface">menu</span>
            </button>
            <span className="font-label-md text-label-md text-on-surface-variant hidden sm:block">
              {PAGE_TITLES[location.pathname] || "Dashboard"}
            </span>
            <span className="material-symbols-outlined text-outline text-sm hidden sm:block">chevron_right</span>
            <div className="flex items-center gap-xs hover:bg-surface-container-highest px-sm py-xs rounded-md transition-colors cursor-pointer">
              <span className="font-headline-sm text-headline-sm text-on-surface">{user?.full_name || "Farm"}</span>
              <span className="material-symbols-outlined text-outline">expand_more</span>
            </div>
          </div>
          <div className="flex items-center gap-md">
            <button className="text-on-surface-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 p-sm rounded-full hover:bg-surface-container-highest">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="text-on-surface-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 p-sm rounded-full hover:bg-surface-container-highest">
              <span className="material-symbols-outlined">help</span>
            </button>
            <div className="w-8 h-8 rounded-full bg-primary-container/20 border border-primary-container flex items-center justify-center overflow-hidden cursor-pointer">
              <span className="material-symbols-outlined text-primary text-sm">person</span>
            </div>
          </div>
        </header>
        <div className="p-xl flex-1 max-w-[1600px] mx-auto w-full">
          {children}
        </div>
      </main>
    </div>
  );
}
