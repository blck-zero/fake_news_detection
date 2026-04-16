import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function predictText(text) {
  const res = await client.post("/predict-text", { text });
  return res.data;
}

export async function predictUrl(url) {
  const res = await client.post("/predict-url", { url });
  return res.data;
}

export async function fetchHistory(limit) {
  const res = await client.get("/history", {
    params: typeof limit === "number" ? { limit } : undefined,
  });
  return res.data.history || [];
}

export async function fetchAdminStats() {
  const res = await client.get("/admin/stats");
  return res.data;
}

