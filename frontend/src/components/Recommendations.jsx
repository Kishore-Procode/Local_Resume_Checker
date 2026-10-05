import { Lightbulb, CheckCircle2, XCircle, ChevronRight } from 'lucide-react'

export default function Recommendations({ recommendations, strengths, weaknesses }) {
  if (!recommendations?.length && !strengths?.length && !weaknesses?.length) return null

  return (
    <div className="glass-card p-6 space-y-6 animate-slide-up">
      <h2 className="section-heading">
        <Lightbulb size={18} className="text-brand-400" />
        Analysis Summary & Recommendations
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        {strengths?.length > 0 && (
          <div className="space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-emerald-400">
              <CheckCircle2 size={15} />
              Strengths
            </h3>
            <ul className="space-y-2">
              {strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="text-emerald-400 mt-0.5 flex-shrink-0">✓</span>
                  <span className="text-sm text-slate-300 leading-relaxed">{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weaknesses */}
        {weaknesses?.length > 0 && (
          <div className="space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-rose-400">
              <XCircle size={15} />
              Gaps & Weaknesses
            </h3>
            <ul className="space-y-2">
              {weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="text-rose-400 mt-0.5 flex-shrink-0">✗</span>
                  <span className="text-sm text-slate-300 leading-relaxed">{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Divider */}
      {(strengths?.length > 0 || weaknesses?.length > 0) && recommendations?.length > 0 && (
        <div className="divider" />
      )}

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300">
            Actionable Recommendations
          </h3>
          <ol className="space-y-3">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3 group">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-brand-500/20 border border-brand-500/30
                                flex items-center justify-center mt-0.5">
                  <span className="text-xs font-bold text-brand-400">{i + 1}</span>
                </div>
                <div className="flex-1 flex items-start gap-2">
                  <p className="text-sm text-slate-300 leading-relaxed flex-1">{rec}</p>
                  <ChevronRight size={14} className="text-slate-600 mt-0.5 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Disclaimer */}
      <div className="p-3 bg-surface-700/30 rounded-xl border border-white/5">
        <p className="text-xs text-slate-500 leading-relaxed">
          <strong className="text-slate-400">Important:</strong> These suggestions are based on automated text analysis.
          Only add skills or experience to your resume that you genuinely possess.
          The ATS Compatibility Score is an estimate and does not represent the score of any specific ATS product.
        </p>
      </div>
    </div>
  )
}
