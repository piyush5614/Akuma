import { BarChart3, Bot, Database, LayoutDashboard, Map, Search, Settings, List } from "lucide-react";
import { NavLink } from "react-router-dom";
import type { Language } from "../api/client";
import { messages } from "../i18n/messages";

const links = [
  ["/", "overview", LayoutDashboard], ["/explorer", "explorer", Search], ["/regions", "regions", Map],
  ["/insights", "insights", BarChart3], ["/saathi", "saathi", Bot], ["/data", "data", Database], ["/settings", "settings", Settings], ["/queries", "queries", List],
] as const;

export function Shell({ children, language, setLanguage }: { children: React.ReactNode; language: Language; setLanguage: (language: Language) => void }) {
  const t = messages[language];
  return <div className="shell"><aside><div className="brand"><span>F</span> FairFarm</div><nav>{links.map(([to, key, Icon]) => <NavLink key={to} to={to} end={to === "/"}><Icon size={18} />{t[key]}</NavLink>)}</nav><div className="demo-label">{t.demo}</div></aside><main><header><div><span className="eyebrow">Maharashtra · Agriculture intelligence</span><h1>{t.title}</h1></div><select aria-label="Language" value={language} onChange={(event) => setLanguage(event.target.value as Language)}><option value="en">English</option><option value="mr">मराठी</option><option value="hi">हिन्दी</option></select></header>{children}</main></div>
}
