// Dimple, Upload Date: 2026-08-02
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart2,
  Database,
  History,
  Moon,
  Radar,
  ShieldCheck,
  Sun,
  Radio,
  Sliders,
  Cpu,
} from "lucide-react";
import { submitAnalysis, getHealth } from "./api/client";
import { AnalyticsPanel } from "./components/AnalyticsPanel";
import { EdaPanel } from "./components/EdaPanel";
import { HistoryPanel } from "./components/HistoryPanel";
import { PdfExportButton } from "./components/PdfExportButton";
import { ProgressPanel } from "./components/ProgressPanel";
import { ResultsPanel } from "./components/ResultsPanel";
import { SpectrogramPanel } from "./components/SpectrogramPanel";
import { UploadPanel } from "./components/UploadPanel";
import { WaveformPanel } from "./components/WaveformPanel";
import { useAnalysisWebSocket } from "./hooks/useAnalysisWebSocket";
import type { AnalysisHistoryItem, AnalysisResponse } from "./types";

const HISTORY_KEY = "acousticspace-history";
const THEME_KEY = "acousticspace-theme";

export default function App() {
  const { state: wsState, connect: wsConnect, reset: wsReset } = useAnalysisWebSocket();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [status, setStatus] = useState("checking");
  const [modelType, setModelType] = useState<string>("baseline_fallback");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"scanner" | "analytics" | "eda" | "history">("scanner");

  // Theme Toggle State
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    return (localStorage.getItem(THEME_KEY) as "dark" | "light") || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  useEffect(() => {
    getHealth().then((res) => {
      setStatus(res.status);
      if (res.model_type) setModelType(res.model_type);
    });
    const stored = localStorage.getItem(HISTORY_KEY);
    if (stored) {
      setHistory(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const statusLabel = useMemo(() => {
    if (status === "ok") return `API Online (${modelType.replace(/_/g, " ")})`;
    if (status === "checking") return "Connecting to API";
    return "API Offline";
  }, [status, modelType]);

  function handleFileChange(file: File | null) {
    setSelectedFile(file);
    setResult(null);
    setError(null);

    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(file ? URL.createObjectURL(file) : null);
  }

  // When WebSocket analysis completes, update result
  useEffect(() => {
    if (wsState.isDone && wsState.result) {
      setResult(wsState.result);
      const item: AnalysisHistoryItem = {
        ...wsState.result,
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
      };
      setHistory((prev) => {
        const next = [item, ...prev].slice(0, 12);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
        return next;
      });
      setIsAnalyzing(false);
    }
    if (wsState.isDone && wsState.error) {
      setError(wsState.error);
      setIsAnalyzing(false);
    }
  }, [wsState.isDone, wsState.result, wsState.error]);

  async function handleAnalyze() {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setResult(null);
    setError(null);
    wsReset();

    try {
      const { task_id } = await submitAnalysis(selectedFile);
      wsConnect(task_id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected analysis error.");
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="app-shell">
      {/* Top Navbar */}
      <header className="topbar">
        <div className="brand-section">
          <div className="brand-icon">
            <Radio size={24} />
          </div>
          <div>
            <p className="eyebrow">Production Audio Forensics</p>
            <h1>AcousticSpace</h1>
          </div>
        </div>

        <div className="topbar-actions">
          <div className={`api-pill ${status === "ok" ? "online" : ""}`}>
            <Activity size={16} />
            <span>{statusLabel}</span>
          </div>

          <button
            className="theme-toggle-btn"
            type="button"
            title="Toggle Dark / Light Theme"
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
          >
            {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </header>

      {/* Signal Strip Banner */}
      <section className="signal-strip" aria-label="project indicators">
        <div className="signal-card">
          <ShieldCheck size={24} />
          <div className="signal-info">
            <span>Acoustic Validation</span>
            <strong>Room Impulse Decay</strong>
          </div>
        </div>
        <div className="signal-card">
          <Radar size={24} />
          <div className="signal-info">
            <span>Feature Dimension</span>
            <strong>118 Librosa Features</strong>
          </div>
        </div>
        <div className="signal-card">
          <Cpu size={24} />
          <div className="signal-info">
            <span>Dataset Scale</span>
            <strong>12,000 WAV Files</strong>
          </div>
        </div>
        <div className="signal-card">
          <History size={24} />
          <div className="signal-info">
            <span>Analyst History</span>
            <strong>{history.length} Saved Scans</strong>
          </div>
        </div>
      </section>

      {/* Tab Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === "scanner" ? "active" : ""}`}
          onClick={() => setActiveTab("scanner")}
        >
          <Sliders size={18} /> Forensic Scanner
        </button>
        <button
          className={`nav-tab ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          <BarChart2 size={18} /> Model Evaluation Metrics
        </button>
        <button
          className={`nav-tab ${activeTab === "eda" ? "active" : ""}`}
          onClick={() => setActiveTab("eda")}
        >
          <Database size={18} /> Dataset EDA & Insights
        </button>
        <button
          className={`nav-tab ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          <History size={18} /> Case History ({history.length})
        </button>
      </nav>

      {/* Main Tab Content */}
      {activeTab === "scanner" && (
        <section className="workspace-grid">
          <UploadPanel
            file={selectedFile}
            isAnalyzing={isAnalyzing}
            onAnalyze={handleAnalyze}
            onFileChange={handleFileChange}
          />
          <WaveformPanel audioUrl={audioUrl} fileName={selectedFile?.name} />

          {/* Real-time progress — show as soon as isAnalyzing starts, with or without WS data */}
          {isAnalyzing && (
            <div className="full-width">
              <ProgressPanel progress={wsState.progress} />
            </div>
          )}

          <div className="full-width">
            <ResultsPanel result={result} error={error} isAnalyzing={isAnalyzing} />
          </div>

          {/* Spectrogram heatmap — shown when result contains mel band data */}
          {result && Array.isArray(result.features?.mel_spectrogram_preview) && (result.features.mel_spectrogram_preview as number[]).length > 0 && (
            <div className="full-width">
              <SpectrogramPanel
                melBands={result.features.mel_spectrogram_preview as number[]}
                label={result.predicted_class?.replace(/_/g, " ")}
                decision={result.decision}
              />
            </div>
          )}

          {/* PDF export button */}
          {result && (
            <div className="full-width" style={{ display: "flex", justifyContent: "flex-end", padding: "0 0 8px" }}>
              <PdfExportButton result={result} />
            </div>
          )}
        </section>
      )}

      {activeTab === "analytics" && <AnalyticsPanel />}
      {activeTab === "eda" && <EdaPanel />}
      {activeTab === "history" && (
        <HistoryPanel
          history={history}
          onSelect={(item) => {
            setResult(item);
            setActiveTab("scanner");
          }}
        />
      )}
    </main>
  );
}
