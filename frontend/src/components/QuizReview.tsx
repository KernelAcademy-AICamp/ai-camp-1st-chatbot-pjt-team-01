import React from 'react'
import { useNavigate } from 'react-router-dom'
import { QuizAttemptOut, ProblemItem } from '../lib/types'
import { exportQuizAttemptJson, exportQuizAttemptCsv } from '../lib/api'
import { Card, CardContent } from './ui/Card'
import Button from './ui/Button'
import Badge from './ui/Badge'
import { RotateCcw, Download, Share, ArrowLeft, CheckCircle, XCircle } from 'lucide-react'

interface QuizReviewProps {
  attempt: QuizAttemptOut
  problems: ProblemItem[]
  onRetry: () => void
  onRetryProblems?: () => void
}

const QuizReview: React.FC<QuizReviewProps> = ({ attempt, problems, onRetry, onRetryProblems }) => {
  const navigate = useNavigate()

  const handleExportJson = async () => {
    try {
      const response = await exportQuizAttemptJson(attempt.attempt_id)
      const blob = new Blob([response.data], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `quiz_attempt_${attempt.attempt_id}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('JSON export failed:', error)
      alert('JSON 다운로드에 실패했습니다.')
    }
  }

  const handleExportCsv = async () => {
    try {
      const response = await exportQuizAttemptCsv(attempt.attempt_id)
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `quiz_attempt_${attempt.attempt_id}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('CSV export failed:', error)
      alert('CSV 다운로드에 실패했습니다.')
    }
  }

  const handleShareLink = () => {
    const reviewUrl = `${window.location.origin}/problems/quiz/review/${attempt.attempt_id}`
    navigator.clipboard.writeText(reviewUrl).then(() => {
      alert('리뷰 링크가 클립보드에 복사되었습니다!')
    }).catch(() => {
      alert('링크 복사에 실패했습니다.')
    })
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 space-y-6 animation-fade-in">
        {/* Header */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-tight font-bold text-white mb-2">퀴즈 리뷰</h1>
                <p className="text-slate">
                  시도 ID: {attempt.attempt_id.slice(0, 8)}...
                </p>
              </div>
              <div className="flex items-center space-x-4">
                {/* 점수 표시 */}
                <div className="text-center">
                  <div className="text-4xl font-bold text-gold">{attempt.score}%</div>
                  <div className="text-sm text-slate-light">
                    {attempt.correct}/{attempt.total} 정답
                  </div>
                </div>
              </div>
            </div>

            {/* 액션 버튼들 */}
            <div className="flex flex-wrap gap-3">
              <Button onClick={onRetry} className="bg-blue-600 hover:bg-blue-700">
                <RotateCcw className="h-4 w-4 mr-2" />
                다시 풀기
              </Button>
              {onRetryProblems && (
                <Button
                  onClick={onRetryProblems}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  AI 맞춤형 문제 생성
                </Button>
              )}
              <Button
                onClick={handleExportJson}
                className="bg-green-600 hover:bg-green-700"
              >
                <Download className="h-4 w-4 mr-2" />
                JSON 다운로드
              </Button>
              <Button
                onClick={handleExportCsv}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <Download className="h-4 w-4 mr-2" />
                CSV 다운로드
              </Button>
              <Button
                onClick={handleShareLink}
                className="bg-orange-600 hover:bg-orange-700"
              >
                <Share className="h-4 w-4 mr-2" />
                링크 공유
              </Button>
              <Button
                onClick={() => navigate('/problems')}
                variant="outline"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                문제 목록
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 결과 요약 */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-tight font-semibold text-white mb-4">결과 요약</h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">{attempt.total}</div>
                <div className="text-sm text-slate-light">총 문제</div>
              </div>
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-400">{attempt.correct}</div>
                <div className="text-sm text-slate-light">정답</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-400">
                  {attempt.total - attempt.correct}
                </div>
                <div className="text-sm text-slate-light">오답</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 문항별 상세 결과 */}
        <div className="space-y-6">
          <h2 className="text-xl font-tight font-semibold text-white">문항별 상세 결과</h2>
          {attempt.items.map((item, index) => {
            const problem = problems.find(p => p.id === item.question_id)
            return (
              <Card
                key={item.question_id}
                className={`border-l-4 ${
                  item.is_correct
                    ? 'border-green-500'
                    : 'border-red-500'
                }`}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">
                      문제 {index + 1}
                    </h3>
                    <Badge
                      variant={item.is_correct ? 'default' : 'secondary'}
                      className={item.is_correct ? 'bg-green-600' : 'bg-red-600'}
                    >
                      {item.is_correct ? (
                        <>
                          <CheckCircle className="h-3 w-3 mr-1" />
                          정답
                        </>
                      ) : (
                        <>
                          <XCircle className="h-3 w-3 mr-1" />
                          오답
                        </>
                      )}
                    </Badge>
                  </div>

                  {/* 문제 내용 */}
                  <div className="mb-4">
                    <p className="text-slate-light leading-relaxed mb-3">
                      {problem?.question}
                    </p>

                    {/* 객관식 보기들 */}
                    {problem?.options && problem.options.length > 0 && (
                      <div className="space-y-2">
                        {problem.options.map((option, optionIndex) => {
                          const optionLabel = String.fromCharCode(65 + optionIndex)
                          const isUserAnswer = item.user_answer === optionLabel
                          const isCorrectAnswer = item.correct_answer === optionLabel
                          
                          return (
                            <div
                              key={optionIndex}
                              className={`p-3 rounded-lg border-2 ${
                                isCorrectAnswer
                                  ? 'border-green-500 bg-green-500/10'
                                  : isUserAnswer && !isCorrectAnswer
                                  ? 'border-red-500 bg-red-500/10'
                                  : 'border-noir-border bg-noir-card'
                              }`}
                            >
                              <span className="font-medium text-white mr-2">
                                {optionLabel}.
                              </span>
                              <span className="text-slate-light">{option}</span>
                              {isCorrectAnswer && (
                                <span className="ml-2 text-green-400 font-semibold">
                                  ✓ 정답
                                </span>
                              )}
                              {isUserAnswer && !isCorrectAnswer && (
                                <span className="ml-2 text-red-400 font-semibold">
                                  ✗ 선택한 답
                                </span>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}

                    {/* 서술형 답안 표시 */}
                    {(!problem?.options || problem.options.length === 0) && (
                      <div className="space-y-3">
                        <div className="bg-gold/10 border border-gold/20 rounded-lg p-3">
                          <p className="text-gold text-sm font-medium">📝 서술형 문제</p>
                        </div>
                        <div className="bg-noir-card rounded-lg p-3">
                          <p className="text-slate-light text-sm">
                            <span className="font-medium">내 답안:</span> {item.user_answer}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 답안 정보 */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <span className="text-sm font-medium text-slate-light">내 답안:</span>
                      <span className={`ml-2 font-semibold ${
                        item.is_correct ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {item.user_answer}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-light">정답:</span>
                      <span className="ml-2 font-semibold text-green-400">
                        {item.correct_answer}
                      </span>
                    </div>
                  </div>

                  {/* 해설 */}
                  {problem?.explanation && (
                    <div className="bg-noir-card rounded-lg p-4 border border-noir-border">
                      <h4 className="font-semibold text-white mb-2">해설</h4>
                      <p className="text-slate-light leading-relaxed">
                        {problem.explanation}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default QuizReview
