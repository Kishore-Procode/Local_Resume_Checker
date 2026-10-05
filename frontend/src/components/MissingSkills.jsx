import { AlertTriangle, Info } from 'lucide-react'

const IMPORTANCE_CONFIG = {
  critical: { color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20', dot: 'bg-rose-400' },
  high: { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20', dot: 'bg-orange-400' },
  medium: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', dot: 'bg-amber-400' },
  low: { color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20', dot: 'bg-slate-400' },
}

const CATEGORY_COLORS = {
  'Programming Languages': 'text-blue-400',
  'Frontend': 'text-cyan-400',
  'Backend': 'text-violet-400',
  'Databases': 'text-emerald-400',
  'Cloud': 'text-sky-400',
  'DevOps': 'text-orange-400',
  'AI/ML': 'text-pink-400',
  'Tools': 'text-slate-400',
}

export default function MissingSkills({ missingSkills, weakMatches }) {
  const hasMissing = missingSkills?.length > 0
  const hasWeak = weakMatches?.length > 0

  if (!hasMissing && !hasWeak) {
    return (
      <div className="glass-card p-6 animate-slide-up">
        <div className="text-center py-4">
          <div className="text-4xl mb-3">🎯</div>
          <p className="text-emerald-400 font-semibold">All requirements matched!</p>
          <p className="text-slate-500 text-sm mt-1">No missing or weak skills detected.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-6 space-y-6 animate-slide-up">
      <h2 className="section-heading">
        <AlertTriangle size={18} className="text-amber-400" />
        Missing & Weak Requirements
      </h2>

      {/* Missing Skills */}
      {hasMissing && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Not Found in Resume ({missingSkills.length})
          </h3>
          <div className="space-y-3">
            {missingSkills.map((skill, i) => {
              const config = IMPORTANCE_CONFIG[skill.importance] || IMPORTANCE_CONFIG.low
              const catColor = CATEGORY_COLORS[skill.category] || 'text-slate-400'

              return (
                <div key={i} className={`p-4 rounded-xl border ${config.bg} space-y-2`}>
                  {/* Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-0.5 ${config.dot}`} />
                      <span className="font-semibold text-slate-100">{skill.skill}</span>
                      <span className={`text-xs ${catColor}`}>{skill.category}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className={`text-xs font-medium ${config.color} capitalize`}>
                        {skill.importance}
                      </span>
                      {skill.jd_frequency > 1 && (
                        <span className="text-xs text-slate-500">
                          ×{skill.jd_frequency} in JD
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Related evidence */}
                  {skill.related_evidence && (
                    <div className="flex items-start gap-2 text-xs text-slate-400">
                      <Info size={11} className="mt-0.5 flex-shrink-0 text-slate-500" />
                      <span>Related: <span className="text-slate-300 italic">"{skill.related_evidence}"</span></span>
                    </div>
                  )}

                  {/* Suggestion */}
                  <p className="text-xs text-slate-400 leading-relaxed pl-4">
                    {skill.suggestion}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Weak Matches */}
      {hasWeak && (
        <div className="space-y-3">
          <div className="divider" />
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Weakly Represented ({weakMatches.length})
          </h3>
          <p className="text-xs text-slate-500">
            These requirements have related content in your resume, but the exact terminology isn't present.
          </p>
          <div className="space-y-3">
            {weakMatches.map((match, i) => (
              <div key={i} className="p-4 rounded-xl border bg-amber-500/5 border-amber-500/15 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-amber-400 flex-shrink-0" />
                  <span className="font-semibold text-slate-100">{match.requirement}</span>
                  <span className="badge-weak">Weak</span>
                </div>
                <p className="text-xs text-slate-400 italic pl-4">
                  Resume: "{match.resume_evidence.slice(0, 120)}"
                </p>
                <p className="text-xs text-slate-400 pl-4">{match.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
