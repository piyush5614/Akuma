import React, { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Database, FileSpreadsheet, RefreshCw, RotateCcw, Save, Settings2, Sprout, Upload } from "lucide-react";
import { api, type AdminSettings } from "../api/client";
import { IndiaMap } from "../components/IndiaMap";
import { EmptyState, ErrorState, LoadingState } from "../components/State";

function PageTitle({ eyebrow, title, text, actions }: { eyebrow: string; title: string; text: string; actions?: React.ReactNode }) {
  return <div className="page-heading-row"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>{actions}</div>;
}

export function Insights() {
  const [crop, setCrop] = useState("onion");
  const [water, setWater] = useState<"low" | "medium" | "high">("medium");
  const crops = useQuery({ queryKey: ["crops"], queryFn: api.crops });
  const seasonality = useQuery({ queryKey: ["seasonality", crop], queryFn: () => api.seasonality(crop) });
  const profits = useQuery({ queryKey: ["crop-profit", water], queryFn: () => api.cropProfit(water) });
  const backtest = useQuery({ queryKey: ["backtest", crop], queryFn: () => api.backtest(crop) });
  return <>
    <PageTitle eyebrow="MARKET INSIGHTS" title="Signals for the next decision" text="Measured seasonality, crop economics, and sell guidance." actions={<label className="page-select"><Sprout size={16} /><select aria-label="Crop" value={crop} onChange={(event) => setCrop(event.target.value)}>{crops.data?.data.map((item) => <option value={item.id} key={item.id}>{item.name.en}</option>)}</select></label>} />
    <div className="insight-grid">
      <section className="card seasonality-card">
        <div className="section-title"><div><span className="eyebrow">SEASONALITY</span><h2>Monthly price index</h2></div><BarChart3 size={19} /></div>
        {seasonality.isPending ? <LoadingState /> : seasonality.isError ? <ErrorState error={seasonality.error} retry={() => void seasonality.refetch()} /> : <>
          <div className="seasonality-summary"><span>Best months <strong>{seasonality.data.data.best_months.join(", ")}</strong></span><span>Lowest months <strong>{seasonality.data.data.worst_months.join(", ")}</strong></span></div>
          <div className="seasonality-chart" aria-label="Monthly seasonality chart">
            {seasonality.data.data.months.map((month) => <div className="seasonality-bar" key={month.month}><span style={{ height: `${Math.min(100, Math.max(12, Number(month.price_index) * 75))}%` }} className={seasonality.data.data.best_months.includes(month.month) ? "best" : seasonality.data.data.worst_months.includes(month.month) ? "worst" : ""} /><small>{month.month}</small></div>)}
          </div>
        </>}
      </section>
      <section className="card backtest-card">
        <div className="section-title"><div><span className="eyebrow">BACKTEST</span><h2>Measured result</h2></div></div>
        {backtest.isPending ? <LoadingState /> : backtest.isError ? <ErrorState error={backtest.error} retry={() => void backtest.refetch()} /> : <div className="backtest-content"><div className="score-ring"><strong>{(Number(backtest.data.data.rule_hit_rate) * 100).toFixed(0)}%</strong><span>Rule hit rate</span></div><div><span>Baseline</span><strong>{(Number(backtest.data.data.baseline_hit_rate) * 100).toFixed(0)}%</strong><small>{backtest.data.data.sample_count} measured samples</small></div></div>}
      </section>
    </div>
    <section className="card profit-card">
      <div className="profit-toolbar"><div><span className="eyebrow">CROP PLANNER</span><h2>Profit and water fit</h2></div><div className="segmented" aria-label="Water availability">{(["low","medium","high"] as const).map((item) => <button type="button" className={water === item ? "active" : ""} onClick={() => setWater(item)} key={item}>{item}</button>)}</div></div>
      {profits.isPending ? <LoadingState /> : profits.isError ? <ErrorState error={profits.error} retry={() => void profits.refetch()} /> : <div className="profit-table">{profits.data.data.slice(0, 8).map((row) => <div className="profit-row" key={row.crop_id}><div><strong>{crops.data?.data.find((item) => item.id === row.crop_id)?.name.en ?? row.crop_id}</strong><span>{row.source} · DEMO assumption</span></div><div><small>Profit range</small><strong>₹{Number(row.price_range_inr_per_quintal[0]).toLocaleString("en-IN")}–₹{Number(row.price_range_inr_per_quintal[1]).toLocaleString("en-IN")}/q</strong></div><div><small>Risk-adjusted midpoint</small><strong>₹{Number(row.risk_adjusted_midpoint_inr_per_acre).toLocaleString("en-IN")}/acre</strong></div><span className={`fit-badge ${row.water_fit}`}>{row.water_fit} water fit</span></div>)}</div>}
    </section>
  </>;
}

