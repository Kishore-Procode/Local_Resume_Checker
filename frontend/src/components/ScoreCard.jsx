import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts'
import { Info, Cpu } from 'lucide-react'

const getScoreColor = (score) => {
  if (score >= 80) return '#22c55e'
  if (score >= 65) return '#6366f1'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
}

const getScoreLabel = (score) => {
  if (score >= 85) return 'Excellent Match'
  if (score >= 70) return 'Good Match'
  if (score >= 55) return 'Moderate Match'
  if (score >= 40) return 'Weak Match'
  return 'Poor Match'
}

const ComponentBar = ({ label, value, weight, tooltip }) => {
  const pct = Math.round(value * 100)
  const barColor = pct >= 80 ? '#22c55e' : pct >= 60 ? '#6366f1' : pct >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="space-y-1.5 group relative">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-300 font-medium">{label}</span>
          <span className="text-slate-600 text-[10px]">({Math.round(weight * 100)}%)</span>
        </div>
        <span className="font-semibold" style={{ color: barColor }}>{pct}%</span>
      </div>
      <div className="progress-bar h-1.5">
        <div
          className="progress-fill"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
    </div>
  )
}

export default function ScoreCard({ score, semanticModelAvailable }) {
  if (!score) return null

  const overall = Math.round(score.overall_score)
  const scoreColor = getScoreColor(overall)
  const scoreLabel = getScoreLabel(overall)

  const gaugeData = [{ value: overall, fill: scoreColor }]

  const components = [
    { label: 'Skills Match', value: score.skills_match, weight: 0.25 },
    { label: 'Keyword Match', value: score.keyword_match, weight: 0.20 },
    { label: 'Semantic Match', value: score.semantic_match, weight: 0.20 },
    { label: 'Experience', value: score.experience_match, weight: 0.10 },
    { label: 'ATS Safety', value: score.ats_parsing_safety, weight: 0.10 },
    { label: 'Education', value: score.education_match, weight: 0.05 },
    { label: 'Sections', value: score.section_completeness, weight: 0.05 },
    { label: 'Quality', value: score.resume_quality, weight: 0.05 },
  ]

  return (
    <div className="glass-card p-6 space-y-6 animate-slide-up">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100">ATS Compatibility Score</h2>
          <p className="text-xs text-slate-500 mt-1">Estimated compatibility — not an actual ATS score</p>
        </div>
        {!semanticModelAvailable && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg">
            <Cpu size={12} className="text-amber-400" />
            <span className="text-xs text-amber-400">No semantic model</span>
          </div>
        )}
      </div>

      {/* Score Gauge */}
      <div className="flex items-center gap-6">
        {/* Radial Chart */}
        <div className="relative w-36 h-36 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="50%"
              innerRadius="72%"
              outerRadius="90%"
              data={gaugeData}
              startAngle={220}
              endAngle={-40}
              barSize={14}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
              <RadialBar
                dataKey="value"
                cornerRadius={10}
                background={{ fill: '#334155' }}
                angleAxisId={0}
              />
            </RadialBarChart>
          </ResponsiveContainer>

          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-black" style={{ color: scoreColor }}>{overall}</span>
            <span className="text-[10px] text-slate-500 font-medium">/ 100</span>
          </div>
        </div>

        {/* Score details */}
        <div className="flex-1 space-y-2">
          <div>
            <span className="text-xl font-bold" style={{ color: scoreColor }}>
              {scoreLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {score.score_explanation}
          </p>
        </div>
      </div>

      {/* Divider */}
      <div className="divider" />

      {/* Component Breakdown */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Score Breakdown
        </h3>
        <div className="space-y-3">
          {components.map((c) => (
            <ComponentBar key={c.label} {...c} />
          ))}
        </div>
      </div>

      {/* Methodology note */}
      <div className="flex items-start gap-2 p-3 bg-surface-700/50 rounded-xl border border-white/5">
        <Info size={13} className="text-slate-500 mt-0.5 flex-shrink-0" />
        <p className="text-xs text-slate-500">
          Score is calculated using keyword matching, skill coverage, semantic similarity (local model),
          section completeness, and resume quality signals. Weights are configurable in{' '}
          <code className="text-slate-400">config.py</code>.
        </p>
      </div>
    </div>
  )
}
