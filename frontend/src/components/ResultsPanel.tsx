// Dimple, Upload Date: 2026-07-28
// Enhanced Forensic Results & Explainability Panel
import { AlertTriangle, CheckCircle2, Gauge, Loader2, ShieldCheck, Zap } from "lucide-react";
import type { AnalysisResponse } from "../types";

type ResultsPanelProps = {
  result: AnalysisResponse | null;
  error: string | null;
  isAnalyzing: boolean;
};

export function ResultsPanel({ result, error, isAnalyzing }: ResultsPanelProps) {
  const suspicious = result?.decision === "suspicious";
  const probabilities = Object.entries(result?.class_probabilities ?? {}).sort((a, b) => b[1] - a[1]);

  return (
    <section className="panel results-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Forensic Verdict & Explainability</p>
          <h2>Analysis Results</h2>
        </div>
        <Gauge size={22} />
      </div>

      {isAnalyzing && (
        <div className="state-row" style={{ padding: "40px 0" }}>
          <Loader2 className="spin" size={28} />
          <span>Computing 118-dim acoustic feature space and running trained ensemble classifier...</span>
        </div>
      )}

      {error && <div className="error-box" style={{ padding: "16px" }}>{error}</div>}

      {!isAnalyzing && !error && !result && (
        <div className="empty-state">Select an audio file or click a demo sample above to run analysis</div>
      )}

      {result && (
        <>
          {/* Verdict Banner */}
          <div className={`verdict-banner ${suspicious ? "danger" : "clear"}`}>
            <div className="verdict-main">
              {suspicious ? <AlertTriangle size={32} /> : <CheckCircle2 size={32} />}
              <div>
                <div className="verdict-title">{suspicious ? "SUSPICIOUS / DEEPFAKE DETECTED" : "AUTHENTIC / LIKELY REAL VOICE"}</div>
                <div className="verdict-sub">Target: {formatLabel(result.predicted_class ?? result.decision)}</div>
              </div>
            </div>
            <div className="confidence-gauge">
              <span>Overall Confidence</span>
              <strong>{toPercent(result.confidence)}</strong>
            </div>
          </div>

          {/* Classification Pills */}
          <div className="metrics-row">
            <InfoCard label="Voice Authenticity" value={formatLabel(result.voice_authenticity ?? "Unknown")} status={result.voice_authenticity === "real"} />
            <InfoCard label="Background Authenticity" value={formatLabel(result.background_authenticity ?? "Unknown")} status={result.background_authenticity === "real"} />
            <InfoCard label="Acoustic Mismatch" value={result.mismatch_detected ? "Mismatch Present" : "Matched Environment"} status={!result.mismatch_detected} />
            <InfoCard label="Audio Duration" value={`${result.duration_seconds.toFixed(2)}s`} status={true} />
          </div>

          {/* Acoustic Features Grid */}
          <div className="metrics-row">
            <Metric label="Reverb Tail Ratio" value={formatFeature(result.features.reverb_tail_ratio)} />
            <Metric label="RIR Decay Slope" value={formatFeature(result.features.rir_decay_slope)} />
            <Metric label="Background Consistency" value={formatFeature(result.features.background_consistency)} />
            <Metric label="Breathing Cadence" value={formatFeature(result.features.breathing_cadence_score)} />
          </div>

          {/* Class Probability Breakdown */}
          {probabilities.length > 0 && (
            <div className="panel" style={{ margin: "20px 0", padding: "16px" }}>
              <h3 style={{ margin: "0 0 14px", fontSize: "0.95rem", fontWeight: 800, textTransform: "uppercase" }}>
                Class Probability Distribution
              </h3>
              <div className="probability-bars">
                {probabilities.map(([label, value]) => (
                  <div className="prob-row" key={label}>
                    <div className="prob-header">
                      <span>{formatLabel(label)}</span>
                      <strong>{toPercent(value)}</strong>
                    </div>
                    <div className="prob-track">
                      <div
                        className={`prob-fill ${value > 0.45 && label !== "real_voice_real_bg" ? "high" : ""}`}
                        style={{ width: `${Math.round(value * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Factors */}
          {result.risk_factors.length > 0 && (
            <div className="risk-list">
              {result.risk_factors.map((factor) => (
                <div key={factor}>{factor}</div>
              ))}
            </div>
          )}

          {/* Suspicious Audio Segment Localization Table */}
          <div style={{ marginTop: "20px" }}>
            <h3 style={{ margin: "0 0 10px", fontSize: "0.95rem", fontWeight: 800, textTransform: "uppercase" }}>
              Localized Acoustic Anomalies
            </h3>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Anomaly Score</th>
                  <th>Forensic Indicator</th>
                </tr>
              </thead>
              <tbody>
                {result.segments.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                      No localized temporal acoustic anomalies detected
                    </td>
                  </tr>
                ) : (
                  result.segments.map((s, idx) => (
                    <tr key={idx}>
                      <td>{s.start.toFixed(2)}s</td>
                      <td>{s.end.toFixed(2)}s</td>
                      <td style={{ color: "#ef4444", fontWeight: 800 }}>{toPercent(s.score)}</td>
                      <td>{s.reason}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Feature Importance Explainability */}
          {result.explanation.length > 0 && (
            <div style={{ marginTop: "20px" }}>
              <h3 style={{ margin: "0 0 10px", fontSize: "0.95rem", fontWeight: 800, textTransform: "uppercase" }}>
                Top Driving Acoustic Features (SHAP / Feature Contribution)
              </h3>
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Feature Name</th>
                    <th>Extracted Sample Value</th>
                    <th>Model Feature Importance</th>
                  </tr>
                </thead>
                <tbody>
                  {result.explanation.slice(0, 6).map((item) => (
                    <tr key={item.feature}>
                      <td style={{ fontWeight: 700 }}>{formatLabel(item.feature)}</td>
                      <td>{item.value.toFixed(4)}</td>
                      <td style={{ color: "var(--accent-primary)", fontWeight: 800 }}>
                        {(item.contribution ?? item.importance ?? 0).toFixed(5)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}

function InfoCard({ label, value, status }: { label: string; value: string; status: boolean }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong style={{ color: status ? "var(--success-text)" : "var(--danger-text)" }}>{value}</strong>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatFeature(value: number | number[] | undefined): string {
  if (typeof value !== "number") return "--";
  return value.toFixed(3);
}

function toPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function formatLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
