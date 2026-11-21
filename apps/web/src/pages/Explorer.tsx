import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { MapPin, Minus, Navigation, Plus, Search, Sprout } from "lucide-react";
import { api, type Recommendation } from "../api/client";
import { IndiaMap } from "../components/IndiaMap";
import { EmptyState, ErrorState, LoadingState } from "../components/State";
import { useLiveLocation } from "../hooks/useLiveLocation";

export function Explorer() {
  const liveLocation = useLiveLocation();
  const [crop, setCrop] = useState("onion");
  const [quantity, setQuantity] = useState(10);
  const [selected, setSelected] = useState<string>();
  const [mapLayer, setMapLayer] = useState<"net" | "modal" | "freshness">("net");
  const crops = useQuery({ queryKey: ["crops"], queryFn: api.crops });
  const recommend = useQuery({
    queryKey: ["recommend", crop, quantity, liveLocation.location.lat, liveLocation.location.lng],
    queryFn: () => api.recommend(crop, quantity, liveLocation.location),
  });

  useEffect(() => {
    const first = recommend.data?.data.recommendations[0];
    if (first) setSelected((current) => current ?? first.mandi.id);
  }, [recommend.data]);

  const recommendations = recommend.data?.data.recommendations ?? [];
  const selectedRecommendation = recommendations.find((item) => item.mandi.id === selected) ?? recommendations[0];
  const markerTextById = Object.fromEntries(recommendations.map((item) => [
    item.mandi.id,
    mapLayer === "net"
      ? `₹${Number(item.costs.net_per_quintal_inr).toLocaleString("en-IN")}/q net`
      : mapLayer === "modal"
        ? `₹${Number(item.mandi.modal_price_inr ?? 0).toLocaleString("en-IN")}/q`
        : item.mandi.freshness,
  ]));
  function adjustQuantity(amount: number) {
    setQuantity((current) => Math.min(10000, Math.max(0.1, Math.round((current + amount) * 10) / 10)));
  }

  return (
    <>
      <div className="page-heading-row"><div><span className="eyebrow">PRICE EXPLORER</span><h1>Where should you sell?</h1><p>Compare backend-ranked mandis by the value left after costs.</p></div></div>
      <section className="explorer-controls" aria-label="Market search controls">
        <label><span>Crop</span><span className="control-with-icon"><Sprout size={16} /><select value={crop} onChange={(event) => setCrop(event.target.value)}><option value="">Select crop</option>{crops.data?.data.map((item) => <option value={item.id} key={item.id}>{item.name.en}</option>)}</select></span></label>
        <div className="quantity-control"><span>Quantity</span><div><button type="button" aria-label="Decrease quantity" onClick={() => adjustQuantity(-1)}><Minus size={16} /></button><input aria-label="Quantity in quintal" type="number" min="0.1" max="10000" step="0.1" value={quantity} onChange={(event) => setQuantity(Math.min(10000, Math.max(0.1, Number(event.target.value) || 0.1)))} /><button type="button" aria-label="Increase quantity" onClick={() => adjustQuantity(1)}><Plus size={16} /></button><span>q</span></div></div>
        <label><span>Location</span><span className="control-with-icon location-control"><MapPin size={16} /><strong>{liveLocation.loading ? "Finding location…" : liveLocation.location.source === "live" ? "Live location" : "Maharashtra fallback"}</strong></span></label>
        <button className="primary-button explorer-search" type="button" onClick={() => void recommend.refetch()}><Search size={16} />Find markets</button>
        <div className="map-layer-toggle" aria-label="Map display layer">{(["net","modal","freshness"] as const).map((layer) => <button type="button" className={mapLayer === layer ? "active" : ""} onClick={() => setMapLayer(layer)} key={layer}>{layer === "net" ? "Net return" : layer === "modal" ? "Modal price" : "Freshness"}</button>)}</div>
      </section>
      {recommend.isPending ? <LoadingState /> : recommend.isError ? <ErrorState error={recommend.error} retry={() => void recommend.refetch()} /> : recommendations.length ? (
        <div className="explorer-layout">
          <section className="card explorer-list">
            <div className="section-title"><div><span className="eyebrow">RANKED RESULTS</span><h2>{recommendations.length} markets found</h2></div><span className="data-chip">DEMO</span></div>
            <div className="market-list">{recommendations.map((item: Recommendation) => (
              <button type="button" key={item.mandi.id} className={selected === item.mandi.id ? "market-row selected" : "market-row"} onClick={() => setSelected(item.mandi.id)}>
                <span className="market-rank">{item.rank}</span>
                <div className="market-name"><strong>{item.mandi.name}</strong><span>{item.distance_km} km · {item.mandi.freshness}</span></div>
                <div className="market-value"><strong>₹{Number(item.costs.net_per_quintal_inr).toLocaleString("en-IN")}/q</strong><span>₹{Number(item.costs.total_net_inr).toLocaleString("en-IN")} total</span></div>
              </button>
            ))}</div>
          </section>
          <section className="explorer-map-column">
            <div className="card explorer-map"><IndiaMap mandis={recommendations.map((item) => item.mandi)} farmerLocation={liveLocation.location} selectedId={selected} onSelect={setSelected} markerTextById={markerTextById} /><div className="map-legend"><span><i className="legend-dot fresh-dot" />Fresh</span><span><i className="legend-dot stale-dot" />Stale</span><span><i className="legend-dot old-dot" />Old</span><small>OpenStreetMap · ranked by net return</small></div></div>
            {selectedRecommendation && <article className="card mandi-detail">
              <div className="mandi-detail-head"><div><span className="eyebrow">SELECTED MARKET</span><h2>{selectedRecommendation.mandi.name}</h2></div><span className={`freshness-chip ${selectedRecommendation.mandi.freshness.toLowerCase()}`}>{selectedRecommendation.mandi.freshness}</span></div>
              <div className="cost-grid"><div><span>Modal price</span><strong>₹{Number(selectedRecommendation.mandi.modal_price_inr ?? 0).toLocaleString("en-IN")}/q</strong></div><div><span>Net per quintal</span><strong>₹{Number(selectedRecommendation.costs.net_per_quintal_inr).toLocaleString("en-IN")}</strong></div><div><span>Total for {quantity} q</span><strong>₹{Number(selectedRecommendation.costs.total_net_inr).toLocaleString("en-IN")}</strong></div></div>
              <a className="primary-button" target="_blank" rel="noreferrer" href={`https://www.google.com/maps/dir/?api=1&destination=${selectedRecommendation.mandi.location.lat},${selectedRecommendation.mandi.location.lng}`}><Navigation size={15} />Navigate</a>
            </article>}
          </section>
        </div>
      ) : <EmptyState label="No ranked markets found. Try a larger radius or another crop." />}
    </>
  );
}
