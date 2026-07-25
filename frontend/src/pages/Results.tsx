import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, Mic, Radio, FileAudio } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import ResultCard from '../components/ResultCard';
import ConfidenceScore from '../components/ConfidenceScore';

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function Results() {
  const navigate = useNavigate();
  const { prediction, audioMetadata, error, reset } = useAnalysis();

  // Redirect to upload if no prediction exists
  useEffect(() => {
    if (!prediction && !error) {
      // Allow a brief moment for context to propagate
      const timer = setTimeout(() => {
        navigate('/upload', { replace: true });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [prediction, error, navigate]);

  if (!prediction) {
    return (
      <div className="results-empty">
        <div className="container">
          <AlertTriangle size={48} className="results-empty__icon" />
          <h2>No Analysis Results</h2>
          <p>Upload and analyze an audio file to see results here.</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => navigate('/upload')}
          >
            <ArrowLeft size={20} />
            Go to Upload
          </button>
        </div>
      </div>
    );
  }

  const isFake = prediction.prediction.toLowerCase() === 'fake';
  const overallLabel = isFake ? 'FAKE AUDIO' : 'REAL AUDIO';
  const overallClass = isFake ? 'results__badge--fake' : 'results__badge--real';

  return (
    <div className="results-page">
      <div className="container">
        <h1 className="results-page__title">Analysis Result</h1>

        {/* Overall Classification */}
        <div className="results__overall fade-in">
          <span className={`results__badge ${overallClass}`}>{overallLabel}</span>
        </div>

        {/* Confidence */}
        <ResultCard title="Confidence Score">
          <ConfidenceScore confidence={prediction.confidence} />
        </ResultCard>

        {/* Analysis Details */}
        <div className="results__grid">
          <ResultCard title="Voice Analysis">
            <div className="results__detail">
              <Mic size={24} aria-hidden="true" />
              <div>
                <div className="results__detail-label">Voice Type</div>
                <div className="results__detail-value">{prediction.voice_type}</div>
              </div>
            </div>
          </ResultCard>

          <ResultCard title="Background Analysis">
            <div className="results__detail">
              <Radio size={24} aria-hidden="true" />
              <div>
                <div className="results__detail-label">Background Type</div>
                <div className="results__detail-value">{prediction.background_type}</div>
              </div>
            </div>
          </ResultCard>
        </div>

        {/* File Info */}
        {audioMetadata && (
          <ResultCard title="File Information">
            <div className="results__file-info">
              <FileAudio size={20} aria-hidden="true" />
              <div className="results__file-details">
                <span>
                  <strong>Filename:</strong> {audioMetadata.filename}
                </span>
                <span>
                  <strong>Size:</strong> {formatFileSize(audioMetadata.size)}
                </span>
                {audioMetadata.duration && (
                  <span>
                    <strong>Duration:</strong> {audioMetadata.duration.toFixed(2)}s
                  </span>
                )}
                <span>
                  <strong>Type:</strong> WAV
                </span>
              </div>
            </div>
          </ResultCard>
        )}

        {/* Action */}
        <div className="results__actions fade-in">
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => {
              reset();
              navigate('/upload');
            }}
          >
            <ArrowLeft size={20} />
            Analyze Another Audio
          </button>
        </div>
      </div>
    </div>
  );
}

