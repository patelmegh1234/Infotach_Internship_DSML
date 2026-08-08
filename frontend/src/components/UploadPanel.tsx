// Dimple, Upload Date: 2026-07-28
// Enhanced Upload & Demo Sample Selector Panel
import { useEffect, useState } from "react";
import { FileAudio, PlayCircle, UploadCloud, X, Sparkles, Music } from "lucide-react";
import { fetchDemoSampleFile, getDemoSamples, type DemoSample } from "../api/client";

type UploadPanelProps = {
  file: File | null;
  isAnalyzing: boolean;
  onAnalyze: () => void;
  onFileChange: (file: File | null) => void;
};

export function UploadPanel({ file, isAnalyzing, onAnalyze, onFileChange }: UploadPanelProps) {
  const [demos, setDemos] = useState<DemoSample[]>([]);
  const [loadingDemo, setLoadingDemo] = useState<string | null>(null);

  useEffect(() => {
    getDemoSamples().then(setDemos);
  }, []);

  async function handleSelectDemo(sample: DemoSample) {
    setLoadingDemo(sample.id);
    try {
      const demoFile = await fetchDemoSampleFile(sample.id);
      onFileChange(demoFile);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDemo(null);
    }
  }

  return (
    <section className="panel upload-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Audio Intake Scanner</p>
          <h2>Suspect File Upload</h2>
        </div>
        <FileAudio size={22} />
      </div>

      <label className="drop-zone">
        <UploadCloud size={32} />
        <span>{file ? file.name : "Click or drag audio file (.wav, .mp3, .flac)"}</span>
        <input
          type="file"
          accept="audio/*,.wav,.mp3,.flac,.ogg,.m4a"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
      </label>

      {file && (
        <div className="file-row">
          <span style={{ fontSize: "0.85rem", fontWeight: 700 }}>
            {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </span>
          <button className="icon-button" type="button" title="Remove file" onClick={() => onFileChange(null)}>
            <X size={18} />
          </button>
        </div>
      )}

      {/* Demo Audio Sample Selector */}
      {demos.length > 0 && (
        <div className="demo-picker">
          <p style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Sparkles size={14} style={{ color: "var(--accent-primary)" }} /> Instant Reviewer Demos
          </p>
          <div className="demo-buttons">
            {demos.map((d) => (
              <button
                key={d.id}
                type="button"
                className="demo-btn"
                disabled={isAnalyzing || loadingDemo === d.id}
                onClick={() => handleSelectDemo(d)}
              >
                <Music size={12} style={{ display: "inline", marginRight: "4px" }} />
                {loadingDemo === d.id ? "Loading..." : d.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <button className="primary-button" type="button" disabled={!file || isAnalyzing} onClick={onAnalyze}>
        <PlayCircle size={18} />
        <span>{isAnalyzing ? "Analyzing Acoustics..." : "Run Forensic Analysis"}</span>
      </button>
    </section>
  );
}
