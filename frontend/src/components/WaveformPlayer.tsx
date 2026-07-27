import { useRef, useEffect, useState, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';
import TimelinePlugin from 'wavesurfer.js/dist/plugins/timeline';
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';

interface WaveformPlayerProps {
  audioFile: File;
  onDurationReady?: (duration: number) => void;
}

export default function WaveformPlayer({ audioFile, onDurationReady }: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [zoom, setZoom] = useState(0);
  const [url, setUrl] = useState<string | null>(null);

  // Create object URL from file
  useEffect(() => {
    const objectUrl = URL.createObjectURL(audioFile);
    setUrl(objectUrl);
    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [audioFile]);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current || !url) return;

    // Destroy previous instance
    if (wavesurferRef.current) {
      wavesurferRef.current.destroy();
      wavesurferRef.current = null;
    }

    const ws = WaveSurfer.create({
      container: containerRef.current,
      url,
      waveColor: '#64748b',
      progressColor: '#22d3ee',
      barWidth: 2,
      barRadius: 2,
      barGap: 2,
      height: 120,
      normalize: true,
      backend: 'WebAudio',
      minPxPerSec: 1,
      fillParent: true,
      autoScroll: true,
      autoCenter: true,
      plugins: [
        TimelinePlugin.create({
          container: '#timeline',
          insertPosition: 'afterbegin',
          timeInterval: 0.5,
          primaryLabelInterval: 1,
          secondaryLabelInterval: 0.5,
        }),
      ],
    });

    wavesurferRef.current = ws;

    ws.on('ready', () => {
      const dur = ws.getDuration();
      setDuration(dur);
      onDurationReady?.(dur);
    });

    ws.on('timeupdate', (time: number) => {
      setCurrentTime(time);
    });

    ws.on('play', () => setIsPlaying(true));
    ws.on('pause', () => setIsPlaying(false));
    ws.on('finish', () => setIsPlaying(false));

    return () => {
      ws.destroy();
      wavesurferRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  const handlePlayPause = useCallback(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  }, []);

  const handleRestart = useCallback(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.setTime(0);
      setCurrentTime(0);
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    setZoom((prev) => {
      const next = Math.min(prev + 10, 100);
      wavesurferRef.current?.zoom(next);
      return next;
    });
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((prev) => {
      const next = Math.max(prev - 10, 0);
      wavesurferRef.current?.zoom(next);
      return next;
    });
  }, []);

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  return (
    <div className="waveform fade-in">
      <div className="waveform__header">
        <span className="waveform__filename">{audioFile.name}</span>
      </div>

      <div className="waveform__visual" ref={containerRef} />

      <div id="timeline" className="waveform__timeline" />

      <div className="waveform__time">
        <span>{formatTime(currentTime)}</span>
        <span>/</span>
        <span>{formatTime(duration)}</span>
      </div>

      <div className="waveform__controls">
        <button
          type="button"
          className="waveform__btn"
          onClick={handlePlayPause}
          aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
        >
          {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          <span>{isPlaying ? 'Pause' : 'Play'}</span>
        </button>

        <button
          type="button"
          className="waveform__btn waveform__btn--icon"
          onClick={handleRestart}
          aria-label="Restart playback"
        >
          <RotateCcw size={18} />
          <span>Restart</span>
        </button>

        <div className="waveform__zoom">
          <button
            type="button"
            className="waveform__btn waveform__btn--icon"
            onClick={handleZoomOut}
            disabled={zoom <= 0}
            aria-label="Zoom out"
          >
            <ZoomOut size={18} />
          </button>

          <input
            type="range"
            className="waveform__slider"
            min={0}
            max={100}
            step={1}
            value={zoom}
            onChange={(e) => {
              const val = Number(e.target.value);
              setZoom(val);
              wavesurferRef.current?.zoom(val);
            }}
            aria-label="Zoom level"
          />

          <button
            type="button"
            className="waveform__btn waveform__btn--icon"
            onClick={handleZoomIn}
            disabled={zoom >= 100}
            aria-label="Zoom in"
          >
            <ZoomIn size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

