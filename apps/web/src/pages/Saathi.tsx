import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { ErrorState, LoadingState } from "../components/State";

export function Saathi() {
  const metrics = useQuery({ queryKey: ["saathi", "metrics"], queryFn: api.saathiMetrics });
  const [message, setMessage] = useState("Which nearby mandi gives the best net return?");
  const [crop, setCrop] = useState("onion");
  const [quantity, setQuantity] = useState("10");
  const [testResult, setTestResult] = useState<Awaited<ReturnType<typeof api.saathiTest>>["data"]>();
  const [testError, setTestError] = useState("");

  async function runTest(event: FormEvent) {
    event.preventDefault();
    setTestError("");
    try {
      setTestResult((await api.saathiTest(message, crop, Number(quantity) || 1)).data);
    } catch (reason) {
      setTestError(reason instanceof Error ? reason.message : "Unable to run Saathi test.");
    }
  }

  return <><div className="page-heading"><span className="eyebrow">SAATHI ADMIN</span><h2>Understand every answer.</h2><p>Monitor language, intent, fallback, refusal, and grounding signals. Demo analytics are anonymized.</p></div>
    {metrics.isPending ? <LoadingState /> : metrics.isError ? <ErrorState error={metrics.error} retry={() => void metrics.refetch()} /> : <><section className="grid stats">
      <article><span className="eyebrow">MESSAGES TODAY</span><strong>{metrics.data.data.messages_per_day.today ?? 0}</strong><span>All platforms</span></article>
      <article><span className="eyebrow">FALLBACK RATE</span><strong>{Math.round(metrics.data.data.fallback_rate * 100)}%</strong><span>Rules or safety fallback</span></article>
      <article><span className="eyebrow">REFUSAL RATE</span><strong>{Math.round(metrics.data.data.refusal_rate * 100)}%</strong><span>Out-of-scope or distress</span></article>
      <article><span className="eyebrow">GROUNDING FAILURES</span><strong>{metrics.data.data.grounding_failure_count}</strong><span>Should remain zero</span></article>
    </section><section className="grid">
      <div className="card"><h2>Provider status</h2><p><b>{metrics.data.data.provider}</b> provider · <b>{metrics.data.data.mode}</b> mode</p><p>Thumbs up: {metrics.data.data.thumbs_ratio.up} · down: {metrics.data.data.thumbs_ratio.down}</p><h3>Top intents</h3>{Object.entries(metrics.data.data.top_intents).map(([intent, count]) => <div className="row" key={intent}><span>{intent}</span><strong>{count}</strong></div>)}</div>
      <div className="card"><h2>Unanswered questions</h2>{metrics.data.data.unanswered_questions.length ? metrics.data.data.unanswered_questions.map((question) => <p key={question}>{question}</p>) : <p className="muted">No unanswered questions yet.</p>}</div>
    </section></>}
    <section className="card form"><h2>Saathi test console</h2><p>Run a server-side test with a sample location. Tool results are shown for inspection.</p><form onSubmit={(event) => void runTest(event)} className="form"><label>Question<input value={message} onChange={(event) => setMessage(event.target.value)} maxLength={500} /></label><label>Crop<input value={crop} onChange={(event) => setCrop(event.target.value)} /></label><label>Quantity (quintal)<input type="number" min="0.1" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label><button className="primary" type="submit">Run test</button></form>{testError && <p className="error">{testError}</p>}{testResult && <div><h3>{testResult.intent} · {testResult.grounded ? "grounded" : "fallback"}</h3><p>{testResult.reply}</p><p>Tools: {testResult.tools_used.join(", ") || "none"}</p><pre>{JSON.stringify(testResult.tool_results, null, 2)}</pre></div>}</section>
  </>;
}
