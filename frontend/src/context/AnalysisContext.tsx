import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { AnalysisState, AnalysisStatus, AudioMetadata, PredictionResult } from '../types/prediction';

interface AnalysisContextValue extends AnalysisState {
  setAudioFile: (file: File | null) => void;
  setAudioMetadata: (meta: AudioMetadata | null) => void;
  setPrediction: (prediction: PredictionResult | null) => void;
  setStatus: (status: AnalysisStatus) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState: AnalysisState = {
  status: 'idle',
  audioFile: null,
  audioMetadata: null,
  prediction: null,
  error: null,
};

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AnalysisState>(initialState);

  const setAudioFile = useCallback((audioFile: File | null) => {
    setState((prev) => ({ ...prev, audioFile }));
  }, []);

  const setAudioMetadata = useCallback((audioMetadata: AudioMetadata | null) => {
    setState((prev) => ({ ...prev, audioMetadata }));
  }, []);

  const setPrediction = useCallback((prediction: PredictionResult | null) => {
    setState((prev) => ({ ...prev, prediction }));
  }, []);

  const setStatus = useCallback((status: AnalysisStatus) => {
    setState((prev) => ({ ...prev, status }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return (
    <AnalysisContext.Provider
      value={{
        ...state,
        setAudioFile,
        setAudioMetadata,
        setPrediction,
        setStatus,
        setError,
        reset,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis(): AnalysisContextValue {
  const ctx = useContext(AnalysisContext);
  if (!ctx) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return ctx;
}

