import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2분으로 증가
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '요청 실패'
    return Promise.reject(new Error(message))
  }
)

// API functions
export const healthCheck = () => api.get('/health')

export const getKPIs = () => api.get('/market/kpis')

export const getTrends = () => api.get('/market/trends')

export const getNews = () => api.get('/market/news')

export const qaChat = (data: { question: string; context?: string }) =>
  api.post('/qa/chat', data)

export const qaSummary = (data: { question: string; context?: string }) =>
  api.post('/qa/summary', data)

export const generateProblems = (data: {
  level: string
  topic: string
  count: number
  style: string
}) => api.post('/problems', data, { timeout: 180000 }) // 3분

export const gradeAnswers = (data: {
  answers: Array<{ question_id: string; user_answer: string }>
}) => api.post('/problems/grade', data)

export const getRecommendations = (data: {
  topic: string
  level: string
  purpose: string
}) => api.post('/recommend', data)

export const createBookmark = (data: {
  title: string
  url: string
  tags: string[]
  note?: string
}) => api.post('/recommend/bookmark', data)

export const getBookmarks = () => api.get('/recommend/bookmarks')

// Quiz Attempt API functions
export const createQuizAttempt = (data: {
  problemset_id?: string
  items: Array<{ question_id: string; user_answer: string }>
  started_at: string
  finished_at: string
}) => api.post('/quiz/attempts', data)

export const getQuizAttempt = (attemptId: string) => 
  api.get(`/quiz/attempts/${attemptId}`)

export const getQuizAttempts = (page: number = 1, size: number = 10) =>
  api.get(`/quiz/attempts?page=${page}&size=${size}`)

export const exportQuizAttemptJson = (attemptId: string) =>
  api.get(`/quiz/attempts/${attemptId}/export.json`, {
    responseType: 'blob'
  })

export const exportQuizAttemptCsv = (attemptId: string) =>
  api.get(`/quiz/attempts/${attemptId}/export.csv`, {
    responseType: 'blob'
  })

// Retry Problems API functions
export const createRetryProblems = (data: {
  attempt_id: string
  model: string
  num_questions: number
}) => api.post('/quiz/retry', data, { timeout: 180000 }) // 3분

// Demo API functions
export const getDemoStatus = () => api.get('/demo/status')

export const resetDemoDatabase = () => api.post('/demo/reset')

export const seedDemoDatabase = () => api.post('/demo/seed')

