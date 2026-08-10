// src/components/ScoreCustomerTab.jsx
import { useState } from "react";
import SignalGauge from "./SignalGauge";
import { predictChurn } from "../api";

const DEFAULTS = {
  gender: "Female",
  senior_citizen: false,
  partner: false,
  dependents: false,
  tenure: 3,
  phone_service: "Yes",
  multiple_lines: "No",
  internet_service: "Fiber optic",
  online_security: "No",
  online_backup: "No",
  device_protection: "No",
  tech_support: "No",
  streaming_tv: "No",
  streaming_movies: "No",
  contract: "Month-to-month",
  paperless_billing: true,
  payment_method: "Electronic check",
  monthly_charges: 75,
  total_charges: "",
};

const SERVICE_OPTIONS = ["Yes", "No"];
const INTERNET_SERVICE_OPTIONS_FOR_ADDONS = ["Yes", "No", "No internet service"];

function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  );
}

function Toggle({ checked, onChange, label }) {
  return (
    <button
      type="button"
      className={`toggle ${checked ? "toggle-on" : ""}`}
      onClick={() => onChange(!checked)}
      aria-pressed={checked}
    >
      <span className="toggle-thumb" />
      <span className="toggle-label">{label}</span>
    </button>
  );
}

export default function ScoreCustomerTab() {
  const [form, setForm] = useState(DEFAULTS);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const update = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  const hasInternet = form.internet_service !== "No";

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...form,
        tenure: Number(form.tenure),
        monthly_charges: Number(form.monthly_charges),
        total_charges: form.total_charges === "" ? null : Number(form.total_charges),
      };
      const res = await predictChurn(payload);
      setResult(res);
    } catch (err) {
      setError(err.message || "Something went wrong scoring this customer.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="score-layout">
      <form className="card form-card" onSubmit={handleSubmit}>
        <div className="card-header">
          <h2>Customer profile</h2>
          <p className="card-subtitle">Enter the account details exactly as they appear in billing/CRM.</p>
        </div>

        <div className="form-section">
          <h3 className="section-label">Profile</h3>
          <div className="form-grid">
            <Field label="Gender">
              <Select value={form.gender} onChange={update("gender")} options={["Female", "Male"]} />
            </Field>
            <Field label="Tenure (months)">
              <input type="number" min="0" max="100" value={form.tenure}
                onChange={(e) => update("tenure")(e.target.value)} />
            </Field>
          </div>
          <div className="toggle-row">
            <Toggle checked={form.senior_citizen} onChange={update("senior_citizen")} label="Senior citizen" />
            <Toggle checked={form.partner} onChange={update("partner")} label="Has partner" />
            <Toggle checked={form.dependents} onChange={update("dependents")} label="Has dependents" />
          </div>
        </div>

        <div className="form-section">
          <h3 className="section-label">Account &amp; billing</h3>
          <div className="form-grid">
            <Field label="Contract">
              <Select value={form.contract} onChange={update("contract")}
                options={["Month-to-month", "One year", "Two year"]} />
            </Field>
            <Field label="Payment method">
              <Select value={form.payment_method} onChange={update("payment_method")}
                options={["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]} />
            </Field>
            <Field label="Monthly charges ($)">
              <input type="number" min="0" step="0.01" value={form.monthly_charges}
                onChange={(e) => update("monthly_charges")(e.target.value)} />
            </Field>
            <Field label="Total charges to date ($)" hint="Leave blank for a brand-new customer">
              <input type="number" min="0" step="0.01" value={form.total_charges}
                onChange={(e) => update("total_charges")(e.target.value)} placeholder="optional" />
            </Field>
          </div>
          <div className="toggle-row">
            <Toggle checked={form.paperless_billing} onChange={update("paperless_billing")} label="Paperless billing" />
          </div>
        </div>

        <div className="form-section">
          <h3 className="section-label">Services</h3>
          <div className="form-grid">
            <Field label="Phone service">
              <Select value={form.phone_service} onChange={update("phone_service")} options={SERVICE_OPTIONS} />
            </Field>
            <Field label="Multiple lines">
              <Select value={form.multiple_lines} onChange={update("multiple_lines")}
                options={["Yes", "No", "No phone service"]} />
            </Field>
            <Field label="Internet service">
              <Select value={form.internet_service} onChange={update("internet_service")}
                options={["DSL", "Fiber optic", "No"]} />
            </Field>
          </div>
          {hasInternet && (
            <div className="form-grid form-grid-addons">
              <Field label="Online security">
                <Select value={form.online_security} onChange={update("online_security")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
              <Field label="Online backup">
                <Select value={form.online_backup} onChange={update("online_backup")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
              <Field label="Device protection">
                <Select value={form.device_protection} onChange={update("device_protection")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
              <Field label="Tech support">
                <Select value={form.tech_support} onChange={update("tech_support")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
              <Field label="Streaming TV">
                <Select value={form.streaming_tv} onChange={update("streaming_tv")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
              <Field label="Streaming movies">
                <Select value={form.streaming_movies} onChange={update("streaming_movies")} options={INTERNET_SERVICE_OPTIONS_FOR_ADDONS} />
              </Field>
            </div>
          )}
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Scoring…" : "Score customer"}
        </button>
      </form>

      <aside className="card result-card">
        <div className="card-header">
          <h2>Risk assessment</h2>
          <p className="card-subtitle">Live score from the deployed model.</p>
        </div>

        {!result && !loading && !error && (
          <div className="result-empty">
            <p>Fill out the profile and click <strong>Score customer</strong> to see this customer's churn risk and the top reasons behind it.</p>
          </div>
        )}

        {loading && <div className="result-empty"><p>Scoring customer…</p></div>}

        {error && (
          <div className="result-error">
            <p><strong>Couldn't score this customer.</strong></p>
            <p>{error}</p>
          </div>
        )}

        {result && !loading && (
          <div className="result-body">
            <SignalGauge probability={result.churn_probability} riskLevel={result.risk_level} />

            <div className="reasons">
              <h3 className="section-label">Top factors</h3>
              <ul className="reasons-list">
                {result.top_reasons.map((r, i) => (
                  <li key={i} className={`reason-item reason-${r.direction === "increases risk" ? "up" : "down"}`}>
                    <span className="reason-arrow">{r.direction === "increases risk" ? "▲" : "▼"}</span>
                    <span className="reason-text">{r.feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="action-callout">
              <h3 className="section-label">Suggested action</h3>
              <p>{result.suggested_action}</p>
            </div>

            <p className="model-footnote mono">Model: {result.model_name}</p>
          </div>
        )}
      </aside>
    </div>
  );
}
