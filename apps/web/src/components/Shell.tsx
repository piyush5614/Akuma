import { Bell, Bot, BarChart3, Database, LayoutDashboard, Languages, LogOut, Map, Search, Settings, List, Sprout, UserCircle } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import type { Language } from "../api/client";
import { messages } from "../i18n/messages";

const links = [
  ["/", "overview", LayoutDashboard], ["/explorer", "explorer", Search], ["/regions", "regions", Map],
  ["/insights", "insights", BarChart3], ["/saathi", "saathi", Bot], ["/data", "data", Database], ["/settings", "settings", Settings], ["/queries", "queries", List],
] as const;

export function Shell({ children, language, setLanguage }: { children: React.ReactNode; language: Language; setLanguage: (language: Language) => void }) {
  const t = messages[language];
  const navigate = useNavigate();
  function logout() {
    localStorage.removeItem("fairfarm_token");
    navigate("/login");
  }
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink className="brand" to="/" aria-label="FairFarm overview">
          <span className="brand-mark"><Sprout size={24} /></span>
          <span>FairFarm</span>
        </NavLink>
        <div className="sidebar-label">FARMER INTELLIGENCE</div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {links.map(([to, key, Icon]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <Icon size={19} /><span>{t[key]}</span>
            </NavLink>
          ))}
        </nav>
        <button className="sidebar-demo" type="button" title="This application uses deterministic demo data">
          <span className="demo-dot" />{t.demo}
        </button>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-kicker">Maharashtra · Agriculture intelligence</span>
            <strong>{t.title}</strong>
          </div>
          <div className="topbar-actions">
            <label className="language-control">
              <Languages size={17} />
              <select aria-label="Language" value={language} onChange={(event) => setLanguage(event.target.value as Language)}>
                <option value="en">English</option><option value="mr">मराठी</option><option value="hi">हिन्दी</option>
              </select>
            </label>
            <button className="icon-button" type="button" aria-label="Notifications"><Bell size={19} /><span className="notification-dot">1</span></button>
            <button className="icon-button" type="button" aria-label="Account"><UserCircle size={21} /></button>
            <button className="icon-button logout-button" type="button" aria-label="Log out" onClick={logout}><LogOut size={18} /></button>
          </div>
        </header>
        <div className="context-bar" aria-label="Current recommendation context">
          <div><span>Crop</span><strong>Onion</strong></div>
          <div><span>Quantity</span><strong>10 quintal</strong></div>
          <div><span>Location</span><strong>Maharashtra</strong></div>
          <span className="context-demo">DEMO</span>
        </div>
        <div className="page-content">{children}</div>
      </main>
    </div>
  );
}
