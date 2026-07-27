interface ConfidenceScoreProps {
  confidence: number;
}

export default function ConfidenceScore({ confidence }: ConfidenceScoreProps) {
  const percent = (confidence * 100).toFixed(0);
  const clamped = Math.min(Math.max(confidence, 0), 1);

  return (
    <div className="confidence fade-in">
      <div className="confidence__value">{percent}%</div>
      <div className="confidence__bar-track" role="progressbar" aria-valuenow={clamped * 100} aria-valuemin={0} aria-valuemax={100} aria-label={`Confidence: ${percent}%`}>
        <div
          className="confidence__bar-fill"
          style={{ width: `${clamped * 100}%` }}
        />
      </div>
      <div className="confidence__label">Confidence</div>
    </div>
  );
}

