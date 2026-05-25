import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Compare from './pages/Compare'
import FitAnalysis from './pages/FitAnalysis'
import Predictor from './pages/Predictor'

export default function App() {
  return (
    <div className="min-h-screen bg-navy-950">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/fit" element={<FitAnalysis />} />
          <Route path="/predict" element={<Predictor />} />
        </Routes>
      </main>
    </div>
  )
}
