// Dimple, Upload Date: 2026-08-02
export type SuspiciousSegment = {
  start: number;
  end: number;
  score: number;
  reason: string;
};

export type ExplanationItem = {
  feature: string;
  value: number;
  importance?: number;       // legacy global importance
  contribution?: number;     // real SHAP per-prediction contribution
};

export type AnalysisResponse = {
  file_name: string;
  duration_seconds: number;
  decision: "suspicious" | "likely_real" | string;
  confidence: number;
  predicted_class?: string | null;
  voice_authenticity?: string | null;
  background_authenticity?: string | null;
  mismatch_detected: boolean;
  class_probabilities: Record<string, number>;
  risk_factors: string[];
  features: Record<string, number | number[]>;
  segments: SuspiciousSegment[];
  explanation: ExplanationItem[];
  model_metadata: Record<string, string | number>;
};

export type AnalysisHistoryItem = AnalysisResponse & {
  id: string;
  createdAt: string;
};

// WebSocket task progress types
export type AnalysisProgress = {
  stage: "queued" | "validating" | "extracting_features" | "classifying" | "generating_report" | "complete" | "error" | "heartbeat";
  progress: number;   // 0-100
  status: "pending" | "running" | "complete" | "error";
  result?: AnalysisResponse;
  error?: string;
};

export type SubmitResponse = {
  task_id: string;
  message: string;
};
