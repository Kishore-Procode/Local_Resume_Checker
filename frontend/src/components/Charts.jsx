import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend
} from 'recharts'
import { BarChart2 } from 'lucide-react'

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6']

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-surface-800 border border-white/10 rounded-xl px-3 py-2 shadow-xl">
        <p className="text-xs font-medium text-slate-300">{label}</p>
        <p className="text-sm font-bold text-brand-400">{Math.round(payload[0].value)}%</p>
      </div>
    )
  }
  return null
}

const ScoreBreakdownChart = ({ score }) => {
  if (!score) return null

  const data = [
    { name: 'Skills', value: score.skills_match * 100 },
    { name: 'Keywords', value: score.keyword_match * 100 },
    { name: 'Semantic', value: score.semantic_match * 100 },
    { name: 'Experience', value: score.experience_match * 100 },
    { name: 'Education', value: score.education_match * 100 },
    { name: 'Sections', value: score.section_completeness * 100 },
    { name: 'ATS Safety', value: score.ats_parsing_safety * 100 },
    { name: 'Quality', value: score.resume_quality * 100 },
  ]

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Score Components
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
          <XAxis
            dataKey="name"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.1)' }} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={40}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.value >= 80 ? '#22c55e' : entry.value >= 60 ? '#6366f1' : entry.value >= 40 ? '#f59e0b' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

const SkillCategoryChart = ({ skillCategories }) => {
  if (!skillCategories?.length) return null

  const data = skillCategories
    .filter(c => c.count > 0)
    .slice(0, 8)
    .map((c, i) => ({
      category: c.category.length > 12 ? c.category.slice(0, 12) + '…' : c.category,
      count: c.count,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    }))

  if (!data.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Skills by Category
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, left: 70, bottom: 0 }}>
          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
          <YAxis
            type="category"
            dataKey="category"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.1)' }} />
          <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={18}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

const KeywordCoverageChart = ({ matchedRequirements }) => {
  if (!matchedRequirements?.length) return null

  // Group by category, compute match rate
  const categoryMap = {}
  matchedRequirements.forEach(r => {
    const cat = r.category || 'other'
    if (!categoryMap[cat]) categoryMap[cat] = { matched: 0, total: 0 }
    categoryMap[cat].total++
    if (r.match_type !== 'missing') categoryMap[cat].matched++
  })

  const data = Object.entries(categoryMap).map(([cat, { matched, total }]) => ({
    name: cat.charAt(0).toUpperCase() + cat.slice(1),
    coverage: Math.round((matched / total) * 100),
  }))

  if (data.length < 2) return null

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Coverage by Requirement Type
      </h3>
      <ResponsiveContainer width="100%" height={180}>
        <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
          <Radar
            name="Coverage"
            dataKey="coverage"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.25}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function Charts({ score, skillCategories, matchedRequirements }) {
  if (!score) return null

  return (
    <div className="glass-card p-6 space-y-8 animate-slide-up">
      <h2 className="section-heading">
        <BarChart2 size={18} className="text-brand-400" />
        Visual Analysis
      </h2>

      <ScoreBreakdownChart score={score} />

      <div className="divider" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SkillCategoryChart skillCategories={skillCategories} />
        <KeywordCoverageChart matchedRequirements={matchedRequirements} />
      </div>
    </div>
  )
}
