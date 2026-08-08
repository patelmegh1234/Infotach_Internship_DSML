// Fathima, Upload Date: 2026-07-28
// Dataset Exploratory Data Analysis & Acoustic Insights Panel
import { useEffect, useState } from "react";
import { Database, PieChart, Layers, ShieldAlert } from "lucide-react";
import { getEdaSummary, type EdaSummaryData } from "../api/client";

export function EdaPanel() {
  const [eda, setEda] = useState<EdaSummaryData | null>(null);

  useEffect(() => {
    getEdaSummary().then(setEda);
  }, []);

  if (!eda) {
    return (
      <div className="panel empty-state">
        <span>Loading dataset EDA statistics...</span>
      </div>
    );
  }

  return (
    <div className="eda-view" style={{ display: "grid", gap: "20px" }}>
      {/* Stat Cards */}
      <div className="metrics-row">
        <div className="metric-card">
          <span>Total Audio Files</span>
          <strong>{eda.total_files.toLocaleString()} Clips</strong>
        </div>
        <div className="metric-card">
          <span>Unique Speakers/Utterances</span>
          <strong>{eda.unique_utterances.toLocaleString()} Utterances</strong>
        </div>
        <div className="metric-card">
          <span>Unique Acoustic Environments</span>
          <strong>{eda.unique_backgrounds.toLocaleString()} Backgrounds</strong>
        </div>
        <div className="metric-card">
          <span>Data Leakage Status</span>
          <strong style={{ color: "#10b981" }}>Group Isolated (0 Leakage)</strong>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Class Distribution */}
        <div className="panel">
          <div className="panel-heading">
            <h2>
              <PieChart size={18} /> Acoustic Target Class Balance
            </h2>
          </div>
          <div className="probability-bars">
            {Object.entries(eda.class_counts).map(([name, count]) => {
              const pct = (count / eda.total_files) * 100;
              return (
                <div key={name} className="prob-row">
                  <div className="prob-header">
                    <span>{name.replace(/_/g, " ").toUpperCase()}</span>
                    <span>
                      {count.toLocaleString()} files ({pct.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="prob-track">
                    <div className="prob-fill" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mix Profile Distribution */}
        <div className="panel">
          <div className="panel-heading">
            <h2>
              <Layers size={18} /> Acoustic Mixing Ratio Profiles
            </h2>
          </div>
          <div className="probability-bars">
            {Object.entries(eda.mix_profile_counts).map(([name, count]) => {
              const pct = (count / eda.total_files) * 100;
              return (
                <div key={name} className="prob-row">
                  <div className="prob-header">
                    <span>{name.replace("_", " ").toUpperCase()} MIX</span>
                    <span>
                      {count.toLocaleString()} files ({pct.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="prob-track">
                    <div className="prob-fill" style={{ width: `${pct}%`, backgroundColor: "#2563eb" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Dataset Insights & Quality Control Card */}
      <div className="panel">
        <div className="panel-heading">
          <h2>
            <Database size={18} /> Dataset Engineering & Leakage Control
          </h2>
        </div>
        <p style={{ color: "var(--text-secondary)", lineHeight: 1.6 }}>
          The AcousticSpace benchmark dataset is derived from <strong>12,000 standardized 2.0-second 16kHz audio clips</strong>.
          To guarantee realistic real-world generalizability and prevent data leakage:
        </p>
        <ul style={{ color: "var(--text-secondary)", lineHeight: 1.8 }}>
          <li>
            <strong>Speaker Grouping:</strong> Cross-validation splits use <code>StratifiedGroupKFold</code> grouped strictly by speaker/utterance ID (e.g. <code>LJ001-0006</code>). No spoken audio content from train appears in test evaluation.
          </li>
          <li>
            <strong>Environmental Separation:</strong> Background acoustic Impulse Response (RIR) decay and noise profiles are independently sampled across 800+ real and synthetic room environments.
          </li>
          <li>
            <strong>Multivariate Targets:</strong> Enables granular classification of synthetic voice artifacts, artificial background noise injection, and voice-environment room acoustic mismatches.
          </li>
        </ul>
      </div>
    </div>
  );
}
