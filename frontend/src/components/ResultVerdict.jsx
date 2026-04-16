function ResultVerdict({ prediction = "REAL" }) {
  const isFake = prediction === "FAKE";

  return (
    <div
      className={`rounded-xl border p-4 transition-colors ${
        isFake
          ? "border-red-500/40 bg-red-500/10"
          : "border-emerald-500/40 bg-emerald-500/10"
      }`}
    >
      <div className="text-xs text-slate-400">Prediction</div>
      <div
        className={`text-2xl font-black tracking-tight ${
          isFake ? "text-red-300" : "text-emerald-300"
        }`}
      >
        {isFake ? "FAKE" : "REAL"}
      </div>
    </div>
  );
}

export default ResultVerdict;

