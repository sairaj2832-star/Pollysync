/**
 * ChartWrapper - Standardized chart container with title, legend, export, and loading states
 * Wraps Chart.js Line/Bar components
 */
import Card from "./Card";

export default function ChartWrapper({
  title = "",
  children,
  legend = [],
  onExport,
  loading = false,
  error = "",
}) {
  return (
    <Card
      header={
        <div className="flex justify-between items-center w-full">
          <span>{title}</span>
          {onExport && (
            <button
              onClick={onExport}
              className="px-sm py-xs rounded-lg bg-background hover:bg-surface-container text-on-surface text-label-sm font-label-sm transition"
              title="Export as CSV"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
            </button>
          )}
        </div>
      }
    >
      {error && (
        <div className="p-md bg-tertiary/10 rounded-lg text-tertiary font-body-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-md">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="font-body-sm text-on-surface-variant">Loading chart...</p>
          </div>
        </div>
      ) : (
        <>
          <div className="relative h-80 w-full">{children}</div>

          {/* Legend */}
          {legend.length > 0 && (
            <div className="flex flex-wrap gap-md mt-md pt-md border-t border-outline-variant/50">
              {legend.map((item, i) => (
                <div key={i} className="flex items-center gap-sm">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color || "#006c49" }}
                  />
                  <span className="font-label-sm text-label-sm text-on-surface-variant">
                    {item.label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </Card>
  );
}

/**
 * Helper to format chart export as CSV
 */
export function exportChartData(title, labels, datasets) {
  let csv = `"${title}"\n`;
  csv += `"Date",${datasets.map((d) => `"${d.label}"`).join(",")}\n`;

  labels.forEach((label, i) => {
    const row = [label, ...datasets.map((d) => d.data[i] ?? "")];
    csv += row.map((v) => `"${v}"`).join(",") + "\n";
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${title}-${new Date().toISOString().split("T")[0]}.csv`);
  link.click();
}
