// src/components/SignalGauge.jsx
// The one deliberate visual signature of this app: churn probability
// rendered as a segmented signal-strength meter (a nod to the telecom
// subject matter) rather than a generic circular progress ring.

const TICK_COUNT = 36;
const START_ANGLE = 180; // left
const END_ANGLE = 0;     // right

function zoneColor(position) {
  if (position >= 0.6) return "var(--signal-high)";
  if (position >= 0.3) return "var(--signal-medium)";
  return "var(--signal-low)";
}

function polar(cx, cy, r, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) };
}

export default function SignalGauge({ probability, riskLevel }) {
  const cx = 130;
  const cy = 130;
  const rInner = 78;
  const rOuter = 100;

  const ticks = Array.from({ length: TICK_COUNT }, (_, i) => {
    const position = i / (TICK_COUNT - 1);
    const angle = START_ANGLE + position * (END_ANGLE - START_ANGLE);
    const inner = polar(cx, cy, rInner, angle);
    const outer = polar(cx, cy, rOuter, angle);
    const isLit = position <= probability;
    return { key: i, inner, outer, color: zoneColor(position), isLit };
  });

  const pct = Math.round(probability * 100);

  const riskColorVar =
    riskLevel === "High" ? "var(--signal-high)" : riskLevel === "Medium" ? "var(--signal-medium)" : "var(--signal-low)";
  const riskDimVar =
    riskLevel === "High" ? "var(--signal-high-dim)" : riskLevel === "Medium" ? "var(--signal-medium-dim)" : "var(--signal-low-dim)";

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      <svg width="260" height="150" viewBox="0 0 260 150">
        {ticks.map((t) => (
          <line
            key={t.key}
            x1={t.inner.x}
            y1={t.inner.y}
            x2={t.outer.x}
            y2={t.outer.y}
            stroke={t.color}
            strokeWidth={5}
            strokeLinecap="round"
            opacity={t.isLit ? 1 : 0.14}
          />
        ))}
        <text
          x={cx}
          y={cy - 6}
          textAnchor="middle"
          fontFamily="var(--font-display)"
          fontSize="40"
          fontWeight="700"
          fill="var(--text-primary)"
        >
          {pct}%
        </text>
        <text
          x={cx}
          y={cy + 18}
          textAnchor="middle"
          fontFamily="var(--font-mono)"
          fontSize="11"
          letterSpacing="0.08em"
          fill="var(--text-secondary)"
        >
          CHURN PROBABILITY
        </text>
      </svg>
      <span
        className="mono"
        style={{
          padding: "4px 14px",
          borderRadius: 999,
          fontSize: 12,
          fontWeight: 600,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          color: riskColorVar,
          background: riskDimVar,
          border: `1px solid ${riskColorVar}`,
        }}
      >
        {riskLevel} risk
      </span>
    </div>
  );
}