export function Regions() {
  const [crop, setCrop] = useState("onion");
  const crops = useQuery({ queryKey: ["crops"], queryFn: api.crops });
  const regions = useQuery({ queryKey: ["regions", crop], queryFn: () => api.regions(crop) });
  const nationalMandis = (regions.data?.data ?? []).map((region) => ({
    id: region.region_id,
    name: region.name,
    district: region.name,
    state: "India",
    freshness: region.freshness,
    modal_price_inr: region.average_modal_price_inr,
    location: region.location,
  }));
  return <>
    <PageTitle eyebrow="REGIONS" title="Compare market districts" text="District activity and modal prices for your selected crop." actions={<label className="page-select"><Sprout size={16} /><select value={crop} onChange={(event) => setCrop(event.target.value)} aria-label="Crop">{crops.data?.data.map((item) => <option value={item.id} key={item.id}>{item.name.en}</option>)}</select></label>} />
    <div className="region-layout">
      <section className="card region-map"><IndiaMap mandis={nationalMandis} /><div className="map-legend"><span><i className="legend-dot fresh-dot" />Fresh</span><span><i className="legend-dot stale-dot" />Stale</span><span><i className="legend-dot old-dot" />Old</span><small>OpenStreetMap · national DEMO markets</small></div></section>
      <aside className="card region-panel"><div className="section-title"><div><span className="eyebrow">DISTRICT SUMMARY</span><h2>Regional activity</h2></div><Database size={18} /></div>
        {regions.isPending ? <LoadingState /> : regions.isError ? <ErrorState error={regions.error} retry={() => void regions.refetch()} /> : regions.data.data.length ? <div className="region-list">{regions.data.data.map((region) => <div className="region-row" key={region.region_id}><div><strong>{region.name}</strong><span>{region.mandi_count} mandi{region.mandi_count === 1 ? "" : "s"}</span></div><strong>₹{region.average_modal_price_inr ? Number(region.average_modal_price_inr).toLocaleString("en-IN") : "—"}</strong></div>)}</div> : <EmptyState />}
      </aside>
    </div>
  </>;
}

export function Data() {
  const [file, setFile] = useState<File>();
  const [preview, setPreview] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  async function selectFile(selected?: File) {
    if (!selected) return;
    setFile(selected); setMessage("");
    const text = await selected.text();
    setPreview(text.split(/\r?\n/).filter(Boolean).slice(0, 6));
  }
  async function upload() {
    if (!file) { setMessage("Choose a CSV file first."); return; }
    setBusy(true); setMessage("");
    try { const result = await api.importCsv(file); setMessage(`Imported ${result.data.imported_records} records; skipped ${result.data.skipped_records}.`); } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Import failed."); } finally { setBusy(false); }
  }
  return <>
    <PageTitle eyebrow="DATA MANAGEMENT" title="Keep the numbers trustworthy" text="Preview and import validated Agmarknet CSV exports." actions={<button className="secondary-button" type="button" onClick={() => inputRef.current?.click()}><Upload size={16} />Choose CSV</button>} />
    <section className="card data-import">
      <div className="data-drop" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void selectFile(event.dataTransfer.files[0]); }}>
        <span className="upload-icon"><FileSpreadsheet size={26} /></span><div><strong>{file?.name ?? "Drop a CSV export here"}</strong><span>{file ? `${(file.size / 1024).toFixed(1)} KB` : "or choose a file from your computer"}</span></div><input ref={inputRef} type="file" accept=".csv,text/csv" onChange={(event) => void selectFile(event.target.files?.[0])} />
      </div>
      {preview.length ? <><div className="csv-preview"><strong>Validation preview</strong>{preview.map((line, index) => <code key={index}>{line}</code>)}</div><div className="data-actions"><button className="primary-button" type="button" onClick={() => void upload()} disabled={busy}><Upload size={15} />{busy ? "Importing…" : "Import records"}</button>{message && <span className="import-message" role="status">{message}</span>}</div></> : <EmptyState label="No CSV selected." />}
    </section>
  </>;
}

