import { useState } from 'react'
import { Zap, ArrowRight, Loader2, AlertTriangle, CheckCircle, FileText, Sparkles, Upload, ShieldCheck, Cpu } from 'lucide-react'
import toast from 'react-hot-toast'
import ResumeUploader from '../components/ResumeUploader.jsx'
import JobDescriptionInput from '../components/JobDescriptionInput.jsx'
import { analyzeResume, getErrorMessage } from '../services/api.js'

export default function Home({ onAnalysisComplete }) {
  const [uploadResult, setUploadResult] = useState(null)
  const [jdText, setJdText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [inputTab, setInputTab] = useState('upload') // 'upload' | 'jd'

  const canAnalyze = uploadResult && jdText.trim().length >= 50 && !isAnalyzing

  const handleUpload = (result) => {
    setUploadResult(result)
    setError('')
    if (result) {
      toast.success('Resume parsed successfully! Now add the job description.')
      setInputTab('jd')
    }
  }

  const handleAnalyze = async () => {
    if (!uploadResult) {
      setError('Please upload your resume first.')
      setInputTab('upload')
      return
    }
    if (jdText.trim().length < 50) {
      setError('Please paste a target job description (at least 50 characters).')
      setInputTab('jd')
      return
    }

    setIsAnalyzing(true)
    setError('')

    try {
      const result = await analyzeResume(uploadResult.resume_id, jdText)
      toast.success(`Analysis complete! ATS Score: ${Math.round(result.score.overall_score)}/100`)
      onAnalysisComplete(result)
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.error(msg)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const loadSampleJd = () => {
    setJdText(
      `Senior Full Stack Developer\n\nRequirements:\n- 4+ years experience with React.js, JavaScript (ES6+), HTML5, CSS3, Tailwind CSS\n- Strong proficiency in Python, FastAPI, REST APIs, and PostgreSQL / SQL databases\n- Hands-on experience with Git, Docker, CI/CD pipelines, and cloud services\n- Proven track record of optimizing web application performance and API latencies\n- Excellent problem-solving skills, team communication, and Agile project management.`
    )
    toast.success('Sample job description loaded!')
  }

  return (
    <div className="min-h-screen bg-[#070d19] text-slate-100 font-sans antialiased relative overflow-hidden flex flex-col justify-center py-10 lg:py-16 selection:bg-blue-500 selection:text-white">
      
      {/* ─── Dark Blue Background Glow Orbs ─────────────────────────────────── */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/15 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/3 right-10 w-[300px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        
        {/* ─── Hero Header & Quotes Section ───────────────────────────────────── */}
        <div className="text-center max-w-3xl mx-auto mb-10 lg:mb-14 space-y-4 animate-fade-in">
          
          {/* Privacy & Tech Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-2 bg-blue-950/70 border border-blue-500/30 rounded-full text-xs font-semibold text-blue-300 shadow-lg shadow-blue-950/50 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            <ShieldCheck size={14} className="text-blue-400" />
            100% Local AI Analysis — No Data Leaves Your Machine
          </div>

          {/* New Strong Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.12]">
            Optimize Your Resume for ATS &{' '}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
              Land 3x More Interviews
            </span>
          </h1>

          {/* New Strong Subheading Quote */}
          <p className="text-slate-400 text-base sm:text-lg leading-relaxed max-w-2xl mx-auto">
            Get instant keyword matching, hard skill gap detection, and ATS format scoring against any job description — processed privately using local AI.
          </p>
        </div>

        {/* ─── Main Content Grid: Dual Input Box + Laptop Preview ────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          
          {/* Left Column: Upload & Job Description Card */}
          <div className="lg:col-span-6 space-y-5">
            <div className="bg-[#0f172a]/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-blue-950/50 backdrop-blur-xl hover:border-slate-700/80 transition-all duration-300 space-y-6">
              
              {/* Step Navigation Tabs */}
              <div className="flex items-center p-1.5 bg-slate-900/90 border border-slate-800 rounded-2xl">
                <button
                  onClick={() => setInputTab('upload')}
                  className={`flex-1 py-2.5 px-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 ${
                    inputTab === 'upload'
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Upload size={16} />
                  1. Upload Resume
                  {uploadResult && <CheckCircle size={15} className="text-emerald-400" />}
                </button>

                <button
                  onClick={() => setInputTab('jd')}
                  className={`flex-1 py-2.5 px-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 ${
                    inputTab === 'jd'
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <FileText size={16} />
                  2. Job Description
                  {jdText.trim().length >= 50 && <CheckCircle size={15} className="text-emerald-400" />}
                </button>
              </div>

              {/* Tab 1: Resume Upload */}
              {inputTab === 'upload' && (
                <div className="animate-fade-in space-y-4">
                  <ResumeUploader
                    onUploaded={handleUpload}
                    isLoading={isAnalyzing}
                  />
                  {uploadResult && (
                    <div className="flex justify-end pt-1">
                      <button
                        onClick={() => setInputTab('jd')}
                        className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1.5 transition"
                      >
                        Next: Add Job Description <ArrowRight size={14} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Job Description Input */}
              {inputTab === 'jd' && (
                <div className="animate-fade-in space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <FileText size={14} className="text-blue-400" />
                      Target Job Description
                    </label>
                    <button
                      onClick={loadSampleJd}
                      type="button"
                      className="text-xs font-medium text-blue-400 hover:text-blue-300 hover:underline flex items-center gap-1 transition"
                    >
                      <Sparkles size={13} />
                      Paste Sample JD
                    </button>
                  </div>

                  <JobDescriptionInput
                    value={jdText}
                    onChange={setJdText}
                    isLoading={isAnalyzing}
                  />

                  <div className="flex justify-between items-center text-xs text-slate-400 pt-1">
                    <span>{jdText.trim().length} characters</span>
                    {jdText.trim().length < 50 ? (
                      <span className="text-amber-400">At least 50 characters required</span>
                    ) : (
                      <span className="text-emerald-400 font-medium flex items-center gap-1">
                        <CheckCircle size={13} /> Ready for match analysis
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Error Box */}
              {error && (
                <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-start gap-2.5 text-xs text-rose-300">
                  <AlertTriangle size={16} className="text-rose-400 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Analyze CTA Button */}
              <button
                onClick={handleAnalyze}
                disabled={!canAnalyze}
                id="main-analyze-btn"
                className={`w-full py-4 px-6 rounded-2xl font-bold text-white text-base transition-all duration-300 flex items-center justify-center gap-3 ${
                  canAnalyze
                    ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 shadow-xl shadow-blue-600/30 scale-[1.01] hover:scale-[1.02] active:scale-[0.99] cursor-pointer'
                    : 'bg-slate-800 text-slate-500 border border-slate-700/60 cursor-not-allowed shadow-none'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Running Local AI Match Engine...
                  </>
                ) : (
                  <>
                    <Zap size={20} className={canAnalyze ? 'fill-current text-yellow-300' : ''} />
                    Analyze Resume & Job Match
                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span className="flex items-center gap-1">
                  <Cpu size={12} className="text-blue-400" /> spaCy & Sentence Transformers
                </span>
                <span>Fast & 100% Private</span>
              </div>
            </div>
          </div>

          {/* Right Column: Dark Laptop Dashboard Preview */}
          <div className="lg:col-span-6 relative">
            
            {/* Glowing Accent Ring Behind Laptop */}
            <div className="absolute -inset-4 bg-gradient-to-r from-blue-600/20 via-indigo-600/20 to-cyan-500/20 rounded-3xl blur-2xl pointer-events-none" />

            {/* Laptop Frame Container */}
            <div className="relative mx-auto max-w-lg lg:max-w-none shadow-2xl rounded-2xl overflow-hidden border border-slate-800 bg-[#0f172a]">
              
              {/* Laptop Display Top Bar */}
              <div className="bg-[#090d16] px-4 py-3 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="text-[11px] text-slate-400 font-mono tracking-wider flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  LIVE ATS SCORE DASHBOARD
                </div>
                <div className="text-[10px] text-blue-400 font-semibold px-2 py-0.5 bg-blue-950 border border-blue-800 rounded">
                  LOCAL ENGINE
                </div>
              </div>

              {/* Mockup Dashboard Content */}
              <div className="p-5 sm:p-6 bg-[#0c1322] space-y-5 text-slate-100 font-sans">
                
                {/* Greeting & Quick Summary */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                  <div>
                    <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Candidate Report</span>
                    <h3 className="text-base font-bold text-white flex items-center gap-2 mt-0.5">
                      ATS Match Analysis <Sparkles size={16} className="text-amber-400" />
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      88 / 100 Overall
                    </span>
                  </div>
                </div>

                {/* Score Cards Grid */}
                <div className="grid grid-cols-4 gap-2.5">
                  {[
                    { label: 'Overall', val: '88', color: 'text-blue-400', border: 'border-blue-500/30' },
                    { label: 'Keyword', val: '85%', color: 'text-emerald-400', border: 'border-emerald-500/30' },
                    { label: 'Format', val: '92%', color: 'text-violet-400', border: 'border-violet-500/30' },
                    { label: 'Impact', val: '90%', color: 'text-amber-400', border: 'border-amber-500/30' },
                  ].map((m, i) => (
                    <div key={i} className={`bg-slate-900/90 p-3 rounded-xl border ${m.border} text-center space-y-1`}>
                      <p className={`text-base font-extrabold ${m.color}`}>{m.val}</p>
                      <p className="text-[10px] text-slate-400 font-medium uppercase tracking-tighter">{m.label}</p>
                    </div>
                  ))}
                </div>

                {/* Readiness Meter Gauge */}
                <div className="bg-slate-900/70 p-4 rounded-2xl border border-slate-800 space-y-2.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-300 font-semibold">Match Readiness Gauge</span>
                    <span className="text-emerald-400 font-bold">Strong Compatibility</span>
                  </div>

                  {/* Gradient Spectrum Bar */}
                  <div className="relative h-3 w-full rounded-full bg-gradient-to-r from-rose-500 via-amber-400 to-emerald-500 p-0.5 overflow-hidden">
                    <div
                      className="absolute top-0 bottom-0 w-2.5 bg-white rounded-full shadow-lg border border-slate-900"
                      style={{ left: '85%' }}
                    />
                  </div>

                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>Weak Match</span>
                    <span>Moderate</span>
                    <span className="text-emerald-400 font-semibold">Strong Match (85+)</span>
                  </div>
                </div>

                {/* Quick Insights List */}
                <div className="bg-slate-900/40 p-3.5 rounded-xl border border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center gap-2 text-slate-300">
                    <CheckCircle size={15} className="text-emerald-400 shrink-0" />
                    <span>Matched 14 core technical skills (React, Python, FastAPI)</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300">
                    <CheckCircle size={15} className="text-emerald-400 shrink-0" />
                    <span>0 critical ATS formatting issues detected</span>
                  </div>
                </div>

              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  )
}
