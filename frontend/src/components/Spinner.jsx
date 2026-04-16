function Spinner({ size = 20, className = "" }) {
  const px = typeof size === "number" ? `${size}px` : size;
  return (
    <span
      className={`inline-block animate-spin rounded-full border-2 border-slate-700 border-t-emerald-400 ${className}`}
      style={{ width: px, height: px }}
      aria-label="Loading"
    />
  );
}

export default Spinner;

