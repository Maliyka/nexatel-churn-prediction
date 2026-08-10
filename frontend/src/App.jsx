// src/App.jsx
import { useState } from "react";
import ScoreCustomerTab from "./components/ScoreCustomerTab";
import InsightsTab from "./components/InsightsTab";
import "./App.css";

export default function App() {
  const [tab, setTab] = useState("score");

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="brand">
            <span className="brand-mark" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                <path d="M3 17c0-6 4-11 8-11" stroke="var(--signal-low)" strokeWidth="2" strokeLinecap="round" opacity="0.4"/>
                <path d="M6 17c0-4 2.5-8 5-8" stroke="var(--signal-medium)" strokeWidth="2" strokeLinecap="round" opacity="0.7"/>
                <path d="M9 17c0-2 1-4 2-4" stroke="var(--signal-high)" strokeWidth="2" strokeLinecap="round"/>
                <circle cx="11" cy="19" r="1.4" fill="var(--text-primary)"/>
              </svg>
            </span>
            <span className="brand-name">NexaTel <span className="brand-name-light">Churn Console</span></span>
          </div>
          <nav className="tab-nav">
            <button className={`tab-btn ${tab === "score" ? "tab-btn-active" : ""}`} onClick={() => setTab("score")}>
              Score a customer
            </button>
            <button className={`tab-btn ${tab === "insights" ? "tab-btn-active" : ""}`} onClick={() => setTab("insights")}>
              Portfolio insights
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {tab === "score" ? <ScoreCustomerTab /> : <InsightsTab />}
      </main>

      <footer className="app-footer">
        <p>NexaTel Customer Churn Prediction &amp; Retention Intelligence System — internal tool, retention team use only.</p>
      </footer>
    </div>
  );
}
