import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ConfidenceBar from "../components/ConfidenceBar";
import SentimentBadge from "../components/SentimentBadge";
import KeywordChips from "../components/KeywordChips";
import ResultVerdict from "../components/ResultVerdict";

function ResultsPage() {
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const raw = localStorage.getItem("last_result");
      if (raw) setResult(JSON.parse(raw));
    } catch {
      // ignore
    }
  }, []);

  const isFake = result?.prediction === "FAKE";

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Results</h1>
        <button
          className="rounded-xl border border-slate-800 bg-slate-900/20 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800/40 transition"
          onClick={() => navigate("/")}
        >
          New Check
        </button>
      </div>

      {!result ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 text-slate-400">
          No results found yet. Run a check from the Home page.
        </div>
      ) : (
        <div className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ResultVerdict prediction={result.prediction} />
            <ConfidenceBar
              confidence={result.confidence}
              variant={isFake ? "fake" : "real"}
            />
          </div>

          <div className="flex flex-wrap gap-3 items-center">
            <SentimentBadge sentiment={result.sentiment} />
            <div className="text-sm text-slate-400">
              Sentiment helps understand whether the text tone appears positive,
              negative, or neutral.
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-semibold text-slate-200">
              Important Keywords
            </div>
            <KeywordChips keywords={result.keywords} />
          </div>

          {result.extracted_text ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
              <div className="text-sm font-semibold text-slate-200 mb-2">
                Extracted Article Text
              </div>
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300 max-h-56 overflow-auto">
                {result.extracted_text}
              </pre>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

export default ResultsPage;