export function SettingsPage() {
  const query = useQuery({ queryKey: ["admin-settings"], queryFn: api.getSettings });
  const [settings, setSettings] = React.useState<AdminSettings>();
  const [saved, setSaved] = useState("");
  React.useEffect(() => { if (query.data) setSettings(query.data.data); }, [query.data]);
  async function save() { if (!settings) return; try { const result = await api.updateSettings(settings); setSettings(result.data); setSaved("Settings saved successfully."); } catch (reason) { setSaved(reason instanceof Error ? reason.message : "Unable to save settings."); } }
  function reset() { void query.refetch().then((result) => { if (result.data) setSettings(result.data.data); setSaved("Defaults reloaded."); }); }
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} retry={() => void query.refetch()} />;
  if (!settings) return <LoadingState />;
  return <>
    <PageTitle eyebrow="SYSTEM SETTINGS" title="Tune calculation assumptions" text="Changes immediately affect backend recommendations." actions={<><button className="secondary-button" type="button" onClick={reset}><RotateCcw size={15} />Reset</button><button className="primary-button" type="button" onClick={() => void save()}><Save size={15} />Save changes</button></>} />
    <section className="card settings-card">
      <div className="settings-grid">
        <label>Road factor<input type="number" min="1" step="0.1" value={settings.road_factor} onChange={(event) => setSettings({ ...settings, road_factor: event.target.value })} /></label>
        <label>Transport ₹ / quintal-km<input type="number" min="0" step="0.01" value={settings.transport_rate_per_quintal_km} onChange={(event) => setSettings({ ...settings, transport_rate_per_quintal_km: event.target.value })} /></label>
        <label>Fee percentage<input type="number" min="0" max="1" step="0.001" value={settings.fee_pct} onChange={(event) => setSettings({ ...settings, fee_pct: event.target.value })} /></label>
      </div>
      <div className="shrinkage-section"><div><span className="eyebrow">SHRINKAGE</span><h2>Crop loss assumptions</h2></div><div className="settings-grid">{Object.entries(settings.shrinkage_pct_by_crop).map(([crop, value]) => <label key={crop}>{crop}<input type="number" min="0" max="1" step="0.001" value={value} onChange={(event) => setSettings({ ...settings, shrinkage_pct_by_crop: { ...settings.shrinkage_pct_by_crop, [crop]: event.target.value } })} /></label>)}</div></div>
      <div className="settings-effect"><Settings2 size={18} /><div><strong>Example effect</strong><span>Transport and fees are applied in the backend; the result updates on the next recommendation.</span></div></div>{saved && <p className="saved-message" role="status">{saved}</p>}
    </section>
  </>;
}

export function Queries() {
  const query = useQuery({ queryKey: ["admin-queries"], queryFn: () => api.queries(50, 0) });
  return <>
    <PageTitle eyebrow="QUERY LOG" title="Recent recommendation activity" text="Anonymised officer and farmer search activity." actions={<button className="secondary-button" type="button" onClick={() => void query.refetch()}><RefreshCw size={15} />Refresh</button>} />
    <section className="card query-card">
      {query.isPending ? <LoadingState /> : query.isError ? <ErrorState error={query.error} retry={() => void query.refetch()} /> : query.data.data.items.length ? <div className="query-table"><div className="query-table-head"><span>Time</span><span>Crop</span><span>Radius</span><span>Rounded location</span></div>{query.data.data.items.map((item, index) => <div className="query-row" key={`${item.requested_at}-${index}`}><span>{new Date(item.requested_at).toLocaleString("en-IN")}</span><strong>{item.crop_id}</strong><span>{item.radius_km} km</span><span>{item.location_rounded.join(", ")}</span></div>)}</div> : <EmptyState label="No anonymised queries logged yet." />}
    </section>
  </>;
}
