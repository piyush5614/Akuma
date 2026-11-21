export type Language = "en" | "mr" | "hi";
export type Freshness = "FRESH" | "STALE" | "OLD" | "NO_REPORT";

export interface Envelope<T> { data: T; data_as_of: string; is_demo: boolean }
export interface Crop { id: string; name: Record<Language, string>; unit: string; perishability: string }
export interface Mandi { id: string; name: string; district: string; freshness: Freshness; modal_price_inr: string | null; location: { lat: number; lng: number } }
export interface Recommendation { mandi: Mandi; distance_km: string; costs: { total_net_inr: string; net_per_quintal_inr: string }; rank: number }
export interface RecommendResult { recommendations: Recommendation[]; old_mandis: Recommendation[]; sell_or_wait: { decision: string; reason: Record<Language, string>; disclaimer: string } }
export interface AdminSettings { road_factor: string; transport_rate_per_quintal_km: string; fee_pct: string; shrinkage_pct_by_crop: Record<string, string> }
export interface SaathiMetrics { messages_per_day: Record<string, number>; messages_by_language: Record<Language, number>; top_intents: Record<string, number>; fallback_rate: number; refusal_rate: number; grounding_failure_count: number; thumbs_ratio: { up: number; down: number }; unanswered_questions: string[]; provider: string; mode: string }
export interface SaathiTestResult { reply: string; language: Language; intent: string; tools_used: string[]; tool_results: Array<Record<string, unknown>>; grounded: boolean; fallback_used: boolean }

const API_URL = window.__FAIRFARM_CONFIG__?.API_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<Envelope<T>> {
  const token = localStorage.getItem("fairfarm_token");
  const method = init?.method?.toUpperCase() ?? "GET";
  const attempts = method === "GET" ? 3 : 1;
  let lastServerMessage = "Unable to load data. Please try again.";
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    let response: Response;
    try {
      response = await fetch(`${API_URL}${path}`, { ...init, signal: AbortSignal.timeout(10000), headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers } });
    } catch (reason) {
      if (attempt === attempts - 1 || method !== "GET") throw reason instanceof Error ? reason : new Error("Unable to load data. Please try again.");
      await new Promise((resolve) => setTimeout(resolve, 200 * 2 ** attempt));
      continue;
    }
    if (response.ok) return response.json() as Promise<Envelope<T>>;
    const body = await response.json().catch(() => ({}));
    lastServerMessage = body.message ?? lastServerMessage;
    if (method !== "GET" || response.status < 500 || attempt === attempts - 1) throw new Error(lastServerMessage);
    await new Promise((resolve) => setTimeout(resolve, 200 * 2 ** attempt));
  }
  throw new Error(lastServerMessage);
}

export const api = {
  crops: () => request<Crop[]>("/crops"),
  mandis: (cropId: string) => request<Mandi[]>(`/mandis?crop_id=${encodeURIComponent(cropId)}&lat=18.52&lng=73.86&radius_km=300`),
  recommend: (cropId: string, quantity: number) => request<RecommendResult>("/recommend", { method: "POST", body: JSON.stringify({ crop_id: cropId, quantity_quintal: quantity, farmer_location: { lat: 18.52, lng: 73.86 }, radius_km: 300 }) }),
  seasonality: (cropId: string) => request<{ best_months: number[]; worst_months: number[] }>("/insights/seasonality?crop_id=" + cropId),
  meta: () => request<{ api_version: string; min_app_version: string; is_demo: boolean }>("/meta"),
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  updateSettings: (settings: AdminSettings) => request<AdminSettings>("/admin/settings", { method: "PUT", body: JSON.stringify(settings) }),
  saathiMetrics: () => request<SaathiMetrics>("/admin/saathi/metrics"),
  saathiTest: (message: string, cropId: string, quantity: number) => request<SaathiTestResult>("/admin/saathi/test", { method: "POST", body: JSON.stringify({ message, ui_language: "auto", context: { lat: 18.52, lng: 73.86, crop_id: cropId, quantity_quintal: quantity }, client: { platform: "web", app_version: "0.1.0" } }) }),
};
