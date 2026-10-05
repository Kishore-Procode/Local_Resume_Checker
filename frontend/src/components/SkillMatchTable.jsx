import { useState } from 'react'
import { CheckCircle, XCircle, AlertCircle, Search, ChevronDown, ChevronUp } from 'lucide-react'

const MATCH_TYPE_CONFIG = {
  exact: { label: 'Exact', className: 'badge-exact' },
  normalized: { label: 'Alias', className: 'badge-exact' },
  fuzzy: { label: 'Fuzzy', className: 'badge-fuzzy' },
  semantic: { label: 'Semantic', className: 'badge-semantic' },
  weak: { label: 'Weak', className: 'badge-weak' },
  missing: { label: 'Missing', className: 'badge-missing' },
}

const CONFIDENCE_CONFIG = {
  high: 'text-emerald-400',
  medium: 'text-amber-400',
  low: 'text-orange-400',
  none: 'text-slate-600',
}

const FILTERS = ['all', 'matched', 'missing', 'weak']

const ExpandableEvidence = ({ text }) => {
  const [expanded, setExpanded] = useState(false)
  if (!text) return <span className="text-slate-600">—</span>

  const isLong = text.length > 100
  const display = expanded || !isLong ? text : text.slice(0, 100) + '…'

  return (
    <div className="space-y-1">
      <p className="text-xs text-slate-400 leading-relaxed italic">"{display}"</p>
      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] text-brand-400 hover:text-brand-300 flex items-center gap-0.5"
        >
          {expanded ? <><ChevronUp size={10} /> Less</> : <><ChevronDown size={10} /> More</>}
        </button>
      )}
    </div>
  )
}

export default function SkillMatchTable({ matchedRequirements }) {
  const [activeFilter, setActiveFilter] = useState('all')
  const [search, setSearch] = useState('')

  if (!matchedRequirements?.length) return null

  // Filter logic
  const filtered = matchedRequirements.filter((r) => {
    const matchFilter =
      activeFilter === 'all' ||
      (activeFilter === 'matched' && !['missing', 'weak'].includes(r.match_type)) ||
      (activeFilter === 'missing' && r.match_type === 'missing') ||
      (activeFilter === 'weak' && r.match_type === 'weak')

    const searchFilter = !search ||
      r.requirement.toLowerCase().includes(search.toLowerCase()) ||
      (r.evidence_text || '').toLowerCase().includes(search.toLowerCase())

    return matchFilter && searchFilter
  })

  const counts = {
    all: matchedRequirements.length,
    matched: matchedRequirements.filter(r => !['missing', 'weak'].includes(r.match_type)).length,
    missing: matchedRequirements.filter(r => r.match_type === 'missing').length,
    weak: matchedRequirements.filter(r => r.match_type === 'weak').length,
  }

  return (
    <div className="glass-card p-6 space-y-4 animate-slide-up">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="section-heading">
          <CheckCircle size={18} className="text-brand-400" />
          Requirements Match Table
        </h2>

        {/* Search */}
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search requirements..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-8 py-2 text-sm w-full sm:w-48"
            id="match-table-search"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 flex-wrap">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            className={activeFilter === f ? 'tab-btn-active' : 'tab-btn'}
            id={`filter-${f}-btn`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            <span className={`ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold
              ${activeFilter === f ? 'bg-white/20' : 'bg-surface-600'}`}>
              {counts[f]}
            </span>
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-2.5 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider w-8">
              </th>
              <th className="text-left py-2.5 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Requirement
              </th>
              <th className="text-left py-2.5 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider hidden sm:table-cell">
                Resume Evidence
              </th>
              <th className="text-left py-2.5 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Match
              </th>
              <th className="text-left py-2.5 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider hidden md:table-cell">
                Confidence
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filtered.map((req, i) => {
              const mc = MATCH_TYPE_CONFIG[req.match_type] || MATCH_TYPE_CONFIG.missing
              const isMissing = req.match_type === 'missing'
              const isWeak = req.match_type === 'weak'

              return (
                <tr
                  key={i}
                  className={`transition-colors hover:bg-surface-700/30
                    ${isMissing ? 'opacity-70' : ''}`}
                >
                  {/* Status icon */}
                  <td className="py-3 px-2">
                    {isMissing
                      ? <XCircle size={16} className="text-rose-400" />
                      : isWeak
                        ? <AlertCircle size={16} className="text-amber-400" />
                        : <CheckCircle size={16} className="text-emerald-400" />
                    }
                  </td>

                  {/* Requirement */}
                  <td className="py-3 px-2">
                    <div className="space-y-0.5">
                      <p className="font-medium text-slate-200">{req.requirement}</p>
                      <span className={`text-[10px] ${
                        req.importance === 'critical' ? 'text-rose-400' :
                        req.importance === 'high' ? 'text-orange-400' :
                        req.importance === 'medium' ? 'text-amber-400' : 'text-slate-500'
                      }`}>
                        {req.importance}
                      </span>
                    </div>
                  </td>

                  {/* Evidence */}
                  <td className="py-3 px-2 max-w-xs hidden sm:table-cell">
                    <ExpandableEvidence text={req.evidence_snippet || req.evidence_text} />
                  </td>

                  {/* Match type */}
                  <td className="py-3 px-2">
                    <span className={mc.className}>{mc.label}</span>
                  </td>

                  {/* Confidence */}
                  <td className="py-3 px-2 hidden md:table-cell">
                    <span className={`text-xs font-medium ${CONFIDENCE_CONFIG[req.confidence] || 'text-slate-600'}`}>
                      {req.confidence === 'none' ? '—' : req.confidence}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div className="text-center py-8 text-slate-500 text-sm">
            No requirements match the current filter.
          </div>
        )}
      </div>

      <p className="text-xs text-slate-600">
        Showing {filtered.length} of {matchedRequirements.length} requirements
      </p>
    </div>
  )
}
