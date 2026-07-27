import { useNavigate } from 'react-router-dom';
import { Waves, FileSearch, Shield, BarChart3, ArrowRight } from 'lucide-react';

const features = [
  {
    icon: Waves,
    title: 'Acoustic Analysis',
    desc: 'Examines Room Impulse Response (RIR) and reverberation characteristics to identify acoustic inconsistencies.',
  },
  {
    icon: FileSearch,
    title: 'Waveform Inspection',
    desc: 'Visualize audio waveforms and inspect spectral patterns with interactive playback controls.',
  },
  {
    icon: Shield,
    title: 'AI Detection',
    desc: 'Machine learning models trained on thousands of real and synthetic audio samples.',
  },
  {
    icon: BarChart3,
    title: 'Forensic Results',
    desc: 'Detailed forensic dashboard with confidence scores and per-component analysis.',
  },
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home">
      {/* Hero */}
      <section className="hero">
        <div className="container hero__inner">
          <div className="hero__badge">AI-Powered Audio Forensics</div>
          <h1 className="hero__title">
            <span className="hero__accent">AcousticSpace</span>
          </h1>
          <p className="hero__subtitle">Detect Deepfake Audio Through Acoustic Space</p>
          <p className="hero__desc">
            AcousticSpace investigates both voice characteristics and the surrounding acoustic
            environment — going beyond traditional vocal artifacts to detect AI-generated speech
            through Room Impulse Response (RIR) analysis, spectral fingerprinting, and acoustic
            forensics.
          </p>
          <button
            type="button"
            className="btn btn-primary hero__cta"
            onClick={() => navigate('/upload')}
          >
            Analyze Audio
            <ArrowRight size={20} />
          </button>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="container">
          <h2 className="features__heading">How AcousticSpace Works</h2>
          <div className="features__grid">
            {features.map((feature) => (
              <article key={feature.title} className="feature-card fade-in">
                <div className="feature-card__icon">
                  <feature.icon size={28} aria-hidden="true" />
                </div>
                <h3 className="feature-card__title">{feature.title}</h3>
                <p className="feature-card__desc">{feature.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

