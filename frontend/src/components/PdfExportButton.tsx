// Dimple, Upload Date: 2026-08-02
// PDF Forensic Report Export — uses Blob URL to avoid popup blocker
import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import type { AnalysisResponse } from "../types";

interface PdfExportButtonProps {
  result: AnalysisResponse;
}

export function PdfExportButton({ result }: PdfExportButtonProps) {
  const [exporting, setExporting] = useState(false);

  const exportPdf = () => {
    setExporting(true);
    try {
      const verdict = result.decision === "likely_real" ? "✅ AUTHENTIC" : "🚨 DEEPFAKE DETECTED";

      const topFeatures = result.explanation
        .slice(0, 8)
        .map((e) => {
          const contrib = (e.contribution ?? e.importance ?? 0).toFixed(5);
          return `<tr><td>${e.feature.replace(/_/g, " ")}</td><td>${e.value?.toFixed(4) ?? "N/A"}</td><td style="color:#4f46e5;font-weight:700">${contrib}</td></tr>`;
        })
        .join("");

      const riskRows = result.risk_factors
        .map((r) => `<li>${r}</li>`)
        .join("");

      const probRows = Object.entries(result.class_probabilities)
        .sort(([, a], [, b]) => b - a)
        .map(([cls, p]) => {
          const pct = (p * 100).toFixed(1);
          return `<tr><td>${cls.replace(/_/g, " ")}</td><td>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="flex:1;background:#e5e7eb;border-radius:4px;height:8px">
                <div style="width:${pct}%;background:#4f46e5;height:100%;border-radius:4px"></div>
              </div>
              <span style="font-weight:700;min-width:42px">${pct}%</span>
            </div>
          </td></tr>`;
        })
        .join("");

      const verdictBg = result.decision === "likely_real" ? "#d1fae5" : "#fee2e2";
      const verdictColor = result.decision === "likely_real" ? "#065f46" : "#991b1b";

      const segmentRows = result.segments.length > 0
        ? result.segments.map((s) => `<tr><td>${s.start.toFixed(2)}s – ${s.end.toFixed(2)}s</td><td>${(s.score * 100).toFixed(1)}%</td><td>${s.reason}</td></tr>`).join("")
        : "<tr><td colspan='3' style='color:#6b7280;font-style:italic'>No suspicious segments detected</td></tr>";

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>AcousticSpace Forensic Report – ${result.file_name}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; padding: 40px; color: #111827; font-size: 13px; line-height: 1.5; }
    .header { border-bottom: 3px solid #4f46e5; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
    .header h1 { color: #4f46e5; font-size: 22px; }
    .header .meta { color: #6b7280; font-size: 11px; text-align: right; }
    .verdict { font-size: 18px; font-weight: bold; padding: 14px 18px; border-radius: 8px; background: ${verdictBg}; color: ${verdictColor}; margin: 16px 0; border-left: 5px solid ${verdictColor}; }
    .confidence { font-size: 13px; font-weight: normal; opacity: 0.85; margin-top: 4px; }
    h2 { color: #3730a3; font-size: 14px; margin: 22px 0 8px; padding-bottom: 4px; border-bottom: 1px solid #e5e7eb; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #4f46e5; color: white; padding: 7px 10px; text-align: left; font-size: 12px; }
    td { padding: 6px 10px; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
    tr:nth-child(even) td { background: #f9fafb; }
    ul { padding-left: 18px; }
    li { margin: 3px 0; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }
    .badge-real { background: #d1fae5; color: #065f46; }
    .badge-fake { background: #fee2e2; color: #991b1b; }
    .footer { margin-top: 32px; padding-top: 12px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 11px; text-align: center; }
    @media print {
      body { padding: 20px; }
      @page { margin: 15mm; }
    }
  </style>
  <script>
    // Auto-trigger print dialog so user can Save as PDF immediately
    window.addEventListener('load', function() {
      setTimeout(function() { window.print(); }, 400);
    });
  </script>
</head>
<body>
  <div class="header">
    <div>
      <h1>🔊 AcousticSpace Forensic Report</h1>
      <div style="color:#6b7280;font-size:12px;margin-top:4px">Audio Deepfake Detection via Room Impulse Response</div>
    </div>
    <div class="meta">
      <div>Generated: ${new Date().toLocaleString()}</div>
      <div>File: <strong>${result.file_name}</strong></div>
      <div>Duration: ${result.duration_seconds?.toFixed(2) ?? "N/A"}s | Model: ${result.model_metadata?.model_type ?? "N/A"}</div>
    </div>
  </div>

  <div class="verdict">
    ${verdict}
    <div class="confidence">Confidence: ${(result.confidence * 100).toFixed(1)}% &nbsp;|&nbsp;
      Voice: <span class="badge ${result.voice_authenticity === "real" ? "badge-real" : "badge-fake"}">${result.voice_authenticity ?? "unknown"}</span> &nbsp;
      Background: <span class="badge ${result.background_authenticity === "real" ? "badge-real" : "badge-fake"}">${result.background_authenticity ?? "unknown"}</span> &nbsp;
      Mismatch: <strong>${result.mismatch_detected ? "YES ⚠️" : "NO ✓"}</strong>
    </div>
  </div>

  <h2>Class Probabilities</h2>
  <table><tr><th>Class</th><th>Probability</th></tr>${probRows}</table>

  <h2>Risk Factors</h2>
  <ul>${riskRows}</ul>

  <h2>Top Feature Contributions</h2>
  <table>
    <tr><th>Feature</th><th>Extracted Value</th><th>Contribution Score</th></tr>
    ${topFeatures || "<tr><td colspan='3' style='color:#6b7280;font-style:italic'>No feature data available</td></tr>"}
  </table>

  <h2>Suspicious Audio Segments</h2>
  <table>
    <tr><th>Time Range</th><th>Anomaly Score</th><th>Reason</th></tr>
    ${segmentRows}
  </table>

  <div class="footer">AcousticSpace — Infotact Internship Project 2026 | Team: Megh Patel, Shubhangi Mane, Fathima, Dimple</div>
</body>
</html>`;

      // Use Blob + anchor click — avoids popup blockers entirely
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.target = "_blank";
      anchor.rel = "noopener";
      anchor.click();
      // Small delay to let the browser tab open before revoking
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } finally {
      setExporting(false);
    }
  };

  return (
    <button
      id="pdf-export-btn"
      className="secondary-button"
      onClick={exportPdf}
      disabled={exporting}
      title="Open printable forensic report (use browser Print → Save as PDF)"
      style={{ display: "flex", alignItems: "center", gap: 6 }}
    >
      {exporting ? <Loader2 size={16} className="spinning" /> : <Download size={16} />}
      {exporting ? "Opening…" : "Export Forensic Report (PDF)"}
    </button>
  );
}
