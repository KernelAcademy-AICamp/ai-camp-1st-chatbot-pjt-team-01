import React, { useState, useEffect } from 'react'
import { ProblemItem, QuizAttemptOut } from '../lib/types'
import { createQuizAttempt } from '../lib/api'
import QuizReview from '../components/QuizReview'
import { Card, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorDisplay from '../components/ErrorDisplay'
import Badge from '../components/ui/Badge'
import { BookOpen, ArrowLeft, CheckCircle } from 'lucide-react'

interface ProblemsQuizPageProps {
  problems?: ProblemItem[]
}

const ProblemsQuizPage: React.FC<ProblemsQuizPageProps> = ({ problems: propsProblems }) => {
  const [problems, setProblems] = useState<ProblemItem[]>([])
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [attemptResult, setAttemptResult] = useState<QuizAttemptOut | null>(null)
  const [showReview, setShowReview] = useState(false)
  const [startTime, setStartTime] = useState<Date | null>(null)

  // 문제 데이터 로딩 (props 또는 localStorage)
  useEffect(() => {
    if (propsProblems && propsProblems.length > 0) {
      setProblems(propsProblems)
      setStartTime(new Date())
    } else {
      // localStorage에서 최근 생성된 문제 불러오기
      const savedProblems = localStorage.getItem('recentProblems')
      if (savedProblems) {
        try {
          const parsedProblems = JSON.parse(savedProblems)
          setProblems(parsedProblems)
          setStartTime(new Date())
        } catch (error) {
          console.error('Failed to parse saved problems:', error)
        }
      }
    }
  }, [propsProblems])

  // 사용자 답안 선택 핸들러
  const handleAnswerSelect = (questionId: string, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }))
  }

  // 제출하기 버튼 핸들러
  const handleSubmit = async () => {
    if (problems.length === 0) {
      alert('문제가 없습니다.')
      return
    }

    // 모든 문제에 답했는지 확인
    const unansweredQuestions = problems.filter(problem => !userAnswers[problem.id || ''])
    if (unansweredQuestions.length > 0) {
      alert('모든 문제에 답해주세요.')
      return
    }

    setIsSubmitting(true)

    try {
      const finishedTime = new Date()
      
      // 답안 데이터 준비
      const answers = problems.map(problem => ({
        question_id: problem.id || '',
        user_answer: userAnswers[problem.id || '']
      }))

      // 퀴즈 시도 생성 및 채점
      const response = await createQuizAttempt({
        problemset_id: undefined, // 선택사항
        items: answers,
        started_at: startTime?.toISOString() || new Date().toISOString(),
        finished_at: finishedTime.toISOString()
      })

      setAttemptResult(response.data)
      setShowReview(true)
    } catch (error) {
      console.error('Quiz submission failed:', error)
      alert('제출에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // 다시 풀기 버튼 핸들러
  const handleRetry = () => {
    setUserAnswers({})
    setAttemptResult(null)
    setShowReview(false)
    setStartTime(new Date())
  }

  if (problems.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <BookOpen className="h-16 w-16 text-slate-dark mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-4">문제가 없습니다</h2>
            <p className="text-slate mb-6">먼저 문제를 생성해주세요.</p>
            <Button
              onClick={() => window.history.back()}
              variant="outline"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              돌아가기
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="w-full py-8">
      <div className="w-full px-4 lg:px-8 xl:px-16 space-y-6 animation-fade-in quiz-container no-max-width">
        {/* Header */}
        <div className="text-center lg:text-left">
          <h1 className="text-3xl lg:text-4xl font-tight font-bold mb-2">경제 문제 풀이</h1>
          <p className="text-slate text-lg">총 {problems.length}문제를 풀어보세요!</p>
        </div>

        {!showReview ? (
          <>
            {/* 문제 목록 */}
            <div className="space-y-8 w-full">
              {problems.map((problem, index) => (
                <Card key={problem.id || index} className="w-full max-w-none !p-0">
                  <CardContent className="p-8 lg:p-10 w-full">
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl lg:text-2xl font-semibold text-white">
                          문제 {index + 1}
                        </h3>
                        {/* 난이도 표시 */}
                        {problem.level && (
                          <Badge 
                            variant={problem.level === 'basic' ? 'default' : 
                                    problem.level === 'intermediate' ? 'secondary' : 'outline'}
                            className={problem.level === 'basic' ? 'bg-green-600 hover:bg-green-700' :
                                       problem.level === 'intermediate' ? 'bg-yellow-600 hover:bg-yellow-700' :
                                       'bg-red-600 hover:bg-red-700 text-white'}
                          >
                            {problem.level === 'basic' ? '🟢 초급' :
                             problem.level === 'intermediate' ? '🟡 중급' : '🔴 고급'}
                          </Badge>
                        )}
                      </div>
                      <p className="text-slate-light leading-relaxed text-lg lg:text-xl">{problem.question}</p>
                    </div>

                    {/* 객관식 보기 */}
                    {problem.options && Array.isArray(problem.options) && problem.options.length > 0 && (
                      <div className="space-y-4">
                        {problem.options.map((option, optionIndex) => {
                          const optionLabel = String.fromCharCode(65 + optionIndex) // A, B, C, D
                          const isSelected = userAnswers[problem.id || ''] === optionLabel
                          
                          return (
                            <label
                              key={optionIndex}
                              className={`flex items-center p-4 lg:p-5 rounded-lg border-2 cursor-pointer transition-all ${
                                isSelected
                                  ? 'border-gold bg-gold/10'
                                  : 'border-noir-border hover:border-gold/50'
                              }`}
                            >
                              <input
                                type="radio"
                                name={`question-${problem.id || index}`}
                                value={optionLabel}
                                checked={isSelected}
                                onChange={() => handleAnswerSelect(problem.id || '', optionLabel)}
                                className="sr-only"
                              />
                              <div className={`w-7 h-7 lg:w-8 lg:h-8 rounded-full border-2 mr-4 flex items-center justify-center ${
                                isSelected ? 'border-gold bg-gold' : 'border-noir-border'
                              }`}>
                                {isSelected && (
                                  <CheckCircle className="w-4 h-4 lg:w-5 lg:h-5 text-noir-bg" />
                                )}
                              </div>
                              <span className="font-medium text-white mr-3 text-lg lg:text-xl">{optionLabel}.</span>
                              <span className="text-slate-light text-lg lg:text-xl">{option}</span>
                            </label>
                          )
                        })}
                      </div>
                    )}

                    {/* 서술형 답변 입력 */}
                    {(!problem.options || !Array.isArray(problem.options) || problem.options.length === 0) && (
                      <div className="space-y-4">
                        <div className="bg-gold/10 border border-gold/20 rounded-lg p-4 lg:p-5">
                          <p className="text-gold text-base lg:text-lg font-medium mb-2">📝 서술형 문제</p>
                          <p className="text-slate-light text-sm lg:text-base">
                            자유롭게 답변을 작성해주세요.
                          </p>
                        </div>
                        <textarea
                          placeholder="답변을 입력하세요..."
                          value={userAnswers[problem.id || ''] || ''}
                          onChange={(e) => handleAnswerSelect(problem.id || '', e.target.value)}
                          className="w-full p-4 lg:p-5 rounded-lg border border-noir-border bg-noir-card text-white placeholder-slate-light focus:border-gold focus:outline-none resize-none text-lg lg:text-xl"
                          rows={5}
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 제출하기 버튼 */}
            <div className="mt-12 text-center">
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting}
                size="lg"
                className="bg-green-600 hover:bg-green-700 text-lg lg:text-xl px-8 lg:px-12 py-4 lg:py-5"
              >
                {isSubmitting ? '제출 중...' : '제출하기'}
              </Button>
            </div>
          </>
        ) : (
          /* 리뷰 화면 */
          attemptResult && (
            <QuizReview
              attempt={attemptResult}
              problems={problems}
              onRetry={handleRetry}
            />
          )
        )}
      </div>
    </div>
  )
}

export default ProblemsQuizPage
