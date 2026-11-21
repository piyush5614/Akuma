import { FormEvent, useState } from "react";
import { Bot, MapPin, Send, ShieldCheck, Sparkles } from "lucide-react";
import { api } from "../api/client";
import { useLiveLocation } from "../hooks/useLiveLocation";

type Message = { role: "user" | "assistant"; text: string; intent?: string; grounded?: boolean };

const starters = [
  "Which nearby mandi gives the best net return?",
  "Should I sell my onion now?",
  "What is net profit?",
];

export function Saathi() {
  const liveLocation = useLiveLocation();
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string>();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Namaskar! I’m Saathi. Ask me which mandi pays more, today’s price, or whether to sell now." },
  ]);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || sending) return;
    setInput("");
    setError("");
    setMessages((current) => [...current, { role: "user", text: message }]);
    setSending(true);
    try {
      const response = await api.saathiChat(message, sessionId, liveLocation.location);
      setSessionId(response.data.session_id);
      setMessages((current) => [...current, {
        role: "assistant",
        text: response.data.reply.text,
        intent: response.data.meta.intent,
        grounded: response.data.meta.grounded,
      }]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Saathi could not answer right now.");
    } finally {
      setSending(false);
    }
  }

  function selectStarter(starter: string) {
    setInput(starter);
  }

  return <div className="saathi-page">
    <div className="saathi-heading">
      <div><span className="eyebrow">SAATHI</span><h2>Your farming companion</h2><p>Ask naturally. I’ll compare nearby mandis and explain what reaches your pocket.</p></div>
      <div className="saathi-location"><MapPin size={16} /> {liveLocation.loading ? "Finding you…" : liveLocation.location.source === "live" ? "Live location enabled" : "Demo location"} </div>
    </div>
    <div className="saathi-layout">
      <section className="chat-shell">
        <div className="chat-header"><div className="saathi-avatar"><Bot size={20} /></div><div><strong>Saathi</strong><span>FairFarm AI assistant</span></div><Sparkles size={18} className="chat-sparkle" /></div>
        <div className="chat-messages">
          {messages.map((message, index) => <div className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
            {message.role === "assistant" && <div className="message-avatar"><Bot size={15} /></div>}
            <div className="message-body"><p>{message.text}</p>{message.intent && <small>{message.intent}{message.grounded ? " · grounded" : " · fallback"}</small>}</div>
          </div>)}
          {sending && <div className="chat-message assistant"><div className="message-avatar"><Bot size={15} /></div><div className="message-body typing"><i /><i /><i /></div></div>}
        </div>
        {error && <div className="chat-error">{error}</div>}
        <div className="starter-row">{starters.map((starter) => <button type="button" key={starter} onClick={() => selectStarter(starter)}>{starter}</button>)}</div>
        <form className="chat-composer" onSubmit={(event) => void sendMessage(event)}>
          <textarea aria-label="Message Saathi" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Message Saathi..." rows={1} maxLength={500} />
          <button type="submit" aria-label="Send message" disabled={!input.trim() || sending}><Send size={18} /></button>
        </form>
        <p className="chat-disclaimer"><ShieldCheck size={14} /> Guidance only, not a guarantee · Demo market data</p>
      </section>
    </div>
  </div>;
}
