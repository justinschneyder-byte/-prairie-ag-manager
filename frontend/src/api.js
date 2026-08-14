const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(path, { method = "GET", body, params } = {}) {
  let url = `${API_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    if (qs) url += `?${qs}`;
  }
  const headers = { "Content-Type": "application/json" };

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      // ignore, keep statusText
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  list: (resource, params) => request(`/${resource}`, { params }),
  create: (resource, body) => request(`/${resource}`, { method: "POST", body }),
  update: (resource, id, body) => request(`/${resource}/${id}`, { method: "PUT", body }),
  remove: (resource, id) => request(`/${resource}/${id}`, { method: "DELETE" }),

  fieldHistory: (fieldId) => request(`/fields/${fieldId}/history`),
  regionalHistory: (year) => request("/weather/regional-history", { params: { year } }),
  regionalForecast: () => request("/weather/regional-forecast"),

  chat: (message) => request("/chat", { method: "POST", body: { message } }),
  exportData: () => request("/export"),
  importData: (payload) => request("/import", { method: "POST", body: payload }),
};
