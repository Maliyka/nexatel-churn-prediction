// src/components/InsightsTab.jsx
import { useEffect, useState } from "react";
import { getDashboardStats } from "../api";

function StatCard({ label, value, sub }) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <span className="stat-value mono">{value}</span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

function BarRow({ label, pct, max }) {
  const width = Math.max(4, (pct / max) * 100);
  return (
    <div className="bar-row">
      <span className="bar-label">{label}</span>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${width}%` }} />
      </div>
      <span className="bar-value mono">{pct.toFixed(1)}%</span>
    </div>
  );
}

export default function InsightsTab() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="card"><p className="result-error">Couldn't load portfolio stats: {error}</p></div>;
  if (!stats) return <div className="card"><p>Loading portfolio insights…</p></div>;

  const contractMax = Math.max(...stats.churn_by_contract.map((c) => c.churn_rate_pct));
  const internetMax = Math.max(...stats.churn_by_internet_service.map((c) => c.churn_rate_pct));

  return (
    <div className="insights-layout">
      <div className="stat-grid">
        <StatCard label="Overall churn rate" value={`${stats.overall_churn_rate_pct}%`} sub={`${stats.churned_customers.toLocaleString()} of ${stats.total_customers.toLocaleString()} customers`} />
        <StatCard label="Monthly revenue at risk" value={`$${stats.monthly_revenue_at_risk.toLocaleString()}`} />
        <StatCard label="Annualized revenue at risk" value={`$${(stats.annualized_revenue_at_risk / 1e6).toFixed(2)}M`} />
        <StatCard label="Model recall (churn class)" value={`${stats.model_recall_pct}%`} sub={stats.model_name} />
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Churn rate by contract type</h2>
          <p className="card-subtitle">Source: SQL query #2, database/queries.sql</p>
        </div>
        <div className="bar-list">
          {stats.churn_by_contract.map((c) => (
            <BarRow key={c.contract} label={c.contract} pct={c.churn_rate_pct} max={contractMax} />
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Churn rate by internet service</h2>
          <p className="card-subtitle">Source: SQL query #3, database/queries.sql</p>
        </div>
        <div className="bar-list">
          {stats.churn_by_internet_service.map((c) => (
            <BarRow key={c.internet_service} label={c.internet_service} pct={c.churn_rate_pct} max={internetMax} />
          ))}
        </div>
      </div>

      <div className="card highlight-card">
        <div className="card-header">
          <h2>Sharpest identifiable risk segment</h2>
          <p className="card-subtitle">Source: SQL query #9, database/queries.sql</p>
        </div>
        <p className="highlight-stat mono">{stats.highest_risk_segment.churn_rate_pct}%</p>
        <p>{stats.highest_risk_segment.description} — {stats.highest_risk_segment.segment_size.toLocaleString()} customers in this segment today.</p>
      </div>
    </div>
  );
}
