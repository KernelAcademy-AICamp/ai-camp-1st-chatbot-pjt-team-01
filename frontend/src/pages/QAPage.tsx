import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { MessageSquare, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { qaChat, qaSummary } from '@/lib/api'
import Button from '@/components/ui/Button'
import Textarea from '@/components/ui/Textarea'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorDisplay from '@/components/ErrorDisplay'

const samplePrompts = [
  '이번 달 CPI 핵심 요약해줘',
  '기준금리 인상이 경제에 미치는 영향은?',
  '최근 실업률 동향 설명해줘',
]

const followUpButtons = [
  '더 간단히 설명',
  '리스크만 알려줘',
  '투자 관점에서',
]

export default function QAPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [citations, setCitations] = useState<string[]>([])

  const chatMutation = useMutation({
    mutationFn: (q: string) => qaChat({ question: q }),
    onSuccess: (response) => {
      setAnswer(response.data.answer_md)
      setCitations(response.data.citations || [])
    },
  })

  const summaryMutation = useMutation({
    mutationFn: (q: string) => qaSummary({ question: q }),
    onSuccess: (response) => {
      setAnswer(response.data.answer_md)
      setCitations(response.data.citations || [])
    },
  })

  const handleSubmit = () => {
    if (!question.trim()) return
    chatMutation.mutate(question)
  }

  const handleSamplePrompt = (prompt: string) => {
    setQuestion(prompt)
    summaryMutation.mutate(prompt)
  }

  const handleFollowUp = (followUp: string) => {
    // const followUpQuestion = `${answer}\n\n${followUp}`
    chatMutation.mutate(followUp)
  }

  const isLoading = chatMutation.isPending || summaryMutation.isPending
  const error = chatMutation.error || summaryMutation.error

  return (
    <div className="max-w-7xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">요약 & Q&A</h1>
        <p className="text-slate">
          경제 지표와 이슈에 대해 AI에게 물어보세요
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Input */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageSquare className="h-5 w-5 mr-2 text-gold" />
                질문하기
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="무엇이 궁금하신가요? 예) 이번 달 CPI 핵심만 요약해줘"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={6}
              />

              <div className="flex flex-wrap gap-2">
                {samplePrompts.map((prompt) => (
                  <Button
                    key={prompt}
                    size="sm"
                    variant="outline"
                    onClick={() => handleSamplePrompt(prompt)}
                    disabled={isLoading}
                  >
                    <Sparkles className="h-3 w-3 mr-1" />
                    {prompt}
                  </Button>
                ))}
              </div>

              <Button
                className="w-full"
                onClick={handleSubmit}
                disabled={isLoading || !question.trim()}
              >
                {isLoading ? '응답 생성 중...' : '질문하기'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right: Answer */}
        <div>
          <Card className="min-h-[400px]">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Sparkles className="h-5 w-5 mr-2 text-gold" />
                AI 응답
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading && <LoadingSpinner text="AI가 답변을 생성하고 있습니다..." />}

              {error && (
                <ErrorDisplay
                  message={error.message}
                  onRetry={() => handleSubmit()}
                />
              )}

              {!isLoading && !error && answer && (
                <div className="space-y-4">
                  <div className="prose prose-invert max-w-none">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => (
                          <p className="mb-3 text-slate-light">{children}</p>
                        ),
                        h1: ({ children }) => (
                          <h1 className="text-2xl font-bold mb-3 text-white">
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 className="text-xl font-bold mb-2 text-white">
                            {children}
                          </h2>
                        ),
                        ul: ({ children }) => (
                          <ul className="list-disc list-inside space-y-1 mb-3">
                            {children}
                          </ul>
                        ),
                        li: ({ children }) => (
                          <li className="text-slate-light">{children}</li>
                        ),
                        code: ({ children }) => (
                          <code className="bg-noir-bg px-1.5 py-0.5 rounded text-gold text-sm">
                            {children}
                          </code>
                        ),
                      }}
                    >
                      {answer}
                    </ReactMarkdown>
                  </div>

                  {citations.length > 0 && (
                    <div className="pt-4 border-t border-noir-border">
                      <p className="text-sm font-medium text-slate mb-2">참고 출처:</p>
                      <div className="flex flex-wrap gap-2">
                        {citations.map((citation, idx) => (
                          <Badge key={idx} variant="secondary">
                            {citation}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t border-noir-border">
                    <p className="text-sm font-medium text-slate mb-2">
                      추가 질문:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {followUpButtons.map((followUp) => (
                        <Button
                          key={followUp}
                          size="sm"
                          variant="outline"
                          onClick={() => handleFollowUp(followUp)}
                          disabled={isLoading}
                        >
                          {followUp}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {!isLoading && !error && !answer && (
                <div className="text-center py-12">
                  <MessageSquare className="h-16 w-16 text-slate-dark mx-auto mb-4" />
                  <p className="text-slate">
                    질문을 입력하거나 샘플 프롬프트를 선택해주세요
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

