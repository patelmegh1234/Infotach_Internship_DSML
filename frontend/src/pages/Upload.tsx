import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import AudioUploader from '../components/AudioUploader';
import WaveformPlayer from '../components/WaveformPlayer';
import AnalysisLoader from '../components/AnalysisLoader';
import { useAnalysis } from '../context/AnalysisContext';
import { analyzeAudio } from '../services/api';

export default function Upload() {
  const navigate = useNavigate();
  const {
    audioFile,
    audioMetadata,
    status,
    error,
    setAudioFile,
    setAudioMetadata,
    setPrediction,
    setStatus,
    setError,
    reset,
  } = useAnalysis();

  const [duration, setDuration] = useState<number | null>(null);

  const handleFileSelected = useCallback(
    (file: File | null) => {
      if (!file) {
        reset();
        setDuration(null);
        return;
      }
      setAudioFile(file);
      setAudioMetadata({
        filename: file.name,
        size: file.size,
        type: file.type || 'audio/wav',
      });
      setPrediction(null);
      setStatus('idle');
      setError(null);
      setDuration(null);
    },
    [setAudioFile, setAudioMetadata, setPrediction, setStatus, setError, reset],
  );

  const handleDurationReady = useCallback((dur: number) => {
    setDuration(dur);
    setAudioMetadata(
      audioMetadata ? { ...audioMetadata, duration: dur } : null,
    );
  }, [setAudioMetadata, audioMetadata]);

  const handleAnalyze = useCallback(async () => {
    if (!audioFile) return;

    setStatus('analyzing');
    setError(null);

    try {
      const result = await analyzeAudio(audioFile);
      setPrediction(result);
      setStatus('complete');
      navigate('/results');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An unexpected error occurred.';
      setError(message);
      setStatus('error');
    }
  }, [audioFile, navigate, setPrediction, setStatus, setError]);

  const canAnalyze = audioFile !== null && status !== 'analyzing';

  return (
    <div className="upload-page">
      <div className="container">
        <h1 className="upload-page__title">Analyze Audio</h1>
        <p className="upload-page__subtitle">
          Upload a WAV audio file to analyze its acoustic characteristics and detect potential
          deepfake manipulation.
        </p>

        <AudioUploader onFileSelected={handleFileSelected} currentFile={audioFile} />

        {audioFile && status !== 'analyzing' && (
          <WaveformPlayer audioFile={audioFile} onDurationReady={handleDurationReady} />
        )}

        {status === 'analyzing' && <AnalysisLoader />}

        {audioFile && status !== 'analyzing' && (
          <div className="upload-page__actions fade-in">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={!canAnalyze}
            >
              <Shield size={20} />
              Analyze Audio
            </button>
          </div>
        )}

        {error && (
          <div className="upload-page__error fade-in" role="alert">
            <p className="upload-page__error-title">Analysis Failed</p>
            <p>{error}</p>
          </div>
        )}

        {audioMetadata && duration !== null && (
          <div className="upload-page__meta fade-in">
            <span>Duration: {duration.toFixed(2)}s</span>
            <span>Type: WAV</span>
          </div>
        )}
      </div>
    </div>
  );
}

