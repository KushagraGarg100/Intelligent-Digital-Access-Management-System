import { useEffect, useMemo, useState } from "react";
import {
  addTag,
  getAsset,
  listAssets,
  listVersions,
  newVersion,
  semanticSearch,
  uploadAsset,
} from "../api/assets";
import { listTags } from "../api/tags";
import { Button } from "../components/Button.jsx";
import { Card } from "../components/Card.jsx";
import { Input } from "../components/Input.jsx";
import { Modal } from "../components/Modal.jsx";

function fmtBytes(n) {
  if (n == null) return "-";
  const units = ["B", "KB", "MB", "GB"];
  let v = Number(n);
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function DashboardPage({ user, onLogout }) {
  const [assets, setAssets] = useState([]);
  const [tags, setTags] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [q, setQ] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [semanticQ, setSemanticQ] = useState("");

  const [selectedId, setSelectedId] = useState(null);
  const [selected, setSelected] = useState(null);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [tagInput, setTagInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [lastUploadInfo, setLastUploadInfo] = useState(null);

  const canSeePublicUrl = useMemo(() => true, []);

  async function refresh() {
    setError("");
    try {
      const [a, t] = await Promise.all([listAssets({ q, tag: tagFilter }), listTags()]);
      setAssets(a);
      setTags(t);
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "failed_to_load");
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const id = setTimeout(() => refresh(), 250);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, tagFilter]);

  async function onUpload(file) {
    setUploading(true);
    setError("");
    setLastUploadInfo(null);
    try {
      const res = await uploadAsset(file);
      setLastUploadInfo(res);
      await refresh();
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "upload_failed");
    } finally {
      setUploading(false);
    }
  }

  async function doSemanticSearch() {
    setBusy(true);
    setError("");
    try {
      const res = await semanticSearch(semanticQ, 15);
      setAssets(res.map((r) => ({ ...r.asset, _score: r.score })));
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "semantic_search_failed");
    } finally {
      setBusy(false);
    }
  }

  async function openAsset(id) {
    setSelectedId(id);
    setSelected(null);
    setSelectedVersions([]);
    setTagInput("");
    try {
      const [a, v] = await Promise.all([getAsset(id), listVersions(id)]);
      setSelected(a);
      setSelectedVersions(v);
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "failed_to_load_asset");
    }
  }

  async function addUserTag() {
    if (!selectedId) return;
    const name = tagInput.trim();
    if (!name) return;
    setBusy(true);
    setError("");
    try {
      await addTag(selectedId, name);
      const a = await getAsset(selectedId);
      setSelected(a);
      setTagInput("");
      await refresh();
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "add_tag_failed");
    } finally {
      setBusy(false);
    }
  }

  async function uploadNewVersion(file) {
    if (!selectedId) return;
    setBusy(true);
    setError("");
    try {
      await newVersion(selectedId, file, "Updated via dashboard");
      const [a, v] = await Promise.all([getAsset(selectedId), listVersions(selectedId)]);
      setSelected(a);
      setSelectedVersions(v);
      await refresh();
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || "new_version_failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-slate-400">
          Upload → AI tags + embeddings → PostgreSQL + FAISS
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={refresh} disabled={busy || uploading}>
            Refresh
          </Button>
          <Button variant="secondary" onClick={onLogout}>
            Logout
          </Button>
        </div>
      </div>

      {error ? (
        <div className="rounded-md border border-rose-900 bg-rose-950/40 p-3 text-sm text-rose-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="p-4 lg:col-span-1">
          <div className="mb-3 text-sm font-semibold">Upload</div>
          <input
            type="file"
            className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-slate-800 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-100 hover:file:bg-slate-700"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) onUpload(file);
              e.target.value = "";
            }}
            disabled={uploading}
          />
          <div className="mt-3 text-xs text-slate-500">
            Supports images, videos, PDFs, and text-like documents.
          </div>
          {lastUploadInfo ? (
            <div className="mt-4 rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
              <div className="font-semibold text-slate-200">Upload result</div>
              <div className="mt-2">
                Asset #{lastUploadInfo.asset?.id} •{" "}
                <span className="text-slate-400">{lastUploadInfo.asset?.asset_type}</span>
              </div>
              {lastUploadInfo.near_duplicate ? (
                <div className="mt-2 text-amber-200">
                  Near-duplicate match: asset #{lastUploadInfo.near_duplicate.asset_id} (
                  {Number(lastUploadInfo.near_duplicate.score).toFixed(3)})
                </div>
              ) : (
                <div className="mt-2 text-slate-500">No near-duplicate detected.</div>
              )}
            </div>
          ) : null}
        </Card>

        <Card className="p-4 lg:col-span-2">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="text-sm font-semibold">Search & filter</div>
            <div className="text-xs text-slate-500">
              User: <span className="text-slate-300">{user?.email}</span>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <div>
              <div className="mb-1 text-xs text-slate-400">Filename contains</div>
              <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="report, invoice…" />
            </div>
            <div>
              <div className="mb-1 text-xs text-slate-400">Tag</div>
              <select
                className="w-full rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500"
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
              >
                <option value="">All</option>
                {tags.map((t) => (
                  <option key={t.id} value={t.name}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <div className="mb-1 text-xs text-slate-400">Semantic search</div>
              <div className="flex gap-2">
                <Input
                  value={semanticQ}
                  onChange={(e) => setSemanticQ(e.target.value)}
                  placeholder="meaning-based search…"
                />
                <Button onClick={doSemanticSearch} disabled={busy || !semanticQ.trim()}>
                  Go
                </Button>
              </div>
            </div>
          </div>

          <div className="mt-4 overflow-hidden rounded-lg border border-slate-800">
            <div className="grid grid-cols-12 bg-slate-900/60 px-3 py-2 text-xs uppercase tracking-wider text-slate-400">
              <div className="col-span-5">Asset</div>
              <div className="col-span-2">Type</div>
              <div className="col-span-2">Size</div>
              <div className="col-span-3">Created</div>
            </div>
            <div className="divide-y divide-slate-800">
              {assets.length === 0 ? (
                <div className="px-3 py-6 text-sm text-slate-500">No assets yet. Upload one.</div>
              ) : (
                assets.map((a) => (
                  <button
                    key={a.id}
                    className="grid w-full grid-cols-12 px-3 py-3 text-left text-sm hover:bg-slate-900/40"
                    onClick={() => openAsset(a.id)}
                  >
                    <div className="col-span-5">
                      <div className="font-medium text-slate-100">{a.original_filename}</div>
                      {a._score != null ? (
                        <div className="text-xs text-slate-500">
                          Similarity: {Number(a._score).toFixed(3)}
                        </div>
                      ) : null}
                    </div>
                    <div className="col-span-2 text-slate-300">{a.asset_type}</div>
                    <div className="col-span-2 text-slate-300">{fmtBytes(a.size_bytes)}</div>
                    <div className="col-span-3 text-slate-500">
                      {a.created_at ? new Date(a.created_at).toLocaleString() : "-"}
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </Card>
      </div>

      <Modal
        open={Boolean(selectedId)}
        title={selected ? `Asset #${selected.id}` : "Asset"}
        onClose={() => setSelectedId(null)}
      >
        {!selected ? (
          <div className="text-sm text-slate-400">Loading…</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-4">
              <div className="text-sm font-semibold">Details</div>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                <div>
                  <span className="text-slate-500">Filename:</span>{" "}
                  <span className="text-slate-100">{selected.original_filename}</span>
                </div>
                <div>
                  <span className="text-slate-500">Type:</span>{" "}
                  <span className="text-slate-100">{selected.asset_type}</span>
                </div>
                <div>
                  <span className="text-slate-500">Size:</span>{" "}
                  <span className="text-slate-100">{fmtBytes(selected.size_bytes)}</span>
                </div>
                <div>
                  <span className="text-slate-500">Latest version:</span>{" "}
                  <span className="text-slate-100">{selected.latest_version}</span>
                </div>
                {canSeePublicUrl && selected.storage_url ? (
                  <div className="break-all">
                    <span className="text-slate-500">URL:</span>{" "}
                    <a className="text-sky-400 hover:underline" href={selected.storage_url} target="_blank">
                      {selected.storage_url}
                    </a>
                  </div>
                ) : null}
                {selected.download_url ? (
                  <div className="mt-2">
                    <a
                      className="text-sm text-sky-400 hover:underline"
                      href={`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8080/api"}/assets/${selected.id}/download`}
                      target="_blank"
                    >
                      Download (API)
                    </a>
                  </div>
                ) : null}
              </div>

              <div className="mt-4">
                <div className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                  Tags
                </div>
                <div className="flex flex-wrap gap-2">
                  {(selected.tags || []).map((t) => (
                    <span
                      key={t.name}
                      className="rounded-full border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200"
                      title={`${t.source}${t.confidence ? ` • ${t.confidence}` : ""}`}
                    >
                      {t.name}
                    </span>
                  ))}
                </div>

                <div className="mt-3 flex gap-2">
                  <Input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    placeholder="add tag…"
                  />
                  <Button onClick={addUserTag} disabled={busy || !tagInput.trim()}>
                    Add
                  </Button>
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-semibold">Versions</div>
                <label className="inline-flex items-center gap-2 text-sm">
                  <span className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800">
                    Upload new version
                  </span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) uploadNewVersion(file);
                      e.target.value = "";
                    }}
                    disabled={busy}
                  />
                </label>
              </div>

              <div className="mt-3 overflow-hidden rounded-lg border border-slate-800">
                <div className="grid grid-cols-12 bg-slate-900/60 px-3 py-2 text-xs uppercase tracking-wider text-slate-400">
                  <div className="col-span-2">Ver</div>
                  <div className="col-span-4">Size</div>
                  <div className="col-span-6">Note</div>
                </div>
                <div className="divide-y divide-slate-800">
                  {selectedVersions.length === 0 ? (
                    <div className="px-3 py-6 text-sm text-slate-500">No versions.</div>
                  ) : (
                    selectedVersions.map((v) => (
                      <div key={v.version} className="grid grid-cols-12 px-3 py-3 text-sm">
                        <div className="col-span-2 font-medium text-slate-100">{v.version}</div>
                        <div className="col-span-4 text-slate-300">{fmtBytes(v.size_bytes)}</div>
                        <div className="col-span-6 text-slate-400">{v.note || "-"}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
}

