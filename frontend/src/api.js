// src/api.js
// Talks to the FastAPI backend. In development, Vite proxies /api -> the
// local backend (see vite.config.js). In production, set VITE_API_URL to
// the deployed Render URL as a Vercel environment variable.

const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export function predictChurn(customer) {
  return request("/predict", {
    method: "POST",
    body: JSON.stringify(customer),
  });
}

export function getDashboardStats() {
  return request("/dashboard-stats");
}

export function getHealth() {
  return request("/health");
}
