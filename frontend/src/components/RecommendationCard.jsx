function stripMarkdown(value = "") {
  return value.replace(/^#{1,3}\s*/, "").replace(/\*\*/g, "").trim();
}

function parseRecommendation(text) {
  const result = { title: "AI agronomist advisory", assessment: [], actions: [], watchOut: "", confidence: "" };
  let section = "assessment";

  for (const rawLine of String(text || "").split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    const lower = stripMarkdown(line).toLowerCase();
    if (line.startsWith("##")) {
      result.title = stripMarkdown(line);
    } else if (lower.startsWith("recommended now")) {
      section = "actions";
    } else if (lower.startsWith("watch out") || lower.startsWith("warning") || lower.startsWith("caution")) {
      section = "watch";
      const content = stripMarkdown(line).replace(/^(watch out|warning|caution)\s*:?/i, "").trim();
      if (content) result.watchOut = content;
    } else if (lower.startsWith("confidence")) {
      section = "confidence";
      result.confidence = stripMarkdown(line).replace(/^confidence\s*:?/i, "").trim();
    } else if (/^[-*]\s+/.test(line) || /^\d+[.)]\s+/.test(line)) {
      result.actions.push(line.replace(/^([-*]\s+|\d+[.)]\s+)/, ""));
    } else if (section === "actions") {
      result.actions.push(stripMarkdown(line));
    } else if (section === "watch") {
      result.watchOut = [result.watchOut, stripMarkdown(line)].filter(Boolean).join(" ");
    } else if (section === "confidence") {
      result.confidence = [result.confidence, stripMarkdown(line)].filter(Boolean).join(" ");
    } else {
      result.assessment.push(stripMarkdown(line));
    }
  }
  return result;
}

export default function RecommendationCard({ text = "", riskLevel = "Low", className = "" }) {
  const borderColor = riskLevel === "Low" ? "border-l-primary" : riskLevel === "Medium" ? "border-l-secondary" : "border-l-tertiary";
  const recommendation = parseRecommendation(text);

  return (
    <section className={`rounded-2xl border border-outline-variant border-l-4 bg-surface p-lg shadow-sm ${borderColor} ${className}`} aria-labelledby="agronomist-advisory">
      <div className="mb-md flex items-start gap-sm">
        <span className="material-symbols-outlined text-primary" aria-hidden="true">psychology</span>
        <div>
          <p className="text-label-sm font-bold uppercase tracking-wide text-primary">AI Agronomist Recommendation</p>
          <h2 id="agronomist-advisory" className="mt-1 text-headline-md font-headline-md text-on-surface">{text ? recommendation.title : "Advice appears after a prediction"}</h2>
        </div>
      </div>
      {!text ? (
        <p className="text-body-md text-on-surface-variant">Run a prediction to receive crop-specific guidance based on your farm settings and current conditions.</p>
      ) : (
        <div className="space-y-md">
          {recommendation.assessment.length > 0 && <p className="text-body-md leading-relaxed text-on-surface-variant">{recommendation.assessment.join(" ")}</p>}
          {recommendation.actions.length > 0 && (
            <div className="rounded-xl bg-primary-container/8 p-md">
              <h3 className="text-label-md font-bold text-on-surface">Recommended now</h3>
              <ul className="mt-sm space-y-sm">
                {recommendation.actions.slice(0, 3).map((action, index) => <li key={`${action}-${index}`} className="flex gap-sm text-body-sm text-on-surface-variant"><span className="material-symbols-outlined text-[18px] text-primary" aria-hidden="true">check_circle</span><span>{action}</span></li>)}
              </ul>
            </div>
          )}
          {recommendation.watchOut && <p className={`rounded-lg px-md py-sm text-body-sm ${riskLevel === "High" ? "bg-tertiary-container/15 text-tertiary" : "bg-surface-container text-on-surface-variant"}`}><strong>Watch out: </strong>{recommendation.watchOut}</p>}
          {recommendation.confidence && <p className="text-body-sm text-on-surface-variant"><strong className="text-on-surface">Confidence: </strong>{recommendation.confidence}</p>}
        </div>
      )}
    </section>
  );
}
