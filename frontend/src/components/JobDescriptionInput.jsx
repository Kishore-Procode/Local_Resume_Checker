import { useState } from 'react'
import { FileText, ChevronDown, ChevronUp, Info } from 'lucide-react'

const MIN_CHARS = 50
const RECOMMEND_CHARS = 200

export default function JobDescriptionInput({ value, onChange, isLoading }) {
  const [focused, setFocused] = useState(false)
  const [showTips, setShowTips] = useState(false)

  const charCount = value.length
  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0
  const isValid = charCount >= MIN_CHARS

  const getCounterColor = () => {
    if (charCount < MIN_CHARS) return 'text-rose-400'
    if (charCount < RECOMMEND_CHARS) return 'text-amber-400'
    return 'text-emerald-400'
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-brand-400" />
          <span className="text-sm font-medium text-slate-300">Job Description</span>
          {!isValid && charCount > 0 && (
            <span className="text-xs text-rose-400">(too short)</span>
          )}
        </div>
        <div className={`text-xs font-medium ${getCounterColor()}`}>
          {wordCount} words
        </div>
      </div>

      {/* Textarea */}
      <div className={`relative rounded-xl transition-all duration-200
        ${focused ? 'ring-2 ring-brand-500/50' : ''}`}>
        <textarea
          id="job-description-input"
          className="textarea-field min-h-[180px] text-sm leading-relaxed"
          placeholder="Paste the full job description here...

Include responsibilities, required skills, qualifications, and any other requirements. The more complete the description, the better the analysis."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={isLoading}
        />
      </div>

      {/* Character guide */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>{charCount} characters</span>
        {charCount > 0 && charCount < RECOMMEND_CHARS && (
          <span className="text-amber-400">
            Paste the full job description for best results
          </span>
        )}
      </div>

      {/* Tips collapsible */}
      <button
        onClick={() => setShowTips(!showTips)}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
        id="jd-tips-toggle"
      >
        <Info size={12} />
        Tips for better analysis
        {showTips ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {showTips && (
        <div className="p-4 bg-surface-700/50 rounded-xl border border-white/5 text-xs text-slate-400 space-y-2 animate-fade-in">
          <p className="font-semibold text-slate-300">For best results:</p>
          <ul className="space-y-1.5 list-none">
            {[
              'Paste the complete job posting, including all sections',
              'Include the "Required" and "Preferred" qualifications sections',
              'Include the list of responsibilities',
              'Include any mentioned tools, technologies, or frameworks',
              'Education and experience requirements improve accuracy',
            ].map((tip, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">→</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
