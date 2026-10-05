import { Shield, AlertTriangle, CheckCircle } from 'lucide-react'

const SEVERITY_CONFIG = {
  critical: { badge: 'badge-critical', icon: '🚨', label: 'Critical' },
  high: { badge: 'badge-high', icon: '⚠️', label: 'High' },
  medium: { badge: 'badge-medium', icon: '⚡', label: 'Medium' },
  low: { badge: 'badge-low', icon: 'ℹ️', label: 'Low' },
}

export default function ParsingAnalysis({ parsingIssues, atsSafetyScore, pageCount, wordCount }) {
  const safetyPct = Math.round((atsSafetyScore ?? 1) * 100)
  const safetyColor = safetyPct >= 85 ? '#22c55e' : safetyPct >= 70 ? '#f59e0b' : '#ef4444'

  const criticalCount = parsingIssues?.filter(i => i.severity === 'critical').length || 0
  const highCount = parsingIssues?.filter(i => i.severity === 'high').length || 0
  const hasIssues = parsingIssues?.length > 0

  return (
    <div className="glass-card p-6 space-y-5 animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="section-heading">
          <Shield size={18} className="text-brand-400" />
          ATS Parsing Analysis
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-black" style={{ color: safetyColor }}>{safetyPct}%</span>
          <span className="text-xs text-slate-500">safe</span>
        </div>
      </div>

      {/* Safety bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-500">
          <span>ATS Safety Score</span>
          <span style={{ color: safetyColor }}>
            {safetyPct >= 90 ? 'Excellent' : safetyPct >= 75 ? 'Good' : safetyPct >= 60 ? 'Fair' : 'Needs attention'}
          </span>
        </div>
        <div className="progress-bar h-2.5">
          <div
            className="progress-fill"
            style={{ width: `${safetyPct}%`, backgroundColor: safetyColor }}
          />
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Pages', value: pageCount ?? '—' },
          { label: 'Words', value: wordCount?.toLocaleString() ?? '—' },
          { label: 'Issues', value: parsingIssues?.length ?? 0,
            color: (parsingIssues?.length ?? 0) === 0 ? 'text-emerald-400' : 'text-amber-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-surface-700/50 rounded-xl p-3 text-center">
            <p className={`text-lg font-bold ${color || 'text-slate-100'}`}>{value}</p>
            <p className="text-xs text-slate-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* No issues */}
      {!hasIssues && (
        <div className="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
          <CheckCircle size={20} className="text-emerald-400 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-emerald-300">No ATS parsing issues detected</p>
            <p className="text-xs text-emerald-400/70 mt-0.5">
              Your resume uses a clean, ATS-friendly format.
            </p>
          </div>
        </div>
      )}

      {/* Issue list */}
      {hasIssues && (
        <div className="space-y-3">
          {(criticalCount + highCount > 0) && (
            <div className="flex items-center gap-2 text-rose-400 text-sm">
              <AlertTriangle size={14} />
              <span className="font-medium">
                {criticalCount + highCount} high-priority issue{criticalCount + highCount !== 1 ? 's' : ''} require attention
              </span>
            </div>
          )}
          {parsingIssues.map((issue, i) => {
            const config = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.low
            return (
              <div key={i} className="p-4 bg-surface-700/40 rounded-xl border border-white/5 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span>{config.icon}</span>
                    <span className="text-sm font-semibold text-slate-200 capitalize">
                      {issue.category?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span className={config.badge}>{config.label}</span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{issue.message}</p>
                {issue.recommendation && (
                  <div className="flex items-start gap-1.5">
                    <span className="text-brand-400 text-xs mt-0.5">→</span>
                    <p className="text-xs text-slate-400 leading-relaxed">{issue.recommendation}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
