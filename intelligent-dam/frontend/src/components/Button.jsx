export function Button({ className = "", variant = "primary", ...props }) {
  const base =
    "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50 disabled:cursor-not-allowed";
  const styles =
    variant === "secondary"
      ? "bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700"
      : variant === "danger"
        ? "bg-rose-600 hover:bg-rose-500 text-white"
        : "bg-sky-600 hover:bg-sky-500 text-white";
  return <button className={`${base} ${styles} ${className}`} {...props} />;
}

