import { useEffect, useMemo, useState } from "react";
import { fetchHistory } from "../services/api";
import Spinner from "../components/Spinner";
import KeywordChips from "../components/KeywordChips";

function HistoryPage() {
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const history = await fetchHistory(200);
        if (mounted) setItems(history);
      } catch (e) {
        if (!mounted) return;
        setError(
          e?.response?.data?.message ||
            e?.response?.data?.error ||
            e?.message ||
            "Failed to load history."
        );
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((it) => {
      const hay = `${it.input_type} ${it.input_value} ${it.prediction} ${
        it.sentiment || ""
      } ${it.keywords?.join(" ") || ""}`.toLowerCase();
      return hay.includes(q);
    });
  }, [items, query]);

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">History</h1>
        <p className="text-slate-300 mt-2">
          Your previous predictions are stored automatically.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
        <input
          className="w-full rounded-xl border border-slate-800 bg-slate-950/40 p-3 outline-none focus:border-emerald-500/40"
          placeholder="Search by text/URL, prediction, sentiment, or keywords..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="text-sm text-slate-400">
          Showing {filtered.length} result{filtered.length === 1 ? "" : "s"}
        </div>
      </div>

      {loading ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 flex items-center gap-3">
          <Spinner size={18} />
          <div className="text-slate-300">Loading history...</div>
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-200">
          {error}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 text-slate-400">
              No matching predictions.
            </div>
          ) : null}

          {filtered.map((it) => {
            const isFake = it.prediction === "FAKE";
            const created = it.created_at
              ? new Date(it.created_at).toLocaleString()
              : "";
            const inputPreview = (it.input_value || "").slice(0, 160);

            return (
              <article
                key={it.id}
                className={`rounded-2xl border p-4 transition ${
                  isFake
                    ? "border-red-500/30 bg-red-500/5"
                    : "border-emerald-500/30 bg-emerald-500/5"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                  <div className="space-y-1">
                    <div className="text-xs text-slate-400">
                      {created} • {it.input_type.toUpperCase()}
                    </div>
                    <div
                      className={`text-lg font-black ${
                        isFake ? "text-red-200" : "text-emerald-200"
                      }`}
                    >
                      {isFake ? "FAKE" : "REAL"}
                    </div>
                    <div className="text-sm text-slate-300">
                      Confidence: {Number(it.confidence || 0).toFixed(1)}%
                    </div>
                    <div className="text-sm text-slate-400">
                      {it.sentiment ? `Sentiment: ${it.sentiment}` : null}
                    </div>
                  </div>

                  <div className="space-y-2 sm:text-right">
                    <div className="text-sm text-slate-300 font-medium">
                      Input
                    </div>
                    <div className="text-sm text-slate-400 break-words">
                      {inputPreview}
                      {(it.input_value || "").length > 160 ? "..." : ""}
                    </div>
                  </div>
                </div>

                {it.keywords && it.keywords.length > 0 ? (
                  <div className="mt-3">
                    <div className="text-xs text-slate-400 mb-2">
                      Keywords
                    </div>
                    <KeywordChips keywords={it.keywords} />
                  </div>
                ) : null}

                {it.extracted_text ? (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-sm text-slate-300 hover:text-slate-100">
                      Show extracted article text
                    </summary>
                    <pre className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-300 max-h-48 overflow-auto">
                      {it.extracted_text}
                    </pre>
                  </details>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default HistoryPage;

