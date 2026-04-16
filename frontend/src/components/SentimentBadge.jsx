function SentimentBadge({ sentiment = "neutral" }) {
  const s = sentiment || "neutral";
  const map = {
    positive: {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
      text: "text-emerald-300",
      label: "Positive",
    },
    negative: {
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      text: "text-red-300",
      label: "Negative",
    },
    neutral: {
      bg: "bg-slate-500/10",
      border: "border-slate-500/30",
      text: "text-slate-300",
      label: "Neutral",
    },
  };

  const style = map[s] || map.neutral;

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium ${style.bg} ${style.border} ${style.text}`}
    >
      {style.label}
    </span>
  );
}

export default SentimentBadge;

