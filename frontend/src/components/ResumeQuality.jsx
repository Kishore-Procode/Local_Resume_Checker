import { Star, TrendingUp, AlertCircle } from 'lucide-react'

const ScoreRing = ({ value, label, color }) => {
  const pct = Math.round(value * 100)
  const circumference = 2 * Math.PI * 20
  const dash = (pct / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-16 h-16">
        <svg viewBox="0 0 48 48" className="w-full h-full -rotate-90">
          <circle cx="24" cy="24" r="20" fill="none" stroke="#334155" strokeWidth="4" />
          <circle
            cx="24" cy="24" r="20" fill="none"
            stroke={color} strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference}`}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-slate-100">{pct}%</span>
        </div>
      </div>
      <span className="text-xs text-slate-400 text-center leading-tight">{label}</span>
    </div>
  )
}

const IssueCard = ({ issue }) => {
  const severityConfig = {
    high: { border: 'border-rose-500/20', bg: 'bg-rose-500/5', text: 'text-rose-400' },
    medium: { border: 'border-amber-500/20', bg: 'bg-amber-500/5', text: 'text-amber-400' },
    low: { border: 'border-slate-500/20', bg: 'bg-slate-500/5', text: 'text-slate-400' },
  }
  const config = severityConfig[issue.severity] || severityConfig.low

  return (
    <div className={`p-3.5 rounded-xl border ${config.bg} ${config.border} space-y-1.5`}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-slate-200 leading-relaxed">{issue.affected_text || issue.suggestion}</p>
        <span className={`text-xs font-medium flex-shrink-0 ${config.text} capitalize`}>
          {issue.severity}
        </span>
      </div>
      {issue.affected_text && issue.suggestion && issue.affected_text !== issue.suggestion && (
        <p className="text-xs text-slate-500 leading-relaxed">↳ {issue.suggestion}</p>
      )}
    </div>
  )
}

export default function ResumeQuality({ qualityMetrics }) {
  if (!qualityMetrics) return null

  const {
    action_verb_score, quantification_score, overall_quality_score,
    total_bullets, bullets_with_metrics, weak_phrase_count,
    first_person_count, repeated_phrases, quality_issues,
    average_bullet_length,
  } = qualityMetrics

  const overallPct = Math.round(overall_quality_score * 100)
  const overallColor = overallPct >= 70 ? '#22c55e' : overallPct >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div className="glass-card p-6 space-y-6 animate-slide-up">
      <h2 className="section-heading">
        <Star size={18} className="text-brand-400" />
        Resume Quality Analysis
      </h2>

      {/* Score rings */}
      <div className="grid grid-cols-3 gap-4">
        <ScoreRing
          value={overall_quality_score}
          label="Overall Quality"
          color={overallColor}
        />
        <ScoreRing
          value={action_verb_score}
          label="Action Verbs"
          color={action_verb_score >= 0.7 ? '#22c55e' : action_verb_score >= 0.5 ? '#f59e0b' : '#ef4444'}
        />
        <ScoreRing
          value={quantification_score}
          label="Quantified"
          color={quantification_score >= 0.4 ? '#22c55e' : quantification_score >= 0.25 ? '#f59e0b' : '#ef4444'}
        />
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total Bullets', value: total_bullets, good: total_bullets > 5 },
          { label: 'With Metrics', value: bullets_with_metrics, good: bullets_with_metrics > 0 },
          { label: 'Weak Phrases', value: weak_phrase_count, good: weak_phrase_count === 0, invert: true },
          { label: 'Avg. Length', value: `${average_bullet_length}w`, good: average_bullet_length >= 10 && average_bullet_length <= 25 },
        ].map(({ label, value, good, invert }) => (
          <div key={label} className="bg-surface-700/50 rounded-xl p-3 text-center">
            <p className={`text-lg font-bold ${good ? 'text-emerald-400' : 'text-amber-400'}`}>
              {value}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Repeated phrases */}
      {repeated_phrases?.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <AlertCircle size={14} className="text-amber-400" />
            <span className="text-sm font-medium text-slate-300">Repeated Phrases</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {repeated_phrases.map((phrase, i) => (
              <span key={i} className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300">
                "{phrase}"
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Issues */}
      {quality_issues?.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <TrendingUp size={14} className="text-brand-400" />
            <span className="text-sm font-medium text-slate-300">
              Improvement Opportunities ({quality_issues.length})
            </span>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {quality_issues.map((issue, i) => (
              <IssueCard key={i} issue={issue} />
            ))}
          </div>
        </div>
      )}

      {quality_issues?.length === 0 && (
        <div className="text-center py-4">
          <p className="text-emerald-400 font-medium">Strong resume quality!</p>
          <p className="text-slate-500 text-xs mt-1">No major quality issues detected.</p>
        </div>
      )}
    </div>
  )
}
