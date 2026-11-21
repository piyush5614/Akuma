import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { IndiaMap } from "../components/IndiaMap";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { useLiveLocation } from "../hooks/useLiveLocation";

export function Explorer() {
  const liveLocation = useLiveLocation();
  const query = useQuery({ queryKey: ["mandis", "onion", liveLocation.location.lat, liveLocation.location.lng], queryFn: () => api.mandis("onion", liveLocation.location) });
  return <><div className="page-heading"><span className="eyebrow">PRICE EXPLORER</span><h2>Where should you sell?</h2><p>Nearby mandis and major market centres within 300 km of your location.</p><div className="location-note">● {liveLocation.loading ? "Finding your location…" : liveLocation.location.source === "live" ? "Using your live location" : "Using demo location · allow location for nearby results"}{liveLocation.error && <span> · {liveLocation.error}</span>}</div></div>{query.isPending ? <LoadingState /> : query.isError ? <ErrorState error={query.error} retry={() => void query.refetch()} /> : query.data.data.length ? <><div className="card map-card"><IndiaMap mandis={query.data.data} /><div className="map-legend"><span><i className="legend-dot fresh-dot" /> Fresh</span><span><i className="legend-dot stale-dot" /> Stale</span><span><i className="legend-dot old-dot" /> Old</span><small>Live OpenStreetMap tiles · DEMO market reports</small></div></div><div className="card table">{query.data.data.map((mandi) => <div className="row" key={mandi.id}><b>{mandi.name}</b><span>{mandi.district}</span><span className={`badge ${mandi.freshness.toLowerCase()}`}>{mandi.freshness}</span><strong>₹{mandi.modal_price_inr ?? "—"}</strong></div>)}</div></> : <EmptyState />}</>
}
