import { api } from "./client";

export async function listTags() {
  const res = await api.get("/tags");
  return res.data;
}

