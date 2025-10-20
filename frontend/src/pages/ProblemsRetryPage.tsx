import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { createRetryProblems, getQuizAttempt } from '../lib/api'
import { RetryResponse, QuizAttemptOut } from '../lib/types'
import { Card, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'

const ProblemsRetryPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>()
  const navigate = useNavigate()
  
  const [retryData, setRetryData] = useState<RetryResponse | null>(null)
  const [attemptData, setAttemptData] = useState<QuizAttemptOut | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!attemptId) {
      setError('시도 ID가 없습니다.')
      setLoading(false)
      return
    }

    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        console.log('재시도 문제 생성 시작...', attemptId)
        
        // 1. 기존 시도 데이터 조회
        const attemptResponse = await getQuizAttempt(attemptId)
        const attempt = attemptResponse.data as QuizAttemptOut
        setAttemptData(attempt)

        // 2. 재시도 문제 생성 요청
        const retryResponse = await createRetryProblems({
          attempt_id: attemptId,
          model: 'gpt-3.5-turbo',  // 더 빠른 모델 사용
          num_questions: 3  // 3개로 줄임
        })
        
        const retry = retryResponse.data as RetryResponse
        setRetryData(retry)
        
        console.log('재시도 문제 생성 완료:', retry)

      } catch (err) {
        console.error('데이터 로딩 실패:', err)
        
        // 타임아웃 에러인 경우 특별한 메시지 표시
        if (err instanceof Error && err.message?.includes('timeout')) {
          setError('AI 맞춤형 문제 생성에 시간이 오래 걸리고 있습니다. 잠시 후 다시 시도해주세요.')
        } else if (err instanceof Error && err.message?.includes('Network Error')) {
          setError('네트워크 연결을 확인해주세요.')
        } else {
          setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [attemptId])

  const handleRetryQuiz = () => {
    if (!retryData) return

    // 문제 세트를 localStorage에 저장
    const problemSet = {
      id: `retry-${attemptId}-${Date.now()}`,
      title: `AI 맞춤형 재시도 문제 (${retryData.count}문제)`,
      items: retryData.problems.map((problem, index) => ({
        question_id: `retry-${attemptId}-${index}`,
        question: problem.question,
        options: problem.options,
        answer: problem.answer,
        explanation: problem.explanation,
        topic: problem.topic,
        level: problem.level
      })),
      created_at: new Date().toISOString(),
      source: 'retry'
    }

    localStorage.setItem('currentProblemSet', JSON.stringify(problemSet))
    navigate('/problems/quiz')
  }

  const getTopicLabel = (topic: string) => {
    const labels: Record<string, string> = {
      macro: '거시경제',
      finance: '금융',
      trade: '무역',
      stats: '통계'
    }
    return labels[topic] || topic
  }

  const getLevelLabel = (level: string) => {
    const labels: Record<string, string> = {
      basic: '기초',
      intermediate: '중급',
      advanced: '고급'
    }
    return labels[level] || level
  }

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      basic: 'bg-green-100 text-green-800',
      intermediate: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-red-100 text-red-800'
    }
    return colors[level] || 'bg-gray-100 text-gray-800'
  }

  const getTopicColor = (topic: string) => {
    const colors: Record<string, string> = {
      macro: 'bg-blue-100 text-blue-800',
      finance: 'bg-purple-100 text-purple-800',
      trade: 'bg-orange-100 text-orange-800',
      stats: 'bg-indigo-100 text-indigo-800'
    }
    return colors[topic] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorDisplay message={error} />
      </div>
    )
  }

  if (!retryData || !attemptData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorDisplay message="데이터를 찾을 수 없습니다." />
      </div>
    )
  }

  // 틀린 문제 분석
  const wrongQuestions = attemptData.items.filter(item => !item.is_correct)
  const correctQuestions = attemptData.items.filter(item => item.is_correct)
  
  // 주제별 틀린 문제 분석
  const wrongTopics = wrongQuestions.reduce((acc, _item) => {
    // 실제로는 문제 상세 정보에서 topic을 가져와야 하지만, 여기서는 기본값 사용
    const topic = 'macro' // 실제로는 문제 데이터에서 가져와야 함
    acc[topic] = (acc[topic] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="max-w-7xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">
          AI 맞춤형 재시도 문제
        </h1>
        <p className="text-slate">
          틀린 문제를 분석하여 생성된 맞춤형 문제입니다.
        </p>
      </div>

      {/* AI 피드백 요약 */}
      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <svg className="w-6 h-6 text-gold mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI 피드백 요약
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 점수 요약 */}
            <div className="space-y-3">
              <h3 className="font-medium text-white">점수 분석</h3>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm text-slate-light">정답: {correctQuestions.length}문제</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                  <span className="text-sm text-slate-light">오답: {wrongQuestions.length}문제</span>
                </div>
              </div>
              <div className="text-2xl font-bold text-white">
                {attemptData.score}점
              </div>
            </div>

            {/* 주제별 분석 */}
            <div className="space-y-3">
              <h3 className="font-medium text-white">틀린 개념 분석</h3>
              <div className="space-y-2">
                {Object.entries(wrongTopics).map(([topic, count]) => (
                  <div key={topic} className="flex items-center justify-between">
                    <Badge variant="secondary">
                      {getTopicLabel(topic)}
                    </Badge>
                    <span className="text-sm text-slate-light">{count}문제 틀림</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 학습 팁 */}
          <div className="mt-6 p-4 bg-gold/10 rounded-lg border border-gold/20">
            <h4 className="font-medium text-gold mb-2">💡 학습 팁</h4>
            <p className="text-slate-light text-sm">
              틀린 문제들을 바탕으로 생성된 맞춤형 문제를 통해 약한 부분을 보완해보세요. 
              각 문제의 해설을 꼼꼼히 읽고 관련 개념을 다시 학습하는 것이 중요합니다.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 생성된 문제 목록 */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-tight font-semibold text-white">
            생성된 맞춤형 문제 ({retryData.count}문제)
          </h2>
          <Button 
            onClick={handleRetryQuiz}
            className="bg-blue-600 hover:bg-blue-700"
          >
            다시 풀기
          </Button>
        </div>

        {retryData.problems.map((problem, index) => (
          <Card key={index} className="hover:border-gold/50 transition-all group">
            <CardContent className="p-6">
              {/* 문제 헤더 */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    문제 {index + 1}
                  </Badge>
                  <Badge variant="secondary">
                    {getTopicLabel(problem.topic)}
                  </Badge>
                  <Badge variant="secondary">
                    {getLevelLabel(problem.level)}
                  </Badge>
                </div>
              </div>

              {/* 문제 내용 */}
              <div className="mb-4">
                <h3 className="text-lg font-medium text-white mb-3 group-hover:text-gold transition-colors">
                  {problem.question}
                </h3>
                
                {/* 선택지 */}
                <div className="space-y-2">
                  {problem.options.map((option, optionIndex) => (
                    <div 
                      key={optionIndex}
                      className={`p-3 rounded-lg border ${
                        option.startsWith(problem.answer) 
                          ? 'bg-green-500/10 border-green-500/50 text-green-400' 
                          : 'bg-noir-card border-noir-border text-slate-light'
                      }`}
                    >
                      <div className="flex items-center">
                        <span className="font-medium mr-2">
                          {String.fromCharCode(65 + optionIndex)})
                        </span>
                        <span>{option}</span>
                        {option.startsWith(problem.answer) && (
                          <svg className="w-5 h-5 text-green-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 해설 */}
              <div className="bg-noir-card p-4 rounded-lg border border-noir-border">
                <h4 className="font-medium text-white mb-2 flex items-center">
                  <svg className="w-4 h-4 text-slate-light mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  해설
                </h4>
                <p className="text-slate-light text-sm leading-relaxed">
                  {problem.explanation}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 하단 액션 버튼 */}
      <div className="mt-8 flex justify-center">
        <Button 
          onClick={handleRetryQuiz}
          size="lg"
          className="bg-blue-600 hover:bg-blue-700"
        >
          맞춤형 문제 다시 풀기
        </Button>
      </div>
    </div>
  )
}

export default ProblemsRetryPage
