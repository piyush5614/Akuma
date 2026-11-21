import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Shell } from "./components/Shell";
import { Dashboard } from "./pages/Dashboard";
import { Explorer } from "./pages/Explorer";
import { Data, Insights, Queries, Regions, SettingsPage } from "./pages/SimplePages";
import { Login } from "./pages/Login";
import { Saathi } from "./pages/Saathi";
import "./styles/tokens.css";
import "./styles/app.css";

const queryClient = new QueryClient();
function App() { const [language, setLanguage] = React.useState<"en" | "mr" | "hi">("en"); return <Routes><Route path="/login" element={<Login />} /><Route path="*" element={<Shell language={language} setLanguage={setLanguage}><Routes><Route path="/" element={<Dashboard />} /><Route path="/explorer" element={<Explorer />} /><Route path="/regions" element={<Regions />} /><Route path="/insights" element={<Insights />} /><Route path="/saathi" element={<Saathi />} /><Route path="/data" element={<Data />} /><Route path="/settings" element={<SettingsPage />} /><Route path="/queries" element={<Queries />} /></Routes></Shell>} /></Routes> }
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><QueryClientProvider client={queryClient}><BrowserRouter><App /></BrowserRouter></QueryClientProvider></React.StrictMode>);
