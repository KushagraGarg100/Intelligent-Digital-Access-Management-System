export function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 ${className}`}
      {...props}
    />
  );
}

