export interface KPIData {
  cpi: number
  cpi_change: number
  gdp_qoq: number
  gdp_yoy: number
  unemployment: number
  unemployment_change: number
  base_rate: number
  base_rate_change: number
  usdkrw: number
  usdkrw_change: number
  spx: number
  spx_change: number
  kospi: number
  kospi_change: number
  updated_at: string
}

export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface TrendsData {
  cpi_series: TimeSeriesPoint[]
  unemployment_series: TimeSeriesPoint[]
  rate_series: TimeSeriesPoint[]
  gdp_series: TimeSeriesPoint[]
}

export interface NewsItem {
  title: string
  summary: string
  url: string
  source: string
  published_at: string
}

export interface ProblemItem {
  id?: string
  question: string
  options?: string[]
  answer: string
  explanation: string
  topic?: 'macro' | 'finance' | 'trade' | 'stats'
  level?: 'basic' | 'intermediate' | 'advanced'
}

export interface AnswerItem {
  question_id: string
  user_answer: string
}

export interface GradeRequest {
  answers: AnswerItem[]
}

export interface GradeResult {
  question_id: string
  is_correct: boolean
  correct_answer: string
}

export interface GradeResponse {
  total: number
  correct: number
  score: number
  results: GradeResult[]
}

export interface RecommendItem {
  title: string
  summary: string
  url: string
  tags: string[]
}

// Quiz Attempt Types
export interface QuizAttemptItem {
  question_id: string
  user_answer: string
  correct_answer: string
  is_correct: boolean
}

export interface QuizAttemptIn {
  problemset_id?: string
  items: AnswerItem[]
  started_at: string
  finished_at: string
}

export interface QuizAttemptOut {
  attempt_id: string
  problemset_id?: string
  total: number
  correct: number
  score: number
  items: QuizAttemptItem[]
  started_at: string
  finished_at: string
  created_at: string
}

export interface QuizAttemptsResponse {
  items: QuizAttemptOut[]
  total: number
  page: number
  size: number
  pages: number
}

// Retry Problems Types
export interface RetryProblemItem {
  question: string
  options: string[]
  answer: string
  explanation: string
  topic: 'macro' | 'finance' | 'trade' | 'stats'
  level: 'basic' | 'intermediate' | 'advanced'
}

export interface RetryRequest {
  attempt_id: string
  model: string
  num_questions: number
}

export interface RetryResponse {
  attempt_id: string
  count: number
  problems: RetryProblemItem[]
  created_at: string
}

