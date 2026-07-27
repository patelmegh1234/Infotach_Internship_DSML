import { Loader2, Waves } from 'lucide-react';

export default function AnalysisLoader() {
  return (
    <div className="loader fade-in">
      <div className="loader__icon">
        <Waves size={40} className="loader__waves" aria-hidden="true" />
        <Loader2 size={32} className="loader__spinner" aria-hidden="true" />
      </div>
      <h2 className="loader__title">Analyzing Audio...</h2>
      <p className="loader__text">
        Inspecting acoustic characteristics
        <br />
        and running deepfake detection.
      </p>
    </div>
  );
}

