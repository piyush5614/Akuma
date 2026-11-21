export type Language = "en" | "mr" | "hi";
export type Freshness = "FRESH" | "STALE" | "OLD" | "NO_REPORT";

export interface Envelope<T> { data: T; data_as_of: string; is_demo: boolean }
export interface Crop { id: string; name: Record<Language, string>; category: "vegetable" | "grain" | "fruit"; unit: string; perishability: string }
export interface Mandi { id: string; name: string; district: string; freshness: Freshness; modal_price_inr: string | null; location: { lat: number; lng: number } }
export interface Recommendation { mandi: Mandi; distance_km: string; costs: { total_net_inr: string; net_per_quintal_inr: string }; rank: number }
export interface RecommendResult { recommendations: Recommendation[]; old_mandis: Recommendation[]; sell_or_wait: { decision: string; reason: Record<Language, string>; disclaimer: string } }
export interface AdminSettings { road_factor: string; transport_rate_per_quintal_km: string; fee_pct: string; shrinkage_pct_by_crop: Record<string, string> }
export interface SaathiMetrics { messages_per_day: Record<string, number>; messages_by_language: Record<Language, number>; top_intents: Record<string, number>; fallback_rate: number; refusal_rate: number; grounding_failure_count: number; thumbs_ratio: { up: number; down: number }; unanswered_questions: string[]; provider: string; mode: string }
export interface SaathiTestResult { reply: string; language: Language; intent: string; tools_used: string[]; tool_results: Array<Record<string, unknown>>; grounded: boolean; fallback_used: boolean }
export interface SaathiChatResult { session_id: string; reply: { text: string; speak_text: string; language: Language; script: "latin" | "devanagari" }; cards: Array<Record<string, unknown>>; chips: string[]; meta: { intent: string; tools_used: string[]; grounded: boolean; fallback_used: boolean; request_id: string } }
export interface LocationContext { lat: number; lng: number; source?: "live" | "fallback" }
export interface NextCropSuggestion { crop: { crop_id: string; risk_adjusted_midpoint_inr_per_acre: string; water_fit: string }; reason: string; reasons: string[] }
export interface AdminSummary { mandi_count: number; crop_count: number; report_count: number; fresh_report_pct: string; query_count: number }
export interface QueryLogItem { requested_at: string; crop_id: string; radius_km: string; location_rounded: [string, string] }
export interface QueryLogResult { items: QueryLogItem[]; total: number }
export interface SeasonalityResult { crop_id: string; months: Array<{ month: number; price_index: string; median_modal_price_inr: string }>; best_months: number[]; worst_months: number[] }
export interface CropProfitRow { crop_id: string; price_range_inr_per_quintal: [string, string]; yield_range_quintal_per_acre: [string, string]; cost_inr_per_acre: string; risk_adjusted_midpoint_inr_per_acre: string; water_fit: string; herd_warning: boolean; source: string }
export interface RegionPrice { region_id: string; name: string; location: { lat: number; lng: number }; average_modal_price_inr: string | null; mandi_count: number; freshness: Freshness }

const API_URL = window.__FAIRFARM_CONFIG__?.API_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<Envelope<T>> {
  const token = localStorage.getItem("fairfarm_token");
  const method = init?.method?.toUpperCase() ?? "GET";
  const attempts = method === "GET" ? 3 : 1;
  let lastServerMessage = "Unable to load data. Please try again.";
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    let response: Response;
    try {
      const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
      response = await fetch(`${API_URL}${path}`, { ...init, signal: AbortSignal.timeout(10000), headers: { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers } });
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
  mandis: (cropId: string, location: LocationContext = { lat: 18.52, lng: 73.86 }) => request<Mandi[]>(`/mandis?crop_id=${encodeURIComponent(cropId)}&lat=${location.lat}&lng=${location.lng}&radius_km=300`),
  recommend: (cropId: string, quantity: number, location: LocationContext = { lat: 18.52, lng: 73.86 }) => request<RecommendResult>("/recommend", { method: "POST", body: JSON.stringify({ crop_id: cropId, quantity_quintal: quantity, farmer_location: { lat: location.lat, lng: location.lng }, radius_km: 300 }) }),
  seasonality: (cropId: string) => request<SeasonalityResult>("/insights/seasonality?crop_id=" + cropId),
  cropProfit: (water: "low" | "medium" | "high" = "medium") => request<CropProfitRow[]>("/insights/crop-profit?water_availability=" + water),
  backtest: (cropId: string) => request<{ crop_id: string; window_days: number; rule_hit_rate: string; baseline_hit_rate: string; sample_count: number; measured_only: boolean }>("/insights/backtest?crop_id=" + cropId),
  regions: (cropId: string) => request<RegionPrice[]>("/regions/prices?crop_id=" + cropId),
  trend: (mandiId: string, cropId: string, days = 30) => request<{ mandi_id: string; crop_id: string; points: Array<{ reported_on: string; modal_price_inr: string; arrivals_quintal: string }> }>(`/mandis/${mandiId}/trend?crop_id=${cropId}&days=${days}`),
  nextCrops: (category: Crop["category"], cropHistory: string[], waterAvailability: "low" | "medium" | "high") => request<NextCropSuggestion[]>("/insights/next-crops", { method: "POST", body: JSON.stringify({ category, crop_history: cropHistory, water_availability: waterAvailability }) }),
  meta: () => request<{ api_version: string; min_app_version: string; is_demo: boolean }>("/meta"),
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  updateSettings: (settings: AdminSettings) => request<AdminSettings>("/admin/settings", { method: "PUT", body: JSON.stringify(settings) }),
  getSettings: () => request<AdminSettings>("/admin/settings"),
  summary: () => request<AdminSummary>("/admin/summary"),
  queries: (limit = 50, offset = 0) => request<QueryLogResult>(`/admin/queries?limit=${limit}&offset=${offset}`),
  importCsv: (file: File) => { const form = new FormData(); form.append("file", file); return request<{ imported_records: number; skipped_records: number; errors: string[] }>("/admin/data/import", { method: "POST", body: form }); },
  saathiMetrics: () => request<SaathiMetrics>("/admin/saathi/metrics"),
  saathiChat: (message: string, sessionId?: string, location: LocationContext = { lat: 18.52, lng: 73.86 }, cropId = "onion", quantityQuintal = 10) => request<SaathiChatResult>("/chat", { method: "POST", body: JSON.stringify({ message, session_id: sessionId, ui_language: "auto", context: { lat: location.lat, lng: location.lng, crop_id: cropId, quantity_quintal: quantityQuintal }, client: { platform: "web", app_version: "0.1.0" } }) }),
  saathiFeedback: (requestId: string, rating: "up" | "down", reasonCode = "clear") => request<{ accepted: boolean }>("/chat/feedback", { method: "POST", body: JSON.stringify({ request_id: requestId, rating, reason_code: reasonCode }) }),
  saathiTest: (message: string, cropId: string, quantity: number) => request<SaathiTestResult>("/admin/saathi/test", { method: "POST", body: JSON.stringify({ message, ui_language: "auto", context: { lat: 18.52, lng: 73.86, crop_id: cropId, quantity_quintal: quantity }, client: { platform: "web", app_version: "0.1.0" } }) }),
};
