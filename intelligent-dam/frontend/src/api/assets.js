import { api } from "./client";

export async function uploadAsset(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/assets/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function listAssets({ q, tag, type } = {}) {
  const res = await api.get("/assets", { params: { q, tag, type } });
  return res.data;
}

export async function deleteAsset(assetId) {
  const res = await api.delete(`/assets/${assetId}`);
  return res.data;
}

export async function getAsset(assetId) {
  const res = await api.get(`/assets/${assetId}`);
  return res.data;
}

export async function listVersions(assetId) {
  const res = await api.get(`/assets/${assetId}/versions`);
  return res.data;
}

export async function addTag(assetId, name) {
  const res = await api.post(`/assets/${assetId}/tags`, { name });
  return res.data;
}

export async function newVersion(assetId, file, note) {
  const form = new FormData();
  form.append("file", file);
  if (note) form.append("note", note);
  const res = await api.post(`/assets/${assetId}/version`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function semanticSearch(query, k = 10) {
  const res = await api.post("/search/semantic", { query, k });
  return res.data;
}

