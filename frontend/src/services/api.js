import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for analysis
})

// ─── Resume Upload ────────────────────────────────────────────────────────────
export const uploadResume = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
  return response.data
}

// ─── Analyze ──────────────────────────────────────────────────────────────────
export const analyzeResume = async (resumeId, jdText) => {
  const response = await api.post('/analyze', {
    resume_id: resumeId,
    jd_text: jdText,
  })
  return response.data
}

// ─── Job Description Analysis ─────────────────────────────────────────────────
export const analyzeJobDescription = async (jdText) => {
  const response = await api.post('/job/analyze', { jd_text: jdText })
  return response.data
}

// ─── Health Check ─────────────────────────────────────────────────────────────
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// ─── Delete Resume ────────────────────────────────────────────────────────────
export const deleteResume = async (resumeId) => {
  const response = await api.delete(`/resume/${resumeId}`)
  return response.data
}

// ─── Error helper ─────────────────────────────────────────────────────────────
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) return error.response.data.detail
  if (error.message) return error.message
  return 'An unexpected error occurred.'
}
