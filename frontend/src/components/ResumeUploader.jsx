import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertTriangle, X, File } from 'lucide-react'
import { uploadResume, getErrorMessage } from '../services/api.js'

const MAX_SIZE_MB = 10
const ACCEPTED = { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }

export default function ResumeUploader({ onUploaded, isLoading }) {
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [parseResult, setParseResult] = useState(null)

  const onDrop = useCallback((accepted, rejected) => {
    setError('')
    setParseResult(null)

    if (rejected.length > 0) {
      const r = rejected[0]
      if (r.errors[0]?.code === 'file-too-large') {
        setError(`File too large. Maximum size is ${MAX_SIZE_MB} MB.`)
      } else {
        setError('Invalid file type. Please upload a PDF or DOCX file.')
      }
      return
    }

    if (accepted.length > 0) {
      setFile(accepted[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    maxFiles: 1,
    disabled: isLoading,
  })

  const handleUpload = async () => {
    if (!file) return
    setError('')
    setUploadProgress(0)
    try {
      const result = await uploadResume(file, setUploadProgress)
      setParseResult(result)
      onUploaded(result)
    } catch (err) {
      setError(getErrorMessage(err))
      setUploadProgress(0)
    }
  }

  const handleRemove = () => {
    setFile(null)
    setParseResult(null)
    setError('')
    setUploadProgress(0)
    onUploaded(null)
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      {!parseResult && (
        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer
            transition-all duration-200 group
            ${isDragActive
              ? 'border-brand-400 bg-brand-500/10'
              : 'border-white/20 bg-surface-700/50 hover:border-brand-500/50 hover:bg-surface-700'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} id="resume-file-input" />

          <div className={`flex flex-col items-center gap-3 transition-all duration-200
            ${isDragActive ? 'scale-105' : 'group-hover:scale-102'}`}>
            <div className={`p-4 rounded-full transition-all duration-200
              ${isDragActive ? 'bg-brand-500/30' : 'bg-surface-600 group-hover:bg-brand-500/20'}`}>
              <Upload
                size={28}
                className={`transition-colors duration-200
                  ${isDragActive ? 'text-brand-300' : 'text-slate-400 group-hover:text-brand-400'}`}
              />
            </div>
            <div>
              <p className="text-slate-200 font-semibold text-base">
                {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
              </p>
              <p className="text-slate-400 text-sm mt-1">
                or <span className="text-brand-400 font-medium">browse files</span>
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <FileText size={12} /> PDF
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <FileText size={12} /> DOCX
              </span>
              <span>•</span>
              <span>Max {MAX_SIZE_MB} MB</span>
            </div>
          </div>
        </div>
      )}

      {/* Selected File (before upload) */}
      {file && !parseResult && (
        <div className="flex items-center gap-3 p-4 bg-surface-700 rounded-xl border border-white/10">
          <div className="p-2 bg-brand-500/20 rounded-lg">
            <File size={20} className="text-brand-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
            <p className="text-xs text-slate-400">{formatSize(file.size)}</p>
          </div>
          <button
            onClick={handleRemove}
            className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-500/10"
            disabled={isLoading}
            id="remove-resume-btn"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Upload Progress */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill bg-gradient-brand"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2.5 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl">
          <AlertTriangle size={16} className="text-rose-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-rose-300">{error}</p>
        </div>
      )}

      {/* Upload Button */}
      {file && !parseResult && (
        <button
          onClick={handleUpload}
          disabled={isLoading}
          className="btn-primary w-full justify-center"
          id="upload-resume-btn"
        >
          <Upload size={18} />
          {isLoading ? 'Uploading...' : 'Upload & Parse Resume'}
        </button>
      )}

      {/* Parse Success */}
      {parseResult && (
        <div className="space-y-3 animate-fade-in">
          <div className="flex items-start gap-3 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
            <CheckCircle size={18} className="text-emerald-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-emerald-300">Resume Parsed Successfully</p>
              <p className="text-xs text-emerald-400/70 mt-0.5 truncate">{parseResult.filename}</p>
            </div>
            <button
              onClick={handleRemove}
              className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
              id="change-resume-btn"
            >
              <X size={14} />
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Words', value: parseResult.word_count?.toLocaleString() },
              { label: 'Type', value: parseResult.file_type },
              { label: 'ATS Safety', value: `${Math.round(parseResult.ats_safety_score * 100)}%` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-surface-700 rounded-xl p-3 text-center">
                <p className="text-base font-bold text-slate-100">{value}</p>
                <p className="text-xs text-slate-500 mt-0.5">{label}</p>
              </div>
            ))}
          </div>

          {/* Parsing Issues */}
          {parseResult.parsing_issues?.length > 0 && (
            <div className="space-y-2">
              {parseResult.parsing_issues.slice(0, 2).map((issue, i) => (
                <div key={i} className={`flex items-start gap-2 p-3 rounded-xl text-xs
                  ${issue.severity === 'critical' || issue.severity === 'high'
                    ? 'bg-rose-500/10 border border-rose-500/20 text-rose-300'
                    : 'bg-amber-500/10 border border-amber-500/20 text-amber-300'}`}>
                  <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
                  <p>{issue.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Privacy note */}
      <p className="text-xs text-slate-500 text-center flex items-center justify-center gap-1.5">
        <span>🔒</span>
        Your resume is analyzed locally — never sent to external servers
      </p>
    </div>
  )
}
