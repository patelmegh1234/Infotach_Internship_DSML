import {
  Upload,
  GitBranch,
  BarChart3,
  Cpu,
  Radio,
  LayoutDashboard,
  Waves,
} from 'lucide-react';

const workflowSteps = [
  { icon: Upload, label: 'Audio Upload', desc: 'User uploads a WAV audio sample for analysis.' },
  { icon: GitBranch, label: 'Preprocessing', desc: 'Resampling, normalization, silence trimming, and segmentation.' },
  { icon: BarChart3, label: 'Feature Extraction', desc: 'MFCCs, spectral centroids, rolloff, zero-crossing rate, RIR features extracted via Librosa.' },
  { icon: Cpu, label: 'ML Model', desc: 'Trained Random Forest classifier on 12,000+ labeled samples across four categories.' },
  { icon: Radio, label: 'Prediction', desc: 'Model returns overall classification, confidence, voice type, and background type.' },
  { icon: LayoutDashboard, label: 'Forensic Dashboard', desc: 'Results presented with confidence scores and per-component analysis.' },
];

const technologies = [
  { category: 'Backend / ML', items: ['Python', 'FastAPI', 'Librosa', 'PyTorch', 'Scikit-learn', 'Joblib'] },
  { category: 'Frontend', items: ['React', 'TypeScript', 'Vite', 'WaveSurfer.js', 'Lucide React'] },
  { category: 'Data', items: ['WAV Audio', 'Metadata CSV', 'NumPy', 'Pandas'] },
];

export default function About() {
  return (
    <div className="about-page">
      <div className="container">
        <h1 className="about-page__title">About AcousticSpace</h1>
        <p className="about-page__subtitle">
          AcousticSpace is a deepfake audio detection system that analyzes both voice
          characteristics and the surrounding acoustic environment. Instead of relying only on
          traditional vocal artifacts, it investigates Room Impulse Response (RIR), reverberation
          patterns, spectral consistency, and background acoustic signatures to identify
          AI-generated speech.
        </p>

        {/* Workflow */}
        <section className="about-section">
          <h2 className="about-section__title">Analysis Workflow</h2>
          <div className="workflow">
            {workflowSteps.map((step, idx) => (
              <div key={step.label} className="workflow__step fade-in">
                <div className="workflow__step-icon">
                  <step.icon size={24} aria-hidden="true" />
                </div>
                <div className="workflow__step-content">
                  <div className="workflow__step-number">Step {idx + 1}</div>
                  <h3 className="workflow__step-label">{step.label}</h3>
                  <p className="workflow__step-desc">{step.desc}</p>
                </div>
                {idx < workflowSteps.length - 1 && (
                  <div className="workflow__connector" aria-hidden="true" />
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Technologies */}
        <section className="about-section">
          <h2 className="about-section__title">Technologies</h2>
          <div className="tech-grid">
            {technologies.map((group) => (
              <div key={group.category} className="tech-card fade-in">
                <h3 className="tech-card__title">{group.category}</h3>
                <ul className="tech-card__list">
                  {group.items.map((tech) => (
                    <li key={tech} className="tech-card__item">
                      <Waves size={14} aria-hidden="true" />
                      {tech}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Data */}
        <section className="about-section">
          <h2 className="about-section__title">Dataset</h2>
          <p className="about-page__text">
            The model is trained on approximately 12,000 two-second, 16 kHz WAV files organized
            across four balanced categories:
          </p>
          <ul className="about-list">
            <li>
              <code>fake_voice_fake_bg</code> — AI-generated voice with synthetic background
            </li>
            <li>
              <code>fake_voice_real_bg</code> — AI-generated voice with real background
            </li>
            <li>
              <code>real_voice_fake_bg</code> — Real voice with synthetic background
            </li>
            <li>
              <code>real_voice_real_bg</code> — Real voice with real background
            </li>
          </ul>
          <p className="about-page__text">
            This four-way classification enables the system to separately evaluate voice and
            acoustic-environment authenticity.
          </p>
        </section>
      </div>
    </div>
  );
}

