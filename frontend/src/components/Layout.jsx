import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard" },
  { path: "/predict", label: "Predict" },
  { path: "/farms", label: "Farms" },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="hidden w-64 flex-col border-r border-slate-200 bg-white p-6 lg:flex">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold text-leaf-700">
          <span className="text-2xl">✿</span>
          PolliSync
        </Link>
        <nav className="mt-10 flex flex-col gap-2">
          {NAV_ITEMS.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                location.pathname.startsWith(path)
                  ? "bg-leaf-50 text-leaf-700"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto border-t border-slate-100 pt-4">
          <p className="text-sm font-medium text-slate-700">{user?.full_name || "Guest"}</p>
          <button
            onClick={logout}
            className="mt-2 text-sm font-semibold text-red-500 hover:text-red-700"
          >
            Log out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6 lg:p-8">{children}</main>
    </div>
  );
}
