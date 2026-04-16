import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { predictText, predictUrl } from "../services/api";
import Spinner from "../components/Spinner";
import ConfidenceBar from "../components/ConfidenceBar";
import SentimentBadge from "../components/SentimentBadge";
import KeywordChips from "../components/KeywordChips";
import ResultVerdict from "../components/ResultVerdict";

function HomePage() {
  const [mode, setMode] = useState("text"); // "text" | "url"
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const isFake = result?.prediction === "FAKE";

  const canSubmit = useMemo(() => {
    if (loading) return false;
    if (mode === "text") return text.trim().length >= 20;
    return url.trim().length >= 10;
  }, [loading, mode, text, url]);

  async function onSubmit() {
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const res =
        mode === "text"
          ? await predictText(text)
          : await predictUrl(url.trim());
      setResult(res);
      try {
        localStorage.setItem("last_result", JSON.stringify(res));
      } catch {
        // ignore storage errors
      }
      navigate("/results");
    } catch (e) {
      const msg =
        e?.response?.data?.message ||
        e?.response?.data?.error ||
        e?.message ||
        "Something went wrong.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">
          Fake News Detection
        </h1>
        <p className="text-slate-300 max-w-2xl mt-2">
          Paste a news article or provide a URL. We&apos;ll analyze the extracted
          text with TF-IDF + Logistic Regression and show a verdict, confidence,
          sentiment, and highlighted keywords.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4 sm:p-6">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className={`px-4 py-2 rounded-xl border text-sm transition ${
              mode === "text"
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                : "border-slate-700 bg-slate-950/30 text-slate-200 hover:bg-slate-800/40"
            }`}
            onClick={() => setMode("text")}
            disabled={loading}
          >
            Analyze Text
          </button>
          <button
            type="button"
            className={`px-4 py-2 rounded-xl border text-sm transition ${
              mode === "url"
                ? "border-red-500/40 bg-red-500/10 text-red-200"
                : "border-slate-700 bg-slate-950/30 text-slate-200 hover:bg-slate-800/40"
            }`}
            onClick={() => setMode("url")}
            disabled={loading}
          >
            Analyze URL
          </button>
        </div>

        <div className="mt-5">
          {mode === "text" ? (
            <div className="space-y-3">
              <label className="text-sm text-slate-300 font-medium">
                News Text
              </label>
              <textarea
                className="w-full min-h-[180px] rounded-xl border border-slate-800 bg-slate-950/40 p-4 outline-none focus:border-emerald-500/40"
                placeholder="Paste the article text here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={loading}
              />
              <div className="text-xs text-slate-400">
                Tip: Include enough context for better results (20+ characters).
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <label className="text-sm text-slate-300 font-medium">
                News URL
              </label>
              <input
                className="w-full rounded-xl border border-slate-800 bg-slate-950/40 p-3 outline-none focus:border-red-500/40"
                placeholder="https://example.com/news-article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
              />
              <div className="text-xs text-slate-400">
                We&apos;ll scrape the article text and run prediction on the
                extracted content.
              </div>
            </div>
          )}

          <div className="mt-5 flex items-center gap-3">
            <button
              type="button"
              onClick={onSubmit}
              disabled={!canSubmit}
              className="flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:opacity-50 disabled:hover:bg-emerald-500"
            >
              {loading ? <Spinner size={18} /> : null}
              {loading ? "Checking..." : "Check News"}
            </button>
            {error ? (
              <div className="text-sm text-red-300">{error}</div>
            ) : (
              <div className="text-sm text-slate-400">
                Paste input and click <span className="text-slate-200">Check News</span>.
              </div>
            )}
          </div>
        </div>
      </div>

      {result ? (
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

          {mode === "url" && result.extracted_text ? (
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
      ) : null}
    </section>
  );
}

export default HomePage;

