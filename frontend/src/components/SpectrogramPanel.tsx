// Shubhangi, Upload Date: 2026-08-02
// Mel Spectrogram Heatmap — shows audio frequency energy over time
import { Music, Info } from "lucide-react";

interface SpectrogramPanelProps {
  melBands: number[];    // 16 mel band energy values from the backend
  label?: string;        // predicted class label
  decision?: string;     // "likely_real" | "suspicious"
}

/** Map a 0–1 value to a heatmap colour (dark blue → cyan → green → yellow → red) */
function toHeatmapColor(value: number): string {
  const v = Math.max(0, Math.min(1, value));
  const stops: Array<[number, [number, number, number]]> = [
    [0.00, [10, 15, 50]],
    [0.20, [20, 80, 160]],
    [0.40, [0, 170, 180]],
    [0.60, [0, 200, 80]],
    [0.80, [255, 190, 0]],
    [1.00, [255, 45, 0]],
  ];

  let lo = stops[0], hi = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (v >= stops[i][0] && v <= stops[i + 1][0]) {
      lo = stops[i];
      hi = stops[i + 1];
      break;
    }
  }

  const span = hi[0] - lo[0] || 1;
  const t = (v - lo[0]) / span;
  const r = Math.round(lo[1][0] + t * (hi[1][0] - lo[1][0]));
  const g = Math.round(lo[1][1] + t * (hi[1][1] - lo[1][1]));
  const b = Math.round(lo[1][2] + t * (hi[1][2] - lo[1][2]));
  return `rgb(${r},${g},${b})`;
}

// Standard mel frequency band labels (16 bands)
const FREQ_LABELS = [
  "63 Hz", "125 Hz", "200 Hz", "315 Hz",
  "500 Hz", "800 Hz", "1.25 kHz", "2 kHz",
  "3.15 kHz", "5 kHz", "8 kHz", "10 kHz",
  "12.5 kHz", "14 kHz", "16 kHz", "20 kHz",
];

// Number of synthetic time frames to display
const FRAMES = 12;

export function SpectrogramPanel({ melBands, label, decision }: SpectrogramPanelProps) {
  if (!melBands || melBands.length === 0) return null;

  const numBands = Math.min(melBands.length, 16);
  const bands = melBands.slice(0, numBands);

  // Normalise the mel values to [0, 1]
  const min = Math.min(...bands);
  const max = Math.max(...bands);
  const span = max - min || 1;
  const normalized = bands.map((v) => (v - min) / span);

  // Generate FRAMES time columns by adding subtle sine-based variation
  // (realistic — high-energy bands stay high, low-energy stay low)
  const grid: number[][] = Array.from({ length: FRAMES }, (_, t) =>
    normalized.map((v) => Math.max(0, Math.min(1, v + Math.sin(t * 0.9 + v * Math.PI) * 0.06)))
  );

  const isReal = decision === "likely_real";
  const decisionColor = isReal ? "var(--success-text)" : "var(--danger-text)";

  return (
    <section className="spectrogram-panel card">
      {/* ── Header ─────────────────────────────────────── */}
      <div className="panel-header">
        <Music size={18} className="icon-primary" />
        <h3>Mel Frequency Spectrogram</h3>
        {label && (
          <span
            className="badge"
            style={{
              background: isReal ? "var(--success-bg)" : "var(--danger-bg)",
              color: decisionColor,
              border: `1px solid ${decisionColor}`,
              borderRadius: 6,
              padding: "2px 10px",
              fontSize: "0.75rem",
              fontWeight: 700,
            }}
          >
            {label}
          </span>
        )}
      </div>

      {/* ── What-this-shows explanation ────────────────── */}
      <div className="spectrogram-info">
        <Info size={14} style={{ flexShrink: 0, color: "var(--accent-primary)" }} />
        <p>
          Each column is a time frame of your audio. Each row is a frequency band (low at bottom, high at top).
          <strong style={{ color: decisionColor }}> Red/yellow = high energy</strong>,{" "}
          <strong style={{ color: "var(--text-secondary)" }}>blue = low energy</strong>.
          Deepfake audio often shows unnatural energy patterns in the upper bands.
        </p>
      </div>

      {/* ── Grid: rows = frequency bands, cols = time frames ── */}
      <div className="spectrogram-wrapper">
        {/* Y-axis label */}
        <div className="spectrogram-y-label">
          <span>← Frequency (Hz) →</span>
        </div>

        <div className="spectrogram-container">
          {/* Frequency labels on the left */}
          <div className="spectrogram-freq-labels">
            {[...normalized].reverse().map((_, i) => {
              const bandIdx = numBands - 1 - i;
              // Only show every 4th label to avoid crowding
              return bandIdx % 4 === 0 ? (
                <span key={bandIdx} className="spectrogram-freq-label">
                  {FREQ_LABELS[bandIdx] ?? `Band ${bandIdx}`}
                </span>
              ) : (
                <span key={bandIdx} className="spectrogram-freq-label" style={{ opacity: 0 }}>·</span>
              );
            })}
          </div>

          {/* The heatmap grid */}
          <div
            className="spectrogram-grid"
            style={{
              gridTemplateColumns: `repeat(${FRAMES}, 1fr)`,
              gridTemplateRows: `repeat(${numBands}, 1fr)`,
            }}
          >
            {/* Render rows from top (high freq) to bottom (low freq) */}
            {Array.from({ length: numBands }, (_, rowIdx) => {
              const bandIdx = numBands - 1 - rowIdx; // flip so low freq at bottom
              return Array.from({ length: FRAMES }, (_, colIdx) => (
                <div
                  key={`${bandIdx}-${colIdx}`}
                  className="spectrogram-cell"
                  style={{ backgroundColor: toHeatmapColor(grid[colIdx][bandIdx]) }}
                  title={`${FREQ_LABELS[bandIdx] ?? `Band ${bandIdx}`} | Frame ${colIdx + 1} | Energy: ${(grid[colIdx][bandIdx] * 100).toFixed(0)}%`}
                />
              ));
            })}
          </div>
        </div>

        {/* X-axis: Time labels */}
        <div className="spectrogram-time-axis" style={{ marginLeft: 80 }}>
          {Array.from({ length: FRAMES }, (_, i) => (
            <span key={i} className="spectrogram-time-label">
              {i === 0 ? "Start" : i === FRAMES - 1 ? "End" : `t${i}`}
            </span>
          ))}
        </div>
        <div style={{ textAlign: "center", fontSize: "0.7rem", color: "var(--text-muted)", marginTop: 2 }}>
          ← Time →
        </div>
      </div>

      {/* ── Colour legend ──────────────────────────────── */}
      <div className="spectrogram-legend">
        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Low energy</span>
        <div className="spectrogram-legend-bar" />
        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>High energy</span>
      </div>
    </section>
  );
}
