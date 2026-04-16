import { useEffect, useState } from "react";
import { fetchAdminStats } from "../services/api";
import Spinner from "../components/Spinner";

function StatCard({ title, value, sub, tone = "neutral" }) {
  const toneClass =
    tone === "fake"
      ? "border-red-500/30 bg-red-500/5 text-red-200"
      : tone === "real"
      ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-200"
      : "border-slate-800 bg-slate-900/20 text-slate-200";

  return (
    <div className={`rounded-2xl border p-4 ${toneClass}`}>
      <div className="text-xs text-slate-400">{title}</div>
      <div className="mt-1 text-2xl font-black tracking-tight">{value}</div>
      {sub ? <div className="mt-1 text-sm text-slate-400">{sub}</div> : null}
    </div>
  );
}

function AdminPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const s = await fetchAdminStats();
        if (mounted) setStats(s);
      } catch (e) {
        if (!mounted) return;
        setError(
          e?.response?.data?.message ||
            e?.response?.data?.error ||
            e?.message ||
            "Failed to load admin stats."
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

  const realPct = Number(stats?.real_percentage || 0);
  const fakePct = Number(stats?.fake_percentage || 0);

  return (
    <section className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Admin Panel</h1>
        <p className="text-slate-300 mt-2">
          Aggregate prediction stats and recent activity.
        </p>
      </div>

      {loading ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-6 flex items-center gap-3">
          <Spinner size={18} />
          <div className="text-slate-300">Loading stats...</div>
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-200">
          {error}
        </div>
      ) : stats ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard title="Total Predictions" value={stats.total_predictions} />
            <StatCard
              title="Real Share"
              value={`${realPct.toFixed(1)}%`}
              tone="real"
            />
            <StatCard
              title="Fake Share"
              value={`${fakePct.toFixed(1)}%`}
              tone="fake"
            />
            <StatCard
              title="Input Mix"
              value={`${stats.input_type_breakdown?.text || 0} text • ${
                stats.input_type_breakdown?.url || 0
              } url`}
              sub="Text vs URL submissions"
            />
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
            <div className="text-sm font-semibold text-slate-200 mb-3">
              Confidence Split (Real vs Fake)
            </div>
            <div className="h-3 rounded-full overflow-hidden bg-slate-800/80 flex">
              <div
                className="bg-emerald-500"
                style={{ width: `${realPct}%` }}
              />
              <div
                className="bg-red-500"
                style={{ width: `${fakePct}%` }}
              />
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span>{realPct.toFixed(1)}% REAL</span>
              <span>{fakePct.toFixed(1)}% FAKE</span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/30 p-4">
            <div className="text-sm font-semibold text-slate-200 mb-3">
              Recent Activity
            </div>
            <div className="space-y-3">
              {(stats.recent || []).map((r, idx) => {
                const isFake = r.prediction === "FAKE";
                const created = r.created_at
                  ? new Date(r.created_at).toLocaleString()
                  : "";
                return (
                  <div
                    key={`${r.created_at || idx}-${idx}`}
                    className={`rounded-xl border p-3 ${
                      isFake
                        ? "border-red-500/25 bg-red-500/5"
                        : "border-emerald-500/25 bg-emerald-500/5"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm text-slate-300">
                        {created} • {r.input_type.toUpperCase()}
                      </div>
                      <div
                        className={`text-sm font-semibold ${
                          isFake ? "text-red-200" : "text-emerald-200"
                        }`}
                      >
                        {isFake ? "FAKE" : "REAL"} • {Number(r.confidence || 0).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                );
              })}
              {(stats.recent || []).length === 0 ? (
                <div className="text-sm text-slate-400">No history yet.</div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default AdminPage;

