import { useState } from "react";
import { login, register } from "../api/auth";
import { Button } from "../components/Button.jsx";
import { Card } from "../components/Card.jsx";
import { Input } from "../components/Input.jsx";

export function AuthPage({ onAuthed }) {
  const [mode, setMode] = useState("login"); // login | register
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("User");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data =
        mode === "login"
          ? await login({ email, password })
          : await register({ email, password, role });
      onAuthed(data);
    } catch (err) {
      const msg = err?.response?.data?.error || err?.message || "auth_failed";
      setError(String(msg));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card className="p-6">
        <div className="mb-2 text-lg font-semibold">
          {mode === "login" ? "Sign in" : "Create account"}
        </div>
        <div className="mb-6 text-sm text-slate-400">
          JWT auth + RBAC (Admin/User)
        </div>
        <form className="space-y-4" onSubmit={submit}>
          <div>
            <div className="mb-1 text-xs text-slate-400">Email</div>
            <Input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              type="email"
              required
            />
          </div>
          <div>
            <div className="mb-1 text-xs text-slate-400">Password</div>
            <Input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              type="password"
              required
            />
          </div>
          {mode === "register" ? (
            <div>
              <div className="mb-1 text-xs text-slate-400">Role</div>
              <select
                className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="User">User</option>
                <option value="Admin">Admin</option>
              </select>
              <div className="mt-2 text-xs text-slate-500">
                In production you’d restrict self-registering as Admin.
              </div>
            </div>
          ) : null}
          {error ? (
            <div className="rounded-md border border-rose-900 bg-rose-950/40 p-3 text-sm text-rose-200">
              {error}
            </div>
          ) : null}
          <div className="flex items-center gap-2">
            <Button type="submit" disabled={busy}>
              {busy ? "Working…" : mode === "login" ? "Login" : "Register"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setMode((m) => (m === "login" ? "register" : "login"))}
              disabled={busy}
            >
              {mode === "login" ? "Need an account?" : "Have an account?"}
            </Button>
          </div>
        </form>
      </Card>

      <Card className="p-6">
        <div className="mb-2 text-lg font-semibold">What you can do</div>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="text-slate-400">
            Upload images, videos, and documents to GCS (or local dev storage).
          </li>
          <li className="text-slate-400">
            Auto-tagging using pretrained models (Transformers + CLIP).
          </li>
          <li className="text-slate-400">
            Semantic search using embeddings + FAISS vector similarity.
          </li>
          <li className="text-slate-400">
            Duplicate detection (exact SHA-256 + near-duplicate embedding match).
          </li>
          <li className="text-slate-400">Asset version history tracking.</li>
        </ul>
      </Card>
    </div>
  );
}

