// Shubhangi, Upload Date: 2026-07-28
// Enhanced Waveform Visualizer & Audio Playback Panel
import { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";
import { AudioLines } from "lucide-react";

type WaveformPanelProps = {
  audioUrl: string | null;
  fileName?: string;
};

export function WaveformPanel({ audioUrl, fileName }: WaveformPanelProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const waveSurferRef = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (!containerRef.current || !audioUrl) return;

    try {
      waveSurferRef.current?.destroy();
      waveSurferRef.current = WaveSurfer.create({
        container: containerRef.current,
        waveColor: "#0d9488",
        progressColor: "#2563eb",
        cursorColor: "#d97706",
        barWidth: 2,
        barGap: 2,
        barRadius: 2,
        height: 140,
        normalize: true,
      });
      waveSurferRef.current.load(audioUrl);
    } catch {
      // Fallback handled by audio element below
    }

    return () => {
      waveSurferRef.current?.destroy();
      waveSurferRef.current = null;
    };
  }, [audioUrl]);

  return (
    <section className="panel waveform-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Acoustic Signal Visualizer</p>
          <h2>{fileName ?? "No file loaded"}</h2>
        </div>
        <AudioLines size={22} />
      </div>

      <div className="waveform-frame">
        {audioUrl ? (
          <div ref={containerRef} />
        ) : (
          <div className="empty-waveform">Select or drag an audio file to render acoustic waveform</div>
        )}
      </div>

      {audioUrl && (
        <div className="audio-player-box">
          <audio controls src={audioUrl}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </section>
  );
}
