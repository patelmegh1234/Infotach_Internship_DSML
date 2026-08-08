// Fathima, Upload Date: 2026-07-28
// Interactive Model Performance & Evaluation Analytics Panel
import { useEffect, useState } from "react";
import { BarChart2, Cpu, CheckCircle2, Award, Zap } from "lucide-react";
import { getModelMetrics, type ModelMetricsData } from "../api/client";

export function AnalyticsPanel() {
  const [metrics, setMetrics] = useState<ModelMetricsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelMetrics().then((data) => {
      setMetrics(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="panel empty-state">
        <Cpu className="spin" size={28} />
        <span>Loading model evaluation metrics...</span>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="panel empty-state">
        <p>No model metrics found. Please train the model artifact.</p>
      </div>
    );
  }

  return (
    <div className="analytics-view" style={{ display: "grid", gap: "20px" }}>
      {/* Metric Highlighting Banner */}
      <div className="metrics-row">
        <div className="metric-card">
          <span>Best Classifier</span>
          <strong>{metrics.best_model.replace(/_/g, " ").toUpperCase()}</strong>
        </div>
        <div className="metric-card">
          <span>4-Class Holdout Accuracy</span>
          <strong>{(metrics.holdout_accuracy * 100).toFixed(2)}%</strong>
        </div>
        <div className="metric-card">
          <span>Holdout Macro F1 Score</span>
          <strong>{(metrics.holdout_f1_macro * 100).toFixed(2)}%</strong>
        </div>
        <div className="metric-card">
          <span>Voice Binary Accuracy</span>
          <strong>{(metrics.voice_binary_accuracy * 100).toFixed(2)}%</strong>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Model Comparison Table */}
        <div className="panel">
          <div className="panel-heading">
            <h2>
              <Award size={18} /> Model Comparison Benchmark
            </h2>
          </div>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>5-Fold CV Acc</th>
                <th>CV Macro F1</th>
                <th>CV Time</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(metrics.comparison).map(([name, stats]) => (
                <tr key={name} style={{ fontWeight: name === metrics.best_model ? 800 : 400 }}>
                  <td style={{ textTransform: "capitalize" }}>
                    {name.replace(/_/g, " ")} {name === metrics.best_model && "🏆"}
                  </td>
                  <td>{(stats.cv_accuracy_mean * 100).toFixed(2)}%</td>
                  <td>{(stats.cv_f1_macro_mean * 100).toFixed(2)}%</td>
                  <td>{stats.cv_seconds}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Confusion Matrix Visual Grid */}
        <div className="panel">
          <div className="panel-heading">
            <h2>
              <BarChart2 size={18} /> Confusion Matrix (Holdout Set)
            </h2>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="custom-table" style={{ textAlign: "center" }}>
              <thead>
                <tr>
                  <th>True \ Predicted</th>
                  {metrics.labels.map((lbl) => (
                    <th key={lbl} style={{ fontSize: "0.7rem" }}>
                      {lbl.replace("_wf_2s", "").replace(/_/g, " ")}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.confusion_matrix.map((row, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 800, fontSize: "0.75rem", textTransform: "capitalize" }}>
                      {metrics.labels[i].replace("_wf_2s", "").replace(/_/g, " ")}
                    </td>
                    {row.map((val, j) => (
                      <td
                        key={j}
                        style={{
                          backgroundColor: i === j ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.05)",
                          fontWeight: i === j ? 900 : 500,
                        }}
                      >
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Dataset & Feature Count Summary */}
      <div className="panel">
        <div className="panel-heading">
          <h2>
            <Zap size={18} /> Validation & Pipeline Metadata
          </h2>
        </div>
        <div className="metrics-row">
          <div className="metric-card">
            <span>Trained Dataset Rows</span>
            <strong>{metrics.dataset_rows.toLocaleString()} samples</strong>
          </div>
          <div className="metric-card">
            <span>Audio Feature Matrix</span>
            <strong>{metrics.feature_count} Acoustic Features</strong>
          </div>
          <div className="metric-card">
            <span>Validation Strategy</span>
            <strong>Utterance Stratified Group Split</strong>
          </div>
          <div className="metric-card">
            <span>Train / Test Split</span>
            <strong>{metrics.train_rows} Train / {metrics.test_rows} Test</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
