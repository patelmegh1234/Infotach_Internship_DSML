export interface PredictionResult {
  prediction: string;
  confidence: number;
  voice_type: string;
  background_type: string;
}

export interface AudioMetadata {
  filename: string;
  size: number;
  type: string;
  duration?: number;
}

export type AnalysisStatus =
  | 'idle'
  | 'uploading'
  | 'analyzing'
  | 'complete'
  | 'error';

export interface AnalysisState {
  status: AnalysisStatus;
  audioFile: File | null;
  audioMetadata: AudioMetadata | null;
  prediction: PredictionResult | null;
  error: string | null;
}

