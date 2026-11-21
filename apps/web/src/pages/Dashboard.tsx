import { useQuery } from "@tanstack/react-query";
import { ArrowRight, CircleDollarSign, MapPin, RefreshCw, Sprout, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/State";

export function Dashboard() {
  const query = useQuery({ queryKey: ["recommend", "onion"], queryFn: () => api.recommend("onion", 10) });
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} retry={() => void query.refetch()} />;
  const items = query.data.data.recommendations;
  const freshCount = items.filter((item) => item.mandi.freshness === "FRESH").length;
  return (
    <>
      <section className="page-heading-row">
        <div><span className="eyebrow">MARKET OVERVIEW</span><h1>Welcome back, Officer</h1><p>Real mandi intelligence for better selling decisions.</p></div>
        <button className="secondary-button" type="button" onClick={() => void query.refetch()}><RefreshCw size={16} /> Refresh</button>
      </section>
      <section className="dashboard-banner">
        <span className="banner-icon"><Sprout size={28} /></span>
        <div><span>Today's best net return</span><h2>{items[0]?.mandi.name ?? "No ranked mandi"} <small>· Onion</small></h2></div>
        <div className="banner-value"><strong>₹{Number(items[0]?.costs.total_net_inr ?? 0).toLocaleString("en-IN")}</strong><span>for 10 quintal</span></div>
      </section>
      <section className="metric-grid">
        <article className="metric-card blue"><div><span>Fresh reports</span><strong>{freshCount} / {items.length}</strong><small>Latest trustworthy data</small></div><span className="metric-icon"><RefreshCw size={20} /></span></article>
        <article className="metric-card green"><div><span>Top mandi</span><strong>{items[0]?.mandi.name ?? "—"}</strong><small>Best net return nearby</small></div><span className="metric-icon"><TrendingUp size={20} /></span></article>
        <article className="metric-card purple"><div><span>Net per quintal</span><strong>₹{Number(items[0]?.costs.net_per_quintal_inr ?? 0).toLocaleString("en-IN")}</strong><small>After transport and fees</small></div><span className="metric-icon"><CircleDollarSign size={20} /></span></article>
        <article className="metric-card amber"><div><span>Data status</span><strong>{query.data.is_demo ? "DEMO" : "LIVE"}</strong><small>Replace with validated reports</small></div><span className="metric-icon"><MapPin size={20} /></span></article>
      </section>
      <section className="dashboard-grid">
        <article className="card ranked-card">
          <div className="section-title"><div><span className="eyebrow">RANKED MARKETS</span><h2>Top mandis</h2></div><Link className="view-link" to="/explorer">View explorer <ArrowRight size={15} /></Link></div>
          {items.length ? <div className="ranked-list">{items.map((item) => (
            <div className="ranked-row" key={item.mandi.id}>
              <span className="rank-number">{item.rank}</span>
              <div className="rank-market"><strong>{item.mandi.name}</strong><span>{item.distance_km} km · {item.mandi.freshness}</span></div>
              <div className="rank-value"><strong>₹{Number(item.costs.total_net_inr).toLocaleString("en-IN")}</strong><span>total net</span></div>
            </div>
          ))}</div> : <EmptyState />}
        </article>
        <article className="card sell-card">
          <span className="eyebrow">SELL GUIDANCE</span>
          <h2>{query.data.data.sell_or_wait.decision.replaceAll("_", " ")}</h2>
          <p>{query.data.data.sell_or_wait.reason.en}</p>
          <small>{query.data.data.sell_or_wait.disclaimer}</small>
          <Link className="primary-button" to="/insights">View signals <ArrowRight size={15} /></Link>
        </article>
      </section>
    </>
  );
}
