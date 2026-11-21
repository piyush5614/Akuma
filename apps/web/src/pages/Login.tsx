import { FormEvent, useState } from "react";
import { Building2, Eye, EyeOff, LockKeyhole, ShieldCheck, Sprout, Zap } from "lucide-react";
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
  const [showPassword, setShowPassword] = useState(false);
  return (
    <main className="login-page">
      <section className="login-card" aria-label="FairFarm sign in">
        <header className="login-header">
          <span className="login-logo"><Sprout size={34} /></span>
          <h1>FairFarm</h1>
          <p>Farmer Market Intelligence</p>
          <span className="login-feature"><Zap size={15} /> Professional market decisions</span>
        </header>
        <div className="login-body">
          <form onSubmit={submit}>
            <label>Email address or Officer ID
              <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="username" placeholder="Email or ID" required />
            </label>
            <label>Password
              <span className="password-field">
                <input value={password} onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} autoComplete="current-password" placeholder="Enter your password" required />
                <button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)}>
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </span>
            </label>
            <div className="login-options"><label><input type="checkbox" /> Remember me</label><button type="button" className="text-button">Forgot password?</button></div>
            {error && <div className="login-error" role="alert">{error}</div>}
            <button className="login-submit" type="submit"><LockKeyhole size={18} /> Sign in to dashboard</button>
          </form>
          <div className="demo-divider"><span>DEMO ACCOUNTS</span></div>
          <div className="demo-grid">
            <button type="button" onClick={() => { setEmail("admin@example.com"); setPassword("change-me"); }}><ShieldCheck size={20} /><span><strong>Admin</strong><small>admin123</small></span></button>
            <button type="button" onClick={() => { setEmail("admin@example.com"); setPassword("change-me"); }}><Building2 size={20} /><span><strong>Officer</strong><small>officer123</small></span></button>
          </div>
        </div>
      </section>
    </main>
  );
}
