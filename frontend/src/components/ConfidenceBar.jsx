function ConfidenceBar({ confidence = 0, variant = "real" }) {
  const pct = Math.max(0, Math.min(100, Number(confidence) || 0));

  const colors =
    variant === "fake"
      ? {
          track: "bg-red-500/10",
          bar: "bg-red-500",
          label: "text-red-300",
        }
      : {
          track: "bg-emerald-500/10",
          bar: "bg-emerald-500",
          label: "text-emerald-300",
        };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className={colors.label + " font-medium"}>
          Confidence: {pct.toFixed(1)}%
        </span>
        <span className="text-slate-400">{variant === "fake" ? "Fake" : "Real"}</span>
      </div>
      <div className={`h-2 rounded-full overflow-hidden ${colors.track}`}>
        <div className={`${colors.bar} h-full`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default ConfidenceBar;

