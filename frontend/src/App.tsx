import { Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';
import About from './pages/About';
import { AnalysisProvider } from './context/AnalysisContext';

export default function App() {
  return (
    <AnalysisProvider>
      <Navbar />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results" element={<Results />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </AnalysisProvider>
  );
}

