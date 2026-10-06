import { useState, useMemo } from 'react'
import {
  Sparkles,
  Copy,
  Check,
  ExternalLink,
  Wand2,
  FileText,
  Sliders,
  Bot,
  Zap,
  CheckCircle2,
  ArrowRight,
  MessageSquareText,
  ShieldAlert,
  Flame
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function PromptSection({ analysis }) {
  const [activeTemplate, setActiveTemplate] = useState('master')
  const [copied, setCopied] = useState(false)
  const [targetScore, setTargetScore] = useState(95)
  const [includeFullJd, setIncludeFullJd] = useState(false)
  const [customNotes, setCustomNotes] = useState('')
  const [selectedTone, setSelectedTone] = useState('Impact-Driven & Metrics Focused')

  if (!analysis) return null

  const {
    score = {},
    missing_skills = [],
    weak_matches = [],
    quality_metrics = {},
    recommendations = [],
    strengths = [],
    weaknesses = [],
    job_analysis = {},
  } = analysis

  // Extract key terms & text for prompt generation
  const overallScore = Math.round(score.overall_score || 0)
  const missingSkillsList = missing_skills.map((m) => m.skill).join(', ')
  const requiredSkillsList = (job_analysis.required_skills || []).slice(0, 15).join(', ')
  const topKeywordsList = Object.keys(job_analysis.keywords || {}).slice(0, 12).join(', ')
  const weaknessesList = weaknesses.map((w) => `- ${w}`).join('\n')
  const strengthsList = strengths.map((s) => `- ${s}`).join('\n')
  const recsList = recommendations.map((r) => `- ${r}`).join('\n')

  const weakPhrasesCount = quality_metrics.weak_phrase_count || 0
  const actionVerbScore = Math.round((quality_metrics.action_verb_score || 0) * 100)
  const metricScore = Math.round((quality_metrics.quantification_score || 0) * 100)

  // Dynamically compute the prompts
  const generatedPrompt = useMemo(() => {
    let prompt = ''

    if (activeTemplate === 'master') {
      prompt = `Act as an elite ATS Resume Strategist and Senior Hiring Specialist. 
I need you to completely rewrite and optimize my resume to guarantee a target ATS score of ${targetScore}+ / 100 for the job description provided below.

==================================================
1. CURRENT ATS RESUME DIAGNOSTIC AUDIT
==================================================
- Current Match Score: ${overallScore}/100
- Keyword Alignment Score: ${Math.round((score.keyword_match || 0) * 100)}%
- Hard Skills Match Score: ${Math.round((score.skills_match || 0) * 100)}%
- Action Verbs Score: ${actionVerbScore}%
- Quantified Metrics Score: ${metricScore}%

CRITICAL MISSING SKILLS TO INTEGRATE:
${missingSkillsList ? missing_skills.map(s => `• ${s.skill} (${s.importance} priority, category: ${s.category})`).join('\n') : 'None specifically missing'}

GAPS & WEAKNESSES DETECTED BY ATS PARSER:
${weaknessesList || '• Enhance quantification and section alignment'}

ACTIONABLE RESUME RECOMMENDATIONS:
${recsList || '• Add bullet points with measurable ROI metrics.'}

==================================================
2. TARGET JOB REQUIREMENTS & TOP ATS KEYWORDS
==================================================
- Core Required Technical Skills: ${requiredSkillsList || 'See Job Description'}
- High-Frequency ATS Keywords: ${topKeywordsList || 'See Job Description'}
${selectedTone ? `- Desired Professional Tone: ${selectedTone}` : ''}
${customNotes.trim() ? `- Additional User Instructions: ${customNotes.trim()}` : ''}

==================================================
3. REWRITE & ATS OPTIMIZATION INSTRUCTIONS
==================================================
Please rewrite my resume section by section (Professional Summary, Core Competencies / Technical Skills, Professional Experience, Projects, Education) following these rules:

1. REWRITE EXPERIENCE BULLET POINTS:
   - Start every single bullet point with a high-impact, active verb (e.g. Engineered, Spearheaded, Optimized, Orchestrated, Accelerated).
   - Apply the Google XYZ Formula: "Accomplished [X] as measured by [Y], by doing [Z]".
   - Naturally embed the missing skills (${missingSkillsList || 'key technical skills'}) into relevant work experience context without keyword stuffing.
   - Include realistic metrics (e.g., %, $, time saved, latency reduction, user growth) for achievements.

2. ATS FORMAT & PARSING SAFETY:
   - Use clean, standard ATS section headings.
   - Avoid tables, graphics, progress bars, or unusual symbols.
   - Ensure clean date ranges (e.g., Month 20XX – Present).

3. PROFESSIONAL SUMMARY:
   - Write a high-converting 3-4 line Executive Summary tailored specifically to this role incorporating top keywords.

4. OUTPUT FORMAT:
   - Output the complete fully rewritten resume in clean Markdown format ready to copy into Word/Google Docs.
   - At the bottom, list the Top 5 Strategic ATS Improvements you made.

==================================================
MY CURRENT RESUME TEXT:
==================================================
[PASTE YOUR COMPLETE RESUME TEXT HERE]
`
    } else if (activeTemplate === 'missing_skills') {
      prompt = `Act as an expert Technical Resume Writer. My resume is currently missing key skills required by an ATS for my target role.

==================================================
MISSING ATS SKILLS & GAPS TO ADD:
==================================================
${missing_skills.map((m, i) => `${i + 1}. Skill: "${m.skill}" (${m.importance.toUpperCase()} importance)\n   Suggestion: ${m.suggestion}`).join('\n\n') || 'Add technical skills matched to JD'}

WEAK OR PARTIAL MATCHES:
${weak_matches.map(w => `• ${w.requirement}: ${w.recommendation}`).join('\n') || 'Strengthen technical evidence'}

==================================================
INSTRUCTIONS FOR CLAUDE:
==================================================
1. Generate 2-3 high-impact, realistic bullet points for EACH missing skill above that I can seamlessly insert into my Work Experience or Projects section.
2. Ensure every bullet point includes realistic quantitative metrics (e.g. reduced latency by 35%, increased adoption by 40%).
3. Format each bullet starting with a strong action verb.
${customNotes.trim() ? `4. Custom Note: ${customNotes.trim()}` : ''}

Target Job Context / Top Keywords: ${topKeywordsList}

Here is my current resume text to contextualize these additions:
[PASTE YOUR RESUME TEXT HERE]`
    } else if (activeTemplate === 'impact_metrics') {
      prompt = `Act as a Resume Coach specializing in quantitative impact optimization. My resume was flagged by ATS for having weak bullet points and low quantified metrics.

==================================================
CURRENT METRICS AUDIT:
==================================================
- Action Verb Score: ${actionVerbScore}% (Needs strong verbs)
- Quantified Bullet Score: ${metricScore}% (Needs numeric impact)
- Weak Phrase Count: ${weakPhrasesCount}

DETECTED WEAKNESSES:
${weaknessesList}

==================================================
INSTRUCTIONS FOR CLAUDE:
==================================================
1. Take my bullet points and transform them using the Google XYZ Formula: "Accomplished [X] as measured by [Y], by doing [Z]".
2. Replace weak action verbs (like "helped", "worked on", "responsible for") with power verbs (like "Spearheaded", "Architected", "Accelerated").
3. Add realistic bracketed placeholders for metrics where exact numbers are missing (e.g. [reduced processing time by 45%], [managed budget of $X00K]).
4. Provide a Before vs After comparison for the top 5 weakest bullet points.

Here is my work experience section:
[PASTE YOUR EXPERIENCE SECTION HERE]`
    } else if (activeTemplate === 'summary_headline') {
      prompt = `Act as a Senior Executive Recruiter. Write high-converting ATS Professional Summaries and Resume Headlines for my application.

==================================================
TARGET KEYWORDS & SKILLS TO FEATURE:
==================================================
- Primary Keywords: ${topKeywordsList}
- Required Technical Skills: ${requiredSkillsList}

MY RESUME STRENGTHS TO HIGHLIGHT:
${strengthsList}

==================================================
INSTRUCTIONS FOR CLAUDE:
==================================================
1. Write 3 distinct versions of a 3-4 sentence Professional Summary tailored for ATS parsing:
   - Version A: Impact & Technical Leadership Focus
   - Version B: Metrics & Problem-Solving Focus
   - Version C: Concise & Modern Executive Focus
2. Write 5 punchy, keyword-packed Resume Title Headlines (e.g. "Senior Full Stack Engineer | React & Python Specialist | Cloud Architecture").
${customNotes.trim() ? `3. Note: ${customNotes.trim()}` : ''}`
    }

    if (includeFullJd && job_analysis.responsibilities) {
      prompt += `\n\n==================================================\nTARGET JOB DESCRIPTION REFERENCE:\n==================================================\n${job_analysis.responsibilities.join('\n')}`
    }

    return prompt
  }, [
    activeTemplate,
    targetScore,
    selectedTone,
    customNotes,
    includeFullJd,
    overallScore,
    score,
    missing_skills,
    missingSkillsList,
    weaknessesList,
    recsList,
    requiredSkillsList,
    topKeywordsList,
    actionVerbScore,
    metricScore,
    weakPhrasesCount,
    weak_matches,
    strengthsList,
    job_analysis
  ])

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedPrompt)
      setCopied(true)
      toast.success('Claude prompt copied to clipboard! Paste it directly into Claude.ai', {
        duration: 4000,
        icon: '📋',
      })
      setTimeout(() => setCopied(false), 3000)
    } catch (err) {
      toast.error('Failed to copy. Please select and copy manually.')
    }
  }

  const handleOpenClaude = async () => {
    await handleCopy()
    window.open('https://claude.ai/new', '_blank', 'noopener,noreferrer')
  }

  const handleOpenChatGPT = async () => {
    await handleCopy()
    window.open('https://chatgpt.com', '_blank', 'noopener,noreferrer')
  }

  return (
    <div className="space-y-6 animate-slide-up">
      {/* ─── Hero Card ────────────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-purple-950/80 border border-indigo-500/30 p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
        <div className="absolute -right-10 -top-10 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-10 -bottom-10 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs font-semibold text-purple-300">
              <Sparkles size={14} className="text-purple-400 animate-pulse" />
              Tailored AI Resume Prompts
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <ShieldAlert size={14} className="text-amber-400" />
              Includes real ATS analysis gaps & keywords
            </div>
          </div>

          <div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
              Copy-Paste Prompts for Claude & LLMs
              <Flame size={24} className="text-amber-400" />
            </h2>
            <p className="text-slate-300 text-sm sm:text-base mt-2 max-w-3xl leading-relaxed">
              Feed these hyper-specific prompts into Claude (or ChatGPT) to automatically resolve your detected missing skills, weak bullet points, and ATS formatting issues to reach a <strong className="text-emerald-400">95+ ATS score</strong>.
            </p>
          </div>

          {/* Quick Action Bar */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={handleOpenClaude}
              className="px-5 py-3 rounded-2xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 hover:from-purple-500 hover:to-indigo-500 text-white text-sm font-bold shadow-lg shadow-purple-600/30 transition-all duration-200 flex items-center gap-2 cursor-pointer active:scale-95"
              id="open-claude-btn"
            >
              <Bot size={18} />
              Copy & Open in Claude.ai
              <ExternalLink size={15} />
            </button>

            <button
              onClick={handleCopy}
              className="px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-semibold transition-all duration-200 flex items-center gap-2 cursor-pointer active:scale-95"
              id="copy-prompt-btn"
            >
              {copied ? (
                <>
                  <Check size={18} className="text-emerald-400" />
                  Copied to Clipboard!
                </>
              ) : (
                <>
                  <Copy size={18} className="text-indigo-400" />
                  Copy Prompt Text
                </>
              )}
            </button>

            <button
              onClick={handleOpenChatGPT}
              className="px-4 py-3 rounded-2xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium transition-all duration-200 flex items-center gap-2 cursor-pointer"
            >
              <MessageSquareText size={15} className="text-emerald-400" />
              Open in ChatGPT
              <ExternalLink size={13} />
            </button>
          </div>
        </div>
      </div>

      {/* ─── Template Selector Tabs ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          {
            id: 'master',
            title: '🚀 Complete ATS Overhaul',
            desc: 'Full resume rewrite prompt targeting 95+ score',
            color: 'from-purple-500/20 to-indigo-500/20 border-purple-500/40 text-purple-300',
          },
          {
            id: 'missing_skills',
            title: '🎯 Missing Skills Injector',
            desc: 'Generate bullet points incorporating missing tools',
            color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300',
          },
          {
            id: 'impact_metrics',
            title: '📈 Action & Metric Booster',
            desc: 'Fix weak action verbs with Google XYZ formula',
            color: 'from-amber-500/20 to-orange-500/20 border-amber-500/40 text-amber-300',
          },
          {
            id: 'summary_headline',
            title: '📝 Professional Summary Generator',
            desc: 'Craft high-converting executive summary & title',
            color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/40 text-cyan-300',
          },
        ].map((tpl) => {
          const isActive = activeTemplate === tpl.id
          return (
            <button
              key={tpl.id}
              onClick={() => setActiveTemplate(tpl.id)}
              className={`p-4 rounded-2xl border text-left transition-all duration-200 flex flex-col justify-between space-y-2 cursor-pointer ${
                isActive
                  ? `bg-gradient-to-br ${tpl.color} shadow-lg ring-2 ring-purple-500/50 scale-[1.02]`
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
              }`}
              id={`template-btn-${tpl.id}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-100">{tpl.title}</span>
                {isActive && <CheckCircle2 size={16} className="text-purple-400" />}
              </div>
              <p className="text-xs leading-relaxed text-slate-400">{tpl.desc}</p>
            </button>
          )
        })}
      </div>

      {/* ─── Prompt Options & Controls Bar ───────────────────────────────────── */}
      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Sliders size={16} className="text-indigo-400" />
            Customize Prompt Parameters
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {generatedPrompt.length} chars | {generatedPrompt.split('\n').length} lines
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Target Score Selection */}
          <div className="space-y-1.5">
            <label className="text-slate-400 font-medium flex items-center justify-between">
              <span>Target ATS Score</span>
              <span className="text-purple-400 font-bold">{targetScore}/100</span>
            </label>
            <select
              value={targetScore}
              onChange={(e) => setTargetScore(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500"
            >
              <option value={90}>90+ ATS Score (Standard Optimization)</option>
              <option value={95}>95+ ATS Score (Recommended)</option>
              <option value={98}>98+ ATS Score (Aggressive High-Match)</option>
            </select>
          </div>

          {/* Tone Selector */}
          <div className="space-y-1.5">
            <label className="text-slate-400 font-medium">Desired Writing Tone</label>
            <select
              value={selectedTone}
              onChange={(e) => setSelectedTone(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500"
            >
              <option value="Impact-Driven & Metrics Focused">Impact-Driven & Metrics Focused</option>
              <option value="Senior Leadership & Strategic">Senior Leadership & Strategic</option>
              <option value="Technical Specialist & Deep Engineering">Technical Specialist & Deep Engineering</option>
              <option value="Concise & Direct">Concise & Direct</option>
            </select>
          </div>

          {/* Include Full JD Checkbox */}
          <div className="flex items-center pt-5">
            <label className="flex items-center gap-2 text-slate-300 font-medium cursor-pointer">
              <input
                type="checkbox"
                checked={includeFullJd}
                onChange={(e) => setIncludeFullJd(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 text-purple-600 focus:ring-purple-500 bg-slate-900"
              />
              <span>Append Job Description Excerpt</span>
            </label>
          </div>
        </div>

        {/* Custom Instructions */}
        <div className="space-y-1.5 pt-1">
          <label className="text-slate-400 text-xs font-medium flex items-center gap-1.5">
            <Wand2 size={13} className="text-purple-400" />
            Additional Custom Instructions for Claude (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. Keep resume strictly under 2 pages, emphasize React & Node.js, highlight remote project management..."
            value={customNotes}
            onChange={(e) => setCustomNotes(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 transition"
          />
        </div>
      </div>

      {/* ─── Code / Text Display Window ───────────────────────────────────────── */}
      <div className="rounded-2xl border border-slate-800 bg-[#090d16] overflow-hidden shadow-2xl">
        {/* Header Bar */}
        <div className="bg-[#0f172a] px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="ml-2 text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <FileText size={13} className="text-indigo-400" />
              claude_ats_prompt.txt
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition flex items-center gap-1.5 cursor-pointer"
            >
              {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              {copied ? 'Copied!' : 'Copy Code'}
            </button>
          </div>
        </div>

        {/* Text Area Content */}
        <div className="p-4 sm:p-6 font-mono text-xs sm:text-sm text-slate-300 leading-relaxed overflow-x-auto max-h-[450px] overflow-y-auto whitespace-pre-wrap selection:bg-purple-600 selection:text-white">
          {generatedPrompt}
        </div>

        {/* Footer info */}
        <div className="bg-[#0b101d] px-4 py-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <Zap size={12} className="text-yellow-400" /> Ready to paste into Claude, ChatGPT, or Gemini
          </span>
          <button
            onClick={handleOpenClaude}
            className="text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1 transition hover:underline cursor-pointer"
          >
            Launch Claude.ai <ArrowRight size={12} />
          </button>
        </div>
      </div>

      {/* ─── How to Use Steps Card ────────────────────────────────────────────── */}
      <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Bot size={15} className="text-purple-400" />
          How to get 100% accurate results from Claude:
        </h4>
        <ol className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-400">
          <li className="p-3 bg-slate-900 rounded-xl border border-slate-800/80 space-y-1">
            <span className="font-bold text-purple-400">Step 1:</span> Copy the prompt text above using the button.
          </li>
          <li className="p-3 bg-slate-900 rounded-xl border border-slate-800/80 space-y-1">
            <span className="font-bold text-purple-400">Step 2:</span> Open Claude (or ChatGPT) and paste the prompt. Replace <code className="text-slate-200">[PASTE YOUR RESUME TEXT HERE]</code> with your actual resume text.
          </li>
          <li className="p-3 bg-slate-900 rounded-xl border border-slate-800/80 space-y-1">
            <span className="font-bold text-purple-400">Step 3:</span> Copy Claude's generated output back into Word/Google Docs or save as PDF!
          </li>
        </ol>
      </div>
    </div>
  )
}
