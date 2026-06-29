import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const FEATURES = [
  {
    title: "Flowering Forecasts",
    text: "Know the exact flowering window for your crops based on weather, location, and crop type.",
    icon: "🗓️",
  },
  {
    title: "Pollination Score",
    text: "Get a 0-100 Pollination Suitability Index (PSI) with clear risk levels.",
    icon: "🛡️",
  },
  {
    title: "AI Advice",
    text: "Receive actionable, crop-specific recommendations powered by AI.",
    icon: "✨",
  },
];

const CROPS = [
  { name: "Mustard", emoji: "🌼" },
  { name: "Wheat", emoji: "🌾" },
  { name: "Sunflower", emoji: "🌻" },
  { name: "Rice", emoji: "🌱" },
  { name: "Cotton", emoji: "☁️" },
];

export default function HomePage() {
  const { token } = useAuth();

  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-br from-leaf-950 via-leaf-700 to-emerald-500 pb-24 pt-16">
        <div className="mx-auto max-w-6xl px-6 lg:px-8">
          <nav className="flex items-center justify-between text-white">
            <Link to="/" className="flex items-center gap-3 text-xl font-bold">
              <span className="grid h-10 w-10 place-items-center rounded-full bg-white/15 text-2xl">
                ✿
              </span>
              PolliSync
            </Link>
            <div className="flex gap-4">
              {token ? (
                <Link
                  to="/dashboard"
                  className="rounded-xl bg-white px-5 py-2 font-bold text-leaf-700 transition hover:-translate-y-0.5"
                >
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="rounded-xl bg-white/15 px-5 py-2 font-semibold text-white transition hover:bg-white/25"
                  >
                    Log in
                  </Link>
                  <Link
                    to="/register"
                    className="rounded-xl bg-pollen px-5 py-2 font-bold text-slate-950 transition hover:-translate-y-0.5"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </nav>

          <div className="mt-20 max-w-3xl text-white">
            <p className="mb-4 font-semibold uppercase tracking-[0.22em] text-emerald-200">
              Pollination intelligence for better timing
            </p>
            <h1 className="text-5xl font-black leading-tight sm:text-6xl">
              Know Before Your Crops Flower
            </h1>
            <p className="mt-6 text-lg leading-8 text-emerald-50/90">
              AI-powered pollination forecasts for Indian farmers. Get flowering predictions,
              pollination suitability scores, and actionable recommendations.
            </p>
            {!token && (
              <Link
                to="/register"
                className="mt-8 inline-flex rounded-xl bg-pollen px-8 py-3 font-bold text-slate-950 shadow-soft transition hover:-translate-y-0.5"
              >
                Get Started
              </Link>
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-20 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft"
            >
              <span className="text-3xl">{f.icon}</span>
              <h3 className="mt-4 text-xl font-black text-slate-900">{f.title}</h3>
              <p className="mt-2 leading-7 text-slate-600">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white py-20">
        <div className="mx-auto max-w-6xl px-6 lg:px-8">
          <h2 className="text-center text-2xl font-black text-slate-900">
            Supported Crops
          </h2>
          <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-5">
            {CROPS.map((c) => (
              <div
                key={c.name}
                className="rounded-2xl border border-slate-100 bg-slate-50 p-6 text-center"
              >
                <span className="text-4xl">{c.emoji}</span>
                <p className="mt-3 font-bold text-slate-700">{c.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white py-8 text-center text-sm text-slate-500">
        <p>PolliSync &mdash; AI-Based Crop Pollination Suitability System</p>
        <p className="mt-1">Built by 4 SY CSE-AI Students</p>
      </footer>
    </div>
  );
}
