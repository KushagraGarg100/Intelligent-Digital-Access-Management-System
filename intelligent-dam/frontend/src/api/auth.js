import { api } from "./client";

export async function register({ email, password, role }) {
  const res = await api.post("/auth/register", { email, password, role });
  return res.data;
}

export async function login({ email, password }) {
  const res = await api.post("/auth/login", { email, password });
  return res.data;
}

export async function me() {
  const res = await api.get("/auth/me");
  return res.data;
}

