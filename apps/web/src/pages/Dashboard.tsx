import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/State";

export function Dashboard() {
  const query = useQuery({ queryKey: ["recommend", "onion"], queryFn: () => api.recommend("onion", 10) });
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} retry={() => void query.refetch()} />;
  const items = query.data.data.recommendations;
  return <><section className="hero"><div><span className="eyebrow">TODAY'S NET RETURN</span><h2>Make the next trip count.</h2><p>Ranked by what reaches you after transport, fees and shrinkage.</p></div><div className="hero-number">₹{Number(items[0]?.costs.total_net_inr ?? 0).toLocaleString("en-IN")}<small>for 10 quintal</small></div></section><section className="grid stats"><article><span className="eyebrow">FRESH REPORTS</span><strong>2 / 3</strong><span>Trust the latest numbers</span></article><article><span className="eyebrow">TOP MANDI</span><strong>{items[0]?.mandi.name ?? "—"}</strong><span>Best net return nearby</span></article><article><span className="eyebrow">DEMO STATUS</span><strong>DEMO</strong><span>Replace with live reports</span></article></section><section className="card"><div className="section-title"><h2>Top mandis</h2><a href="/explorer">View explorer →</a></div>{items.length ? <div className="table">{items.map((item) => <div className="row" key={item.mandi.id}><b>#{item.rank} {item.mandi.name}</b><span>{item.mandi.freshness}</span><strong>₹{Number(item.costs.total_net_inr).toLocaleString("en-IN")}</strong></div>)}</div> : <EmptyState />}</section></>
}
