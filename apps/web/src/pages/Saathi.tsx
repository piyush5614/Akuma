import { FormEvent, useEffect, useMemo, useState } from "react";
import { Bot, MapPin, Mic, Send, ShieldCheck, Sparkles, ThumbsDown, ThumbsUp, Volume2 } from "lucide-react";
import { api, Crop, LocationContext, RecommendResult } from "../api/client";

type Message = { role: "user" | "assistant"; text: string; intent?: string; grounded?: boolean; requestId?: string };
type SpeechResultEvent = { results: ArrayLike<{ 0: { transcript: string } }> };
type SpeechRecognitionInstance = { continuous: boolean; interimResults: boolean; lang: string; start: () => void; stop: () => void; onresult: ((event: SpeechResultEvent) => void) | null; onend: (() => void) | null };
type SpeechRecognitionConstructor = new () => SpeechRecognitionInstance;

const starters = [
  "Which nearby mandi gives the best net return?",
  "Should I sell my onion now?",
  "What is net profit?",
];

export function Saathi() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [category, setCategory] = useState<Crop["category"]>("vegetable");
  const [selectedCrop, setSelectedCrop] = useState("onion");
  const [quantity, setQuantity] = useState("10");
  const [waterAvailability, setWaterAvailability] = useState<"low" | "medium" | "high">("medium");
  const [lat, setLat] = useState("18.52");
  const [lng, setLng] = useState("73.86");
  const [marketResult, setMarketResult] = useState<RecommendResult>();
  const [nextCropSuggestions, setNextCropSuggestions] = useState<{ crop: { crop_id: string; risk_adjusted_midpoint_inr_per_acre: string; water_fit: string }; reason: string }[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string>();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Namaskar! I’m Saathi. Ask me which mandi pays more, today’s price, or whether to sell now." },
  ]);
  const [flowError, setFlowError] = useState("");
  const [listening, setListening] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("fairfarm_saathi_history");
    if (saved) {
      try { setMessages(JSON.parse(saved) as Message[]); } catch { localStorage.removeItem("fairfarm_saathi_history"); }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("fairfarm_saathi_history", JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    void api.crops().then((response) => setCrops(response.data)).catch(() => setFlowError("Crop catalogue could not be loaded."));
  }, []);

  const categoryCrops = useMemo(() => crops.filter((crop) => crop.category === category), [crops, category]);
  const location: LocationContext = { lat: Number(lat) || 18.52, lng: Number(lng) || 73.86, source: "fallback" };

  async function findMarkets() {
    setFlowError("");
    const amount = Number(quantity);
    if (!selectedCrop || !Number.isFinite(amount) || amount <= 0) {
      setFlowError("Choose a crop and enter a valid quantity.");
      return;
    }
    try {
      const response = await api.recommend(selectedCrop, amount, location);
      setMarketResult(response.data);
    } catch (reason) {
      setFlowError(reason instanceof Error ? reason.message : "Markets could not be loaded.");
    }
  }

  async function suggestNextCrops() {
    try {
      const response = await api.nextCrops(category, [selectedCrop], waterAvailability);
      setNextCropSuggestions(response.data);
    } catch (reason) {
      setFlowError(reason instanceof Error ? reason.message : "Crop suggestions could not be loaded.");
    }
  }

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || sending) return;
    setInput("");
    setError("");
    setMessages((current) => [...current, { role: "user", text: message }]);
    setSending(true);
    try {
      const response = await api.saathiChat(message, sessionId, location);
      setSessionId(response.data.session_id);
      setMessages((current) => [...current, {
        role: "assistant",
        text: response.data.reply.text,
        intent: response.data.meta.intent,
        grounded: response.data.meta.grounded,
        requestId: response.data.meta.request_id,
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

  function speak(text: string) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-IN";
    window.speechSynthesis.speak(utterance);
  }

  function listen() {
    const speechWindow = window as unknown as { SpeechRecognition?: SpeechRecognitionConstructor; webkitSpeechRecognition?: SpeechRecognitionConstructor };
    const Recognition = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    if (!Recognition) {
      setError("Voice input is not supported in this browser.");
      return;
    }
    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript;
      if (transcript) setInput(transcript);
    };
    recognition.onend = () => setListening(false);
    setListening(true);
    recognition.start();
  }

  async function feedback(message: Message, rating: "up" | "down") {
    if (!message.requestId) return;
    try { await api.saathiFeedback(message.requestId, rating); } catch { return; }
  }

  return <div className="saathi-page">
    <div className="saathi-heading">
      <div><span className="eyebrow">SAATHI</span><h2>Your farming companion</h2><p>Tell me your crop, quantity, and location. I’ll compare markets and help you plan the next crop.</p></div>
      <div className="saathi-location"><MapPin size={16} /> Manual location</div>
    </div>
    <section className="guided-flow card">
      <div className="guided-title"><div><span className="eyebrow">SMART MARKET FINDER</span><h3>What are you selling?</h3></div><span>Step 1 · 3</span></div>
      <div className="guided-label">Crop type</div>
      <div className="guided-options">{(["vegetable", "grain", "fruit"] as const).map((item) => <button className={category === item ? "selected" : ""} type="button" key={item} onClick={() => { setCategory(item); setSelectedCrop(""); }}>{item === "vegetable" ? "Vegetables" : item === "grain" ? "Grains" : "Fruits"}</button>)}</div>
      <div className="guided-label">Select crop</div>
      <div className="crop-options">{categoryCrops.map((crop) => <button className={selectedCrop === crop.id ? "selected" : ""} type="button" key={crop.id} onClick={() => setSelectedCrop(crop.id)}>{crop.name.en}<small>{crop.name.hi} · {crop.name.mr}</small></button>)}</div>
      <div className="guided-grid"><label>Quantity (quintal)<input type="number" min="0.1" step="0.1" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label><label>Latitude<input value={lat} onChange={(event) => setLat(event.target.value)} /></label><label>Longitude<input value={lng} onChange={(event) => setLng(event.target.value)} /></label></div>
      <div className="guided-actions"><button className="primary" type="button" onClick={() => void findMarkets()}>Find best markets</button><label>Water for next crop<select value={waterAvailability} onChange={(event) => setWaterAvailability(event.target.value as "low" | "medium" | "high")}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label><button type="button" onClick={() => void suggestNextCrops()}>Suggest my next crop</button></div>
      {flowError && <p className="chat-error">{flowError}</p>}
      {marketResult && <div className="market-result"><div><strong>Best market: {marketResult.recommendations[0]?.mandi.name ?? "No fresh market found"}</strong><span>{marketResult.recommendations[0] ? `₹${marketResult.recommendations[0].costs.total_net_inr} total net · ${marketResult.recommendations[0].distance_km} km` : "Try a larger radius or another crop."}</span></div><b>{marketResult.sell_or_wait.decision}: {marketResult.sell_or_wait.reason.en}</b></div>}
      {nextCropSuggestions.length > 0 && <div className="next-crops"><strong>Crop ideas for your farm</strong>{nextCropSuggestions.map((suggestion) => <div key={suggestion.crop.crop_id}><b>{crops.find((crop) => crop.id === suggestion.crop.crop_id)?.name.en ?? suggestion.crop.crop_id}</b><span>{suggestion.reason}</span></div>)}</div>}
    </section>
    <div className="saathi-layout">
      <section className="chat-shell">
        <div className="chat-header"><div className="saathi-avatar"><Bot size={20} /></div><div><strong>Saathi</strong><span>FairFarm AI assistant</span></div><button type="button" className="chat-clear" onClick={() => setMessages([{ role: "assistant", text: "Chat history cleared. How can I help?" }])}>Clear chat</button><Sparkles size={18} className="chat-sparkle" /></div>
        <div className="chat-messages">
          {messages.map((message, index) => <div className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
            {message.role === "assistant" && <div className="message-avatar"><Bot size={15} /></div>}
            <div className="message-body"><p>{message.text}</p>{message.intent && <small>{message.intent}{message.grounded ? " · grounded" : " · fallback"}</small>}
              {message.role === "assistant" && <div className="message-actions"><button type="button" aria-label="Read message aloud" onClick={() => speak(message.text)}><Volume2 size={14} /></button>{message.requestId && <><button type="button" aria-label="Helpful answer" onClick={() => void feedback(message, "up")}><ThumbsUp size={14} /></button><button type="button" aria-label="Unhelpful answer" onClick={() => void feedback(message, "down")}><ThumbsDown size={14} /></button></>}</div>}
            </div>
          </div>)}
          {sending && <div className="chat-message assistant"><div className="message-avatar"><Bot size={15} /></div><div className="message-body typing"><i /><i /><i /></div></div>}
        </div>
        {error && <div className="chat-error">{error}</div>}
        <div className="starter-row">{starters.map((starter) => <button type="button" key={starter} onClick={() => selectStarter(starter)}>{starter}</button>)}</div>
        <form className="chat-composer" onSubmit={(event) => void sendMessage(event)}>
          <textarea aria-label="Message Saathi" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Message Saathi..." rows={1} maxLength={500} />
          <button type="button" aria-label={listening ? "Listening" : "Use microphone"} className={listening ? "mic-button listening" : "mic-button"} onClick={listen}><Mic size={18} /></button>
          <button type="submit" aria-label="Send message" disabled={!input.trim() || sending}><Send size={18} /></button>
        </form>
        <p className="chat-disclaimer"><ShieldCheck size={14} /> Guidance only, not a guarantee · Demo market data</p>
      </section>
    </div>
  </div>;
}
