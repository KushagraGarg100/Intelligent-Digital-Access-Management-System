export function Card({ className = "", ...props }) {
  return (
    <div
      className={`rounded-xl border border-slate-800 bg-slate-950/60 shadow-sm ${className}`}
      {...props}
    />
  );
}

