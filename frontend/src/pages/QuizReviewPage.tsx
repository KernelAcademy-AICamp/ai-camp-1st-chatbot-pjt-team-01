import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { QuizAttemptOut, ProblemItem } from '../lib/types'
import { getQuizAttempt } from '../lib/api'
import QuizReview from '../components/QuizReview'
import LoadingSpinner from '../components/LoadingSpinner'

const QuizReviewPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>()
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState<QuizAttemptOut | null>(null)
  const [problems, setProblems] = useState<ProblemItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAttemptData = async () => {
      if (!attemptId) {
        setError('시도 ID가 없습니다.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const response = await getQuizAttempt(attemptId)
        const attemptData = response.data
        
        setAttempt(attemptData)
        
        // 문제 데이터를 attempt에서 추출하여 ProblemItem 형태로 변환
        const problemItems: ProblemItem[] = attemptData.items.map((item: any, index: number) => ({
          id: item.question_id,
          question: `문제 ${index + 1}`, // 실제 문제 내용은 백엔드에서 제공하지 않으므로 임시로 설정
          answer: item.correct_answer,
          explanation: `정답: ${item.correct_answer}`, // 실제 해설은 백엔드에서 제공하지 않으므로 임시로 설정
          options: ['A', 'B', 'C', 'D'] // 기본 옵션 설정
        }))
        
        setProblems(problemItems)
      } catch (error) {
        console.error('Failed to fetch attempt data:', error)
        setError('퀴즈 시도 데이터를 불러올 수 없습니다.')
      } finally {
        setLoading(false)
      }
    }

    fetchAttemptData()
  }, [attemptId])

  const handleRetry = () => {
    // 문제 생성 페이지로 이동
    navigate('/problems')
  }

  const handleRetryProblems = () => {
    // AI 맞춤형 재시도 문제 페이지로 이동
    navigate(`/problems/retry/${attemptId}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error || !attempt) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">오류 발생</h2>
          <p className="text-gray-600 mb-6">{error || '퀴즈 시도를 찾을 수 없습니다.'}</p>
          <button
            onClick={() => navigate('/problems')}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            문제 목록으로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  return (
    <QuizReview
      attempt={attempt}
      problems={problems}
      onRetry={handleRetry}
      onRetryProblems={handleRetryProblems}
    />
  )
}

export default QuizReviewPage
