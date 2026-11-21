export type Language = "en" | "mr" | "hi";
export type Freshness = "FRESH" | "STALE" | "OLD" | "NO_REPORT";

export interface Envelope<T> { data: T; data_as_of: string; is_demo: boolean }
export interface Crop { id: string; name: Record<Language, string>; unit: string; perishability: string }
export interface Mandi { id: string; name: string; district: string; freshness: Freshness; modal_price_inr: string | null; location: { lat: number; lng: number } }
export interface Recommendation { mandi: Mandi; distance_km: string; costs: { total_net_inr: string; net_per_quintal_inr: string }; rank: number }
export interface RecommendResult { recommendations: Recommendation[]; old_mandis: Recommendation[]; sell_or_wait: { decision: string; reason: Record<Language, string>; disclaimer: string } }
export interface AdminSettings { road_factor: string; transport_rate_per_quintal_km: string; fee_pct: string; shrinkage_pct_by_crop: Record<string, string> }

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<Envelope<T>> {
  const token = localStorage.getItem("fairfarm_token");
  const response = await fetch(`${API_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.message ?? "Unable to load data. Please try again.");
  }
  return response.json() as Promise<Envelope<T>>;
}

export const api = {
  crops: () => request<Crop[]>("/crops"),
  mandis: (cropId: string) => request<Mandi[]>(`/mandis?crop_id=${encodeURIComponent(cropId)}&lat=18.52&lng=73.86&radius_km=300`),
  recommend: (cropId: string, quantity: number) => request<RecommendResult>("/recommend", { method: "POST", body: JSON.stringify({ crop_id: cropId, quantity_quintal: quantity, farmer_location: { lat: 18.52, lng: 73.86 }, radius_km: 300 }) }),
  seasonality: (cropId: string) => request<{ best_months: number[]; worst_months: number[] }>("/insights/seasonality?crop_id=" + cropId),
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  updateSettings: (settings: AdminSettings) => request<AdminSettings>("/admin/settings", { method: "PUT", body: JSON.stringify(settings) }),
};
