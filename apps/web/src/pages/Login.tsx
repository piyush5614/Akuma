import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try { const result = await api.login(email, password); localStorage.setItem("fairfarm_token", result.data.access_token); navigate("/"); } catch (reason) { setError(reason instanceof Error ? reason.message : "Sign in failed."); }
  }
  return <div className="login-page"><div className="login-card"><div className="brand"><span>F</span> FairFarm</div><span className="eyebrow">OFFICER DASHBOARD</span><h1>Welcome back.</h1><p>Sign in to see what reaches farmers after costs.</p><form onSubmit={submit}><label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label><label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required /></label>{error && <div className="error">{error}</div>}<button className="primary" type="submit">Sign in →</button></form></div></div>;
}
