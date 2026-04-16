function KeywordChips({ keywords = [] }) {
  const clean = Array.isArray(keywords) ? keywords : [];
  if (clean.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {clean.map((k) => (
        <span
          key={k}
          className="rounded-full border border-slate-700 bg-slate-900/40 px-3 py-1 text-xs text-slate-200"
        >
          {k}
        </span>
      ))}
    </div>
  );
}

export default KeywordChips;

