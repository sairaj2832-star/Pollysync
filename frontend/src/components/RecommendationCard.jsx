export default function RecommendationCard({ text = "", riskLevel = "Low" }) {
  const borderColor =
    riskLevel === "Low" ? "border-l-primary-container"
    : riskLevel === "Medium" ? "border-l-secondary"
    : "border-l-tertiary";

  function renderMarkdown(text) {
    const lines = text.split("\n").filter(Boolean);
    return lines.map((line, i) => {
      if (line.startsWith("## ")) {
        return (
          <p key={i} className="font-headline-sm text-headline-sm text-on-surface mb-sm">
            {line.slice(3)}
          </p>
        );
      }
      if (line.startsWith("**") && line.endsWith("**")) {
        return (
          <p key={i} className="mt-2 font-semibold text-on-surface">
            {line.slice(2, -2)}
          </p>
        );
      }
      if (line.startsWith("- ")) {
        return (
          <li key={i} className="ml-4 list-disc font-body-md text-body-md text-on-surface-variant">
            {line.slice(2)}
          </li>
        );
      }
      return (
        <p key={i} className="font-body-md text-body-md text-on-surface-variant mb-sm">
          {line}
        </p>
      );
    });
  }

  return (
    <div className={`bg-primary-container/5 border border-outline-variant rounded-xl p-lg border-l-4 ${borderColor} shadow-[0_1px_3px_rgba(0,0,0,0.05)]`}>
      <div className="flex items-center gap-sm mb-md">
        <span className="material-symbols-outlined text-primary-container">psychology</span>
        <h3 className="font-headline-sm text-headline-sm text-on-surface">AI Agronomist Recommendation</h3>
      </div>
      <div className="font-body-md text-body-md text-on-surface-variant prose prose-sm max-w-none">
        {text ? renderMarkdown(text) : (
          <p className="font-body-md text-body-md text-on-surface-variant">
            No recommendation yet. Run a prediction first.
          </p>
        )}
      </div>
    </div>
  );
}
