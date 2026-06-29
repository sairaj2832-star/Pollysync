import { useEffect, useState } from "react";
import { getHealth } from "./lib/api";

const features = [
  {
    title: "Flowering forecast",
    text: "Estimate the crop flowering window from seasonal and environmental features.",
  },
  {
    title: "Pollination score",
    text: "Turn weather, crop health, pollen, and pollinator signals into a clear PSI.",
  },
  {
    title: "Practical guidance",
    text: "Translate model output into short actions a farmer can use in the field.",
  },
];

export default function App() {
  const [apiState, setApiState] = useState("checking");

  useEffect(() => {
    let active = true;

    getHealth()
      .then(() => active && setApiState("online"))
      .catch(() => active && setApiState("offline"));

    return () => {
      active = false;
    };
  }, []);

  const statusText = {
    checking: "Checking API",
    online: "API online",
    offline: "API offline",
  }[apiState];

  return (
    <main className="min-h-screen overflow-hidden bg-leaf-50 text-slate-900">
      <div className="absolute inset-x-0 top-0 -z-0 h-96 bg-gradient-to-br from-leaf-950 via-leaf-700 to-emerald-500" />

      <section className="relative mx-auto max-w-6xl px-6 pb-16 pt-8 lg:px-8">
        <nav className="flex items-center justify-between text-white">
          <a className="flex items-center gap-3 text-xl font-bold" href="/">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-white/15 text-2xl">
              ✿
            </span>
            PolliSync
          </a>
          <span
            className={"rounded-full px-3 py-1 text-sm " + (
              apiState === "online"
                ? "bg-emerald-300/20 text-emerald-50"
                : "bg-white/15 text-white"
            )}
          >
            {statusText}
          </span>
        </nav>

        <div className="grid items-center gap-12 pb-24 pt-20 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="text-white">
            <p className="mb-4 font-semibold uppercase tracking-[0.22em] text-emerald-200">
              Pollination intelligence for better timing
            </p>
            <h1 className="max-w-3xl text-5xl font-black leading-tight sm:text-6xl">
              Know when crops bloom. Know when pollinators can thrive.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-emerald-50/90">
              PolliSync brings weather, vegetation, and bee observations together
              to estimate flowering windows and pollination suitability.
            </p>
            <a
              className="mt-8 inline-flex rounded-xl bg-pollen px-6 py-3 font-bold text-slate-950 shadow-soft transition hover:-translate-y-0.5"
              href="#foundation"
            >
              Explore the foundation
            </a>
          </div>

          <div className="rounded-3xl border border-white/20 bg-white/95 p-6 shadow-soft backdrop-blur">
            <p className="text-sm font-bold uppercase tracking-wider text-leaf-700">
              Demo snapshot
            </p>
            <div className="my-6 flex items-end justify-between">
              <div>
                <p className="text-sm text-slate-500">Pollination suitability</p>
                <p className="text-6xl font-black text-leaf-700">84</p>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-bold text-emerald-800">
                Low risk
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full w-[84%] rounded-full bg-gradient-to-r from-pollen to-leaf-500" />
            </div>
            <div className="mt-6 grid grid-cols-3 gap-3 text-center">
              {[
                ["28°C", "Temperature"],
                ["67%", "Humidity"],
                ["0.76", "NDVI"],
              ].map(([value, label]) => (
                <div className="rounded-2xl bg-slate-50 p-3" key={label}>
                  <p className="font-black">{value}</p>
                  <p className="mt-1 text-xs text-slate-500">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div
          className="relative grid gap-5 rounded-3xl bg-white p-6 shadow-soft md:grid-cols-3 lg:p-8"
          id="foundation"
        >
          {features.map((feature, index) => (
            <article className="rounded-2xl border border-emerald-100 p-5" key={feature.title}>
              <span className="text-sm font-black text-pollen">0{index + 1}</span>
              <h2 className="mt-3 text-xl font-black text-leaf-950">{feature.title}</h2>
              <p className="mt-2 leading-7 text-slate-600">{feature.text}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
