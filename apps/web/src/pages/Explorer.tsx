import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/State";

export function Explorer() {
  const query = useQuery({ queryKey: ["mandis", "onion"], queryFn: () => api.mandis("onion") });
  return <><div className="page-heading"><span className="eyebrow">PRICE EXPLORER</span><h2>Where should you sell?</h2><p>Compare modal price and freshness across nearby mandis.</p></div><div className="card map-placeholder">Map view · OpenStreetMap pins will appear here<div className="map-pins">● Fresh &nbsp; ● Stale &nbsp; ● Old</div></div>{query.isPending ? <LoadingState /> : query.isError ? <ErrorState error={query.error} retry={() => void query.refetch()} /> : query.data.data.length ? <div className="card table">{query.data.data.map((mandi) => <div className="row" key={mandi.id}><b>{mandi.name}</b><span>{mandi.district}</span><span className={`badge ${mandi.freshness.toLowerCase()}`}>{mandi.freshness}</span><strong>₹{mandi.modal_price_inr ?? "—"}</strong></div>)}</div> : <EmptyState />}</>
}
