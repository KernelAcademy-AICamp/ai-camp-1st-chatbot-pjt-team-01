import React, { useState } from 'react'
import { generateProblems } from '../../lib/api'
import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorDisplay from '../../components/ErrorDisplay'
import Badge from '../../components/ui/Badge'
import { BookOpen, Play, RefreshCw } from 'lucide-react'

// 타입 정의
interface ProblemItem {
  question: string
  options?: string[]
  answer: string
  explanation: string
  topic: 'macro' | 'finance' | 'trade' | 'stats'
  level: 'basic' | 'intermediate' | 'advanced'
}

// interface ProblemResponse {
//   items: ProblemItem[]
//   topic: 'macro' | 'finance' | 'trade' | 'stats'
//   level: 'basic' | 'intermediate' | 'advanced'
//   created_at: string
// }

interface ProblemRequest {
  topic: 'macro' | 'finance' | 'trade' | 'stats'
  level: 'basic' | 'intermediate' | 'advanced'
  style: 'mcq' | 'free'
  count: number
}

const ProblemsPage: React.FC = () => {
  // 상태 관리
  const navigate = useNavigate()
  const [formData, setFormData] = useState<ProblemRequest>({
    topic: 'macro',
    level: 'basic',
    style: 'mcq',
    count: 3  // 기본값을 3개로 줄임
  })
  
  const [problems, setProblems] = useState<ProblemItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // API 호출 함수
  const handleGenerateProblems = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('문제 생성 시작...', formData)
      const response = await generateProblems(formData)
      console.log('문제 생성 완료:', response.data)
      
      const problemsWithIds = response.data.items.map((problem: any, index: number) => ({
        ...problem,
        id: `problem_${Date.now()}_${index}` // 고유 ID 생성
      }))
      setProblems(problemsWithIds)
      
      // localStorage에 저장
      localStorage.setItem('recentProblems', JSON.stringify(problemsWithIds))
    } catch (err: any) {
      console.error('문제 생성 에러:', err)
      
      // 타임아웃 에러인 경우 특별한 메시지 표시
      if (err.message?.includes('timeout')) {
        setError('AI 문제 생성에 시간이 오래 걸리고 있습니다. 잠시 후 다시 시도해주세요.')
      } else if (err.message?.includes('Network Error')) {
        setError('네트워크 연결을 확인해주세요.')
      } else {
        setError(err.message || '문제 생성에 실패했습니다.')
      }
    } finally {
      setLoading(false)
    }
  }

  // 문제 풀기 함수
  const handleStartQuiz = () => {
    if (problems.length === 0) {
      alert('먼저 문제를 생성해주세요.')
      return
    }
    navigate('/problems/quiz')
  }

  // 입력 핸들러
  const handleInputChange = (field: keyof ProblemRequest, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">경제 문제 생성</h1>
        <p className="text-slate">AI가 생성하는 맞춤형 경제 문제를 풀어보세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Form */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2 text-gold" />
                문제 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Topic */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  주제
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'macro', label: '거시경제' },
                    { value: 'finance', label: '금융' },
                    { value: 'trade', label: '무역' },
                    { value: 'stats', label: '통계' },
                  ].map((opt) => (
                    <Button
                      key={opt.value}
                      size="sm"
                      variant={formData.topic === opt.value ? 'default' : 'outline'}
                      onClick={() => handleInputChange('topic', opt.value as ProblemRequest['topic'])}
                    >
                      {opt.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Level */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  난이도
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'basic', label: '초급' },
                    { value: 'intermediate', label: '중급' },
                    { value: 'advanced', label: '고급' },
                  ].map((opt) => (
                    <Button
                      key={opt.value}
                      size="sm"
                      variant={formData.level === opt.value ? 'default' : 'outline'}
                      onClick={() => handleInputChange('level', opt.value as ProblemRequest['level'])}
                    >
                      {opt.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Style */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  형식
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'mcq', label: '객관식' },
                    { value: 'free', label: '서술형' },
                  ].map((opt) => (
                    <Button
                      key={opt.value}
                      size="sm"
                      variant={formData.style === opt.value ? 'default' : 'outline'}
                      onClick={() => handleInputChange('style', opt.value as ProblemRequest['style'])}
                    >
                      {opt.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Count */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  문제 수
                </label>
                <Input
                  type="number"
                  min="1"
                  max="20"
                  value={formData.count}
                  onChange={(e) => handleInputChange('count', parseInt(e.target.value))}
                />
              </div>

              <Button
                className="w-full"
                onClick={handleGenerateProblems}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    AI가 문제를 생성하고 있습니다...
                  </>
                ) : (
                  <>
                    <BookOpen className="h-4 w-4 mr-2" />
                    문제 만들기
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-4">
          {loading && <LoadingSpinner text="문제를 생성하고 있습니다..." />}

          {error && (
            <ErrorDisplay
              message={error}
              onRetry={handleGenerateProblems}
            />
          )}

          {problems.length > 0 && (
            <>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-tight font-semibold">
                  생성된 문제 ({problems.length}개)
                </h2>
                <Button
                  onClick={handleStartQuiz}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Play className="h-4 w-4 mr-2" />
                  문제 풀기
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {problems.map((problem, index) => (
                  <Card
                    key={index}
                    className="hover:border-gold/50 transition-all group"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-gold transition-colors">
                            문제 {index + 1}
                          </h3>
                          <p className="text-sm text-slate-light mb-3 line-clamp-3">
                            {problem.question}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 mb-3">
                        <Badge variant="secondary">
                          {problem.topic === 'macro' ? '거시경제' : 
                           problem.topic === 'finance' ? '금융' :
                           problem.topic === 'trade' ? '무역' : '통계'}
                        </Badge>
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
                      </div>

                      {/* 객관식 보기 */}
                      {problem.options && problem.options.length > 0 && (
                        <div className="space-y-2 mb-3">
                          {problem.options.map((option, optIndex) => (
                            <div key={optIndex} className="flex items-center text-sm">
                              <span className="w-5 h-5 bg-noir-card rounded-full flex items-center justify-center text-xs font-medium text-slate-light mr-2">
                                {String.fromCharCode(65 + optIndex)}
                              </span>
                              <span className="text-slate-light">{option}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* 서술형 안내 */}
                      {(!problem.options || problem.options.length === 0) && (
                        <div className="bg-gold/10 border border-gold/20 rounded-lg p-3 mb-3">
                          <p className="text-gold text-sm font-medium">📝 서술형 문제</p>
                          <p className="text-slate-light text-xs mt-1">
                            아래 정답을 참고하여 자유롭게 답변해보세요.
                          </p>
                        </div>
                      )}

                      <div className="border-t border-noir-border pt-3 space-y-2">
                        <div className="text-xs">
                          <span className="text-green-400 font-medium">정답: </span>
                          <span className="text-slate-light">{problem.answer}</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-blue-400 font-medium">해설: </span>
                          <span className="text-slate-light line-clamp-2">{problem.explanation}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}

          {!loading && !error && problems.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <BookOpen className="h-16 w-16 text-slate-dark mx-auto mb-4" />
                <p className="text-slate">
                  설정을 선택하고 "문제 만들기"를 클릭하세요
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProblemsPage