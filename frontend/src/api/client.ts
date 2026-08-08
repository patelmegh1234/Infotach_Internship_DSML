// Dimple, Upload Date: 2026-08-02
// Production API Client for AcousticSpace Frontend — with Task-based Submit
import type { AnalysisResponse, SubmitResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface DemoSample {
  id: string;
  name: string;
  description: string;
  target_class: string;
}

export interface ModelMetricsData {
  created_at_utc: string;
  dataset_rows: number;
  train_rows: number;
  test_rows: number;
  feature_count: number;
  best_model: string;
  holdout_accuracy: number;
  holdout_balanced_accuracy: number;
  holdout_f1_macro: number;
  voice_binary_accuracy: number;
  training_seconds: number;
  comparison: Record<string, { cv_accuracy_mean: number; cv_f1_macro_mean: number; cv_seconds: number }>;
  confusion_matrix: number[][];
  labels: string[];
}

export interface EdaSummaryData {
  total_files: number;
  duplicate_paths: number;
  class_counts: Record<string, number>;
  mix_profile_counts: Record<string, number>;
  unique_utterances: number;
  unique_backgrounds: number;
}

/** Synchronous analysis (kept for backward compatibility). */
export async function analyzeAudio(file: File): Promise<AnalysisResponse> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Analysis failed. Please try another audio file.");
  }

  return response.json();
}

/**
 * Submit audio for async task-based analysis.
 * Returns task_id — caller should connect to WS /ws/{task_id} for progress.
 */
export async function submitAnalysis(file: File): Promise<SubmitResponse> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/analyze/submit`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Submission failed. Please try another audio file.");
  }

  return response.json();
}

export async function getHealth(): Promise<{ status: string; model_type?: string; artifact_loaded?: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) return { status: "offline" };
    return await response.json();
  } catch {
    return { status: "offline" };
  }
}

export async function getModelMetrics(): Promise<ModelMetricsData | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/metrics`);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function getEdaSummary(): Promise<EdaSummaryData | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/eda-summary`);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function getDemoSamples(): Promise<DemoSample[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/demo-samples`);
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

export async function fetchDemoSampleFile(sampleId: string): Promise<File> {
  const response = await fetch(`${API_BASE_URL}/api/demo-samples/${sampleId}`);
  if (!response.ok) {
    throw new Error(`Failed to load demo sample '${sampleId}'.`);
  }
  const blob = await response.blob();
  return new File([blob], `${sampleId}.wav`, { type: "audio/wav" });
}
