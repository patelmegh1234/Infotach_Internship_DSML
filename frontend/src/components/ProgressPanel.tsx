// Dimple, Upload Date: 2026-08-02
// Real-time Analysis Progress Bar Panel
import { CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";
import type { AnalysisProgress } from "../types";

interface ProgressPanelProps {
  progress: AnalysisProgress | null;
}

const STAGES = [
  { key: "validating",          label: "Validating File",             pct: 5  },
  { key: "extracting_features", label: "Extracting Acoustic Features", pct: 30 },
  { key: "classifying",         label: "Running ML Classifier",        pct: 75 },
  { key: "generating_report",   label: "Generating Forensic Report",   pct: 90 },
  { key: "complete",            label: "Analysis Complete",            pct: 100 },
];

function getStageLabel(stage: string): string {
  return STAGES.find((s) => s.key === stage)?.label ?? stage.replace(/_/g, " ");
}

function getCompletedStages(currentStage: string): string[] {
  const idx = STAGES.findIndex((s) => s.key === currentStage);
  return STAGES.slice(0, idx).map((s) => s.key);
}

export function ProgressPanel({ progress }: ProgressPanelProps) {
  // If no WS data yet but we know we're analyzing — show a "submitting" stub
  if (!progress) {
    return (
      <div className="progress-panel">
        <div className="progress-header">
          <Loader2 size={20} className="icon-primary spinning" />
          <span className="progress-title">Submitting audio for analysis…</span>
          <span className="progress-pct">0%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill progress-fill--pulse" style={{ width: "5%" }} />
        </div>
        <p className="progress-hint">Connecting to analysis engine. Please wait…</p>
      </div>
    );
  }

  const pct = progress.progress ?? 0;
  const isError = progress.status === "error";
  const isDone = progress.status === "complete";
  const completedStages = getCompletedStages(progress.stage);

  return (
    <div className="progress-panel">
      <div className="progress-header">
        {isError ? (
          <AlertTriangle size={20} className="icon-error" />
        ) : isDone ? (
          <CheckCircle2 size={20} className="icon-success" />
        ) : (
          <Loader2 size={20} className="icon-primary spinning" />
        )}
        <span className="progress-title">
          {isError ? "Analysis Failed" : isDone ? "Analysis Complete ✓" : "Analyzing Audio…"}
        </span>
        <span className="progress-pct">{pct}%</span>
      </div>

      {/* Progress bar track */}
      <div className="progress-track">
        <div
          className={`progress-fill ${isError ? "progress-fill--error" : isDone ? "progress-fill--done" : ""}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Stage pills */}
      <div className="progress-stages">
        {STAGES.filter((s) => s.key !== "complete").map((stage) => {
          const isCompleted = completedStages.includes(stage.key);
          const isCurrent = progress.stage === stage.key;
          return (
            <div
              key={stage.key}
              className={`progress-stage ${isCompleted ? "progress-stage--done" : ""} ${isCurrent ? "progress-stage--active" : ""}`}
            >
              {isCompleted ? (
                <CheckCircle2 size={12} />
              ) : isCurrent ? (
                <Loader2 size={12} className="spinning" />
              ) : (
                <span className="progress-stage-dot" />
              )}
              <span>{stage.label}</span>
            </div>
          );
        })}
      </div>

      {isError && progress.error && (
        <div className="progress-error-msg">
          <AlertTriangle size={14} /> {progress.error}
        </div>
      )}

      {!isError && !isDone && (
        <p className="progress-hint">
          Currently: <strong>{getStageLabel(progress.stage)}</strong>
        </p>
      )}
    </div>
  );
}
