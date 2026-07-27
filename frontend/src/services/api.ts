import type { PredictionResult } from '../types/prediction';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

/**
 * Sends an audio file to the backend for deepfake detection analysis.
 *
 * @param file - The WAV audio file to analyze
 * @returns The prediction result from the backend
 * @throws If the API request fails or returns an invalid response
 */
export async function analyzeAudio(file: File): Promise<PredictionResult> {
  const formData = new FormData();
  formData.append('file', file);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000);

  try {
    const response = await fetch(`${BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let detail = `Server error (${response.status})`;
      try {
        const errorBody = await response.json();
        if (errorBody.detail) {
          detail = errorBody.detail;
        }
      } catch {
        // ignore parse error; use default message
      }
      throw new Error(detail);
    }

    const data: unknown = await response.json();

    if (!isValidPrediction(data)) {
      throw new Error('Invalid response format from server');
    }

    return data;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    if (err instanceof TypeError) {
      throw new Error('Unable to reach the server. Please ensure the backend is running.');
    }
    throw err;
  }
}

function isValidPrediction(data: unknown): data is PredictionResult {
  if (typeof data !== 'object' || data === null) {
    return false;
  }
  const d = data as Record<string, unknown>;
  return (
    typeof d.prediction === 'string' &&
    typeof d.confidence === 'number' &&
    typeof d.voice_type === 'string' &&
    typeof d.background_type === 'string'
  );
}

