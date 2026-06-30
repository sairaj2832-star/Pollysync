export default function RecommendationCard({ text = "", riskLevel = "Low" }) {
  const borderColor =
    riskLevel === "Low" ? "border-l-emerald-500"
    : riskLevel === "Medium" ? "border-l-amber-500"
    : "border-l-red-500";

  const badgeColor =
    riskLevel === "Low" ? "bg-emerald-100 text-emerald-800"
    : riskLevel === "Medium" ? "bg-amber-100 text-amber-800"
    : "bg-red-100 text-red-800";

  function renderMarkdown(text) {
    const lines = text.split("\n").filter(Boolean);
    return lines.map((line, i) => {
      if (line.startsWith("## ")) {
        return <h3 key={i} className="mt-3 text-lg font-bold text-slate-900">{line.slice(3)}</h3>;
      }
      if (line.startsWith("**") && line.endsWith("**")) {
        return <p key={i} className="mt-2 font-semibold text-slate-800">{line.slice(2, -2)}</p>;
      }
      if (line.startsWith("- ")) {
        return <li key={i} className="ml-4 list-disc text-slate-700">{line.slice(2)}</li>;
      }
      return <p key={i} className="mt-1 text-slate-700">{line}</p>;
    });
  }

  return (
    <div className={`rounded-2xl border border-slate-100 bg-white p-5 shadow-soft border-l-4 ${borderColor}`}>
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
          AI Recommendation
        </h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${badgeColor}`}>
          {riskLevel} Risk
        </span>
      </div>
      <div className="mt-3 text-sm leading-7">
        {text ? renderMarkdown(text) : <p className="text-slate-400">No recommendation yet.</p>}
      </div>
    </div>
  );
}
