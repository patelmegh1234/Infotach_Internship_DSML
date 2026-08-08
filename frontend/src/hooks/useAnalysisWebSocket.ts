// Dimple, Upload Date: 2026-08-02
// WebSocket hook for real-time analysis progress streaming
import { useCallback, useRef, useState } from "react";
import type { AnalysisProgress, AnalysisResponse } from "../types";

const BASE_WS = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000")
  .replace(/^http/, "ws");

export type ProgressState = {
  taskId: string | null;
  progress: AnalysisProgress | null;
  isDone: boolean;
  result: AnalysisResponse | null;
  error: string | null;
};

export function useAnalysisWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const [state, setState] = useState<ProgressState>({
    taskId: null, progress: null, isDone: false, result: null, error: null,
  });

  const connect = useCallback((taskId: string) => {
    // Close any existing connection
    wsRef.current?.close();

    setState({ taskId, progress: null, isDone: false, result: null, error: null });

    const ws = new WebSocket(`${BASE_WS}/ws/${taskId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data: AnalysisProgress = JSON.parse(event.data);
        setState((prev) => ({
          ...prev,
          progress: data,
          isDone: data.status === "complete" || data.status === "error",
          result: data.result ?? prev.result,
          error: data.error ?? prev.error,
        }));
      } catch {
        // ignore parse errors
      }
    };

    ws.onerror = () => {
      setState((prev) => ({ ...prev, error: "WebSocket connection error.", isDone: true }));
    };

    ws.onclose = () => {
      // Connection closed — nothing to do
    };
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  const reset = useCallback(() => {
    disconnect();
    setState({ taskId: null, progress: null, isDone: false, result: null, error: null });
  }, [disconnect]);

  return { state, connect, disconnect, reset };
}
