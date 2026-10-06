import { useState } from 'react'
import { ArrowLeft, Clock, Cpu, CheckCircle, Tag } from 'lucide-react'
import ScoreCard from '../components/ScoreCard.jsx'
import SkillMatchTable from '../components/SkillMatchTable.jsx'
import MissingSkills from '../components/MissingSkills.jsx'
import ResumeQuality from '../components/ResumeQuality.jsx'
import ParsingAnalysis from '../components/ParsingAnalysis.jsx'
import Recommendations from '../components/Recommendations.jsx'
import Charts from '../components/Charts.jsx'
import PromptSection from '../components/PromptSection.jsx'

const SECTIONS_CONFIG = {
  contact: 'Contact',
  summary: 'Summary',
  skills: 'Skills',
  experience: 'Experience',
  education: 'Education',
  projects: 'Projects',
  certifications: 'Certifications',
  achievements: 'Achievements',
  publications: 'Publications',
  languages: 'Languages',
  volunteer: 'Volunteer',
}

const SectionStatusGrid = ({ sections }) => (
  <div className="glass-card p-6 animate-slide-up">
    <h2 className="section-heading mb-4">
      <Tag size={18} className="text-brand-400" />
      Detected Resume Sections
    </h2>
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
      {sections?.map((sec) => (
        <div
          key={sec.name}
          className={`flex items-center gap-2 p-3 rounded-xl border text-sm
            ${sec.detected
              ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-300'
              : 'bg-surface-700/30 border-white/5 text-slate-600'
            }`}
        >
          <span>{sec.detected ? '✓' : '○'}</span>
          <span className="font-medium capitalize">{SECTIONS_CONFIG[sec.name] || sec.name}</span>
        </div>
      ))}
    </div>
  </div>
)

const SkillChip = ({ skill }) => (
  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand-500/10 border border-brand-500/20 rounded-xl text-xs text-brand-300 font-medium">
    {skill.name}
    {skill.frequency > 1 && (
      <span className="text-brand-500 text-[10px]">×{skill.frequency}</span>
    )}
  </span>
)

const SkillsSummary = ({ skills }) => (
  <div className="glass-card p-6 animate-slide-up">
    <h2 className="section-heading mb-4">
      <CheckCircle size={18} className="text-brand-400" />
      Skills Detected in Resume ({skills?.length || 0})
    </h2>
    <div className="flex flex-wrap gap-2">
      {skills?.slice(0, 40).map((skill, i) => (
        <SkillChip key={i} skill={skill} />
      ))}
      {skills?.length > 40 && (
        <span className="px-3 py-1.5 text-xs text-slate-500">
          +{skills.length - 40} more
        </span>
      )}
      {!skills?.length && (
        <p className="text-sm text-slate-500">No known skills detected.</p>
      )}
    </div>
  </div>
)

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'prompts', label: 'Claude Prompts ✨' },
  { id: 'matching', label: 'Requirements' },
  { id: 'missing', label: 'Missing Skills' },
  { id: 'quality', label: 'Quality' },
  { id: 'parsing', label: 'ATS Safety' },
  { id: 'charts', label: 'Charts' },
]

export default function Dashboard({ analysis, onReset }) {
  const [activeTab, setActiveTab] = useState('overview')

  if (!analysis) return null

  const {
    score, contact_info, sections, resume_skills, skill_categories,
    job_analysis, matched_requirements, missing_skills, weak_matches,
    quality_metrics, parsing_issues, recommendations, strengths, weaknesses,
    semantic_model_available, processing_time_ms,
  } = analysis

  return (
    <div className="min-h-screen bg-surface-900">
      {/* Top bar */}
      <div className="sticky top-0 z-40 bg-surface-900/90 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <button
            onClick={onReset}
            className="btn-secondary text-sm"
            id="back-to-home-btn"
          >
            <ArrowLeft size={16} />
            New Analysis
          </button>

          {/* Score badge */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-black text-gradient">
                {Math.round(score.overall_score)}
              </span>
              <span className="text-sm text-slate-500">/100</span>
            </div>
            <span className="hidden sm:block text-sm text-slate-400">ATS Score</span>
          </div>

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-slate-500">
            {!semantic_model_available && (
              <div className="flex items-center gap-1 text-amber-400">
                <Cpu size={12} />
                <span>No semantic model</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Clock size={12} />
              <span>{(processing_time_ms / 1000).toFixed(1)}s</span>
            </div>
          </div>
        </div>

        {/* Tab navigation */}
        <div className="max-w-7xl mx-auto px-4 pb-2 flex gap-1 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={activeTab === tab.id ? 'tab-btn-active flex-shrink-0' : 'tab-btn flex-shrink-0'}
              id={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left column */}
            <div className="lg:col-span-1 space-y-6">
              <ScoreCard score={score} semanticModelAvailable={semantic_model_available} />
              <ParsingAnalysis
                parsingIssues={parsing_issues}
                atsSafetyScore={score.ats_parsing_safety}
                pageCount={null}
                wordCount={null}
              />
            </div>

            {/* Right column */}
            <div className="lg:col-span-2 space-y-6">
              <Recommendations
                recommendations={recommendations}
                strengths={strengths}
                weaknesses={weaknesses}
                onGoToPrompts={() => setActiveTab('prompts')}
              />
              <SectionStatusGrid sections={sections} />
              <SkillsSummary skills={resume_skills} />
            </div>
          </div>
        )}

        {/* Claude Prompts Tab */}
        {activeTab === 'prompts' && (
          <PromptSection analysis={analysis} />
        )}

        {/* Matching Tab */}
        {activeTab === 'matching' && (
          <SkillMatchTable matchedRequirements={matched_requirements} />
        )}

        {/* Missing Tab */}
        {activeTab === 'missing' && (
          <MissingSkills missingSkills={missing_skills} weakMatches={weak_matches} />
        )}

        {/* Quality Tab */}
        {activeTab === 'quality' && (
          <ResumeQuality qualityMetrics={quality_metrics} />
        )}

        {/* Parsing Tab */}
        {activeTab === 'parsing' && (
          <ParsingAnalysis
            parsingIssues={parsing_issues}
            atsSafetyScore={score.ats_parsing_safety}
            pageCount={null}
            wordCount={null}
          />
        )}

        {/* Charts Tab */}
        {activeTab === 'charts' && (
          <Charts
            score={score}
            skillCategories={skill_categories}
            matchedRequirements={matched_requirements}
          />
        )}
      </div>
    </div>
  )
}
