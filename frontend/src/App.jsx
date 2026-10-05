import { useState, useEffect } from 'react'
import { Wifi, WifiOff } from 'lucide-react'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import { healthCheck } from './services/api.js'

function BackendStatus({ status }) {
  if (status === 'checking') return null
  if (status === 'ok') return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-2.5
                    bg-rose-500/10 border border-rose-500/30 rounded-xl text-sm text-rose-300
                    shadow-xl backdrop-blur-md animate-fade-in">
      <WifiOff size={16} />
      Backend not reachable. Is the FastAPI server running?
    </div>
  )
}

export default function App() {
  const [analysis, setAnalysis] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    healthCheck()
      .then(() => setBackendStatus('ok'))
      .catch(() => setBackendStatus('error'))
  }, [])

  const handleAnalysisComplete = (result) => {
    setAnalysis(result)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleReset = () => {
    setAnalysis(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <>
      {analysis
        ? <Dashboard analysis={analysis} onReset={handleReset} />
        : <Home onAnalysisComplete={handleAnalysisComplete} />
      }
      <BackendStatus status={backendStatus} />
    </>
  )
}
