import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { MessageSquare, Sparkles, Upload, X, FileText, Database, Clock, CheckCircle2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { qaChat, qaSummary, qaUploadFiles, getUploads } from '@/lib/api'
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

type Tab = 'upload' | 'saved'

interface SavedDocument {
  filename?: string
  storage_id?: string
  upload_id?: string
  document_id?: string
  timestamp: string
  question: string
  file_count: number
  text_length?: number
  original_filenames?: string[]
}

export default function QAPage() {
  // 기본 상태
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [citations, setCitations] = useState<string[]>([])

  // 탭 상태
  const [activeTab, setActiveTab] = useState<Tab>('upload')

  // 새 문서 업로드 상태
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])

  // 저장된 문서 상태
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null)
  const [savedDocuments, setSavedDocuments] = useState<SavedDocument[]>([])

  // 저장된 문서 목록 조회
  const { data: uploadsData, refetch: refetchUploads } = useQuery({
    queryKey: ['uploads'],
    queryFn: getUploads,
  })

  useEffect(() => {
    if (uploadsData?.data?.uploads) {
      setSavedDocuments(uploadsData.data.uploads)
    } else {
      setSavedDocuments([])
    }
  }, [uploadsData])

  // Mutations
  const chatMutation = useMutation({
    mutationFn: (data: { question: string; document?: string }) =>
      qaChat({
        question: data.question,
        context: data.document
      }),
    onSuccess: (response) => {
      setAnswer(response.data.answer_md)
      setCitations(response.data.citations || [])
    },
  })

  const summaryMutation = useMutation({
    mutationFn: (data: { question: string; document?: string }) =>
      qaSummary({
        question: data.question,
        context: data.document
      }),
    onSuccess: (response) => {
      setAnswer(response.data.answer_md)
      setCitations(response.data.citations || [])
    },
  })

  const uploadMutation = useMutation({
    mutationFn: (data: { question: string; files: File[] }) =>
      qaUploadFiles(data),
    onSuccess: (response) => {
      setAnswer(response.data.answer_md)
      setCitations(response.data.citations || [])
      setUploadedFiles([])
      refetchUploads()
    },
  })

  // 파일 업로드 핸들러
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      const fileArray = Array.from(files)
      const validFiles = fileArray.filter(file => {
        if (file.size > 10 * 1024 * 1024) {
          alert(`${file.name}은(는) 10MB를 초과합니다.`)
          return false
        }
        return true
      })
      setUploadedFiles(prev => [...prev, ...validFiles])
    }
  }

  const handleFileRemove = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  // 드래그&드롭 핸들러
  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const files = e.dataTransfer.files
    if (files) {
      const fileArray = Array.from(files)
      const validFiles = fileArray.filter(file => {
        // 파일 형식 검증
        const validExtensions = ['.pdf', '.doc', '.docx', '.txt']
        const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
        if (!validExtensions.includes(fileExtension)) {
          alert(`${file.name}은(는) 지원하지 않는 형식입니다. (PDF, DOCX, TXT만 가능)`)
          return false
        }
        // 파일 크기 검증
        if (file.size > 10 * 1024 * 1024) {
          alert(`${file.name}은(는) 10MB를 초과합니다.`)
          return false
        }
        return true
      })
      setUploadedFiles(prev => [...prev, ...validFiles])
    }
  }

  // 문서 저장 (업로드)
  const handleSaveDocument = () => {
    if (uploadedFiles.length === 0) {
      alert('업로드할 파일을 선택해주세요.')
      return
    }

    uploadMutation.mutate({
      question: question || '문서 업로드',
      files: uploadedFiles
    })
  }

  // 질문 제출
  const handleSubmit = () => {
    if (!question.trim()) {
      alert('질문을 입력해주세요.')
      return
    }

    if (activeTab === 'saved' && !selectedDocument) {
      alert('문서를 먼저 선택해주세요.')
      return
    }

    const data = {
      question: question,
      document: activeTab === 'saved' && selectedDocument ? selectedDocument : undefined
    }

    chatMutation.mutate(data)
  }

  const handleSamplePrompt = (prompt: string) => {
    setQuestion(prompt)
    if (activeTab === 'saved' && selectedDocument) {
      summaryMutation.mutate({ question: prompt, document: selectedDocument })
    } else {
      summaryMutation.mutate({ question: prompt })
    }
  }

  const handleFollowUp = (followUp: string) => {
    chatMutation.mutate({
      question: followUp,
      document: activeTab === 'saved' && selectedDocument ? selectedDocument : undefined
    })
  }

  const isLoading = chatMutation.isPending || summaryMutation.isPending || uploadMutation.isPending
  const error = chatMutation.error || summaryMutation.error || uploadMutation.error

  return (
    <div className="max-w-7xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">요약 & Q&A</h1>
        <p className="text-slate">
          문서를 업로드하거나 저장된 문서를 선택하여 AI에게 질문하세요
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Input */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="h-5 w-5 mr-2 text-gold" />
                문서 관리
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 탭 전환 */}
              <div className="flex gap-2 p-1 bg-noir-bg rounded-lg">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
                    activeTab === 'upload'
                      ? 'bg-gold text-noir-bg'
                      : 'text-slate hover:text-gold'
                  }`}
                >
                  <Upload className="inline h-4 w-4 mr-2" />
                  새 문서 업로드
                </button>
                <button
                  onClick={() => {
                    setActiveTab('saved')
                    refetchUploads()
                  }}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition ${
                    activeTab === 'saved'
                      ? 'bg-gold text-noir-bg'
                      : 'text-slate hover:text-gold'
                  }`}
                >
                  <FileText className="inline h-4 w-4 mr-2" />
                  저장된 문서
                </button>
              </div>

              {/* 탭 1: 새 문서 업로드 */}
              {activeTab === 'upload' && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label
                      className="block"
                      onDragOver={handleDragOver}
                      onDrop={handleDrop}
                    >
                      <div className="flex items-center justify-center w-full h-32 px-4 transition bg-noir-card border-2 border-noir-border border-dashed rounded-lg hover:border-gold cursor-pointer group">
                        <div className="text-center">
                          <Upload className="w-8 h-8 mx-auto text-slate group-hover:text-gold transition" />
                          <p className="mt-2 text-sm text-slate">
                            <span className="font-medium text-gold">클릭</span>하거나 파일을 드래그하여 업로드
                          </p>
                          <p className="text-xs text-slate-dark mt-1">
                            PDF, DOCX, TXT (최대 10MB)
                          </p>
                        </div>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        onChange={handleFileChange}
                        multiple
                        accept=".pdf,.doc,.docx,.txt"
                        disabled={isLoading}
                      />
                    </label>

                    {/* 업로드된 파일 목록 */}
                    {uploadedFiles.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate">
                          업로드된 파일 ({uploadedFiles.length})
                        </p>
                        {uploadedFiles.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-noir-card border border-noir-border rounded-lg hover:border-gold transition"
                          >
                            <div className="flex items-center space-x-3 flex-1 min-w-0">
                              <FileText className="w-5 h-5 text-gold flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm text-slate-light truncate">
                                  {file.name}
                                </p>
                                <p className="text-xs text-slate-dark">
                                  {(file.size / 1024).toFixed(1)} KB
                                </p>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleFileRemove(index)}
                              className="ml-2 p-1 text-slate-dark hover:text-red-500 hover:bg-red-500/10 rounded transition flex-shrink-0"
                              disabled={isLoading}
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <Textarea
                    placeholder="문서에 대한 설명이나 메모 (선택사항)"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    rows={3}
                  />

                  <Button
                    className="w-full"
                    onClick={handleSaveDocument}
                    disabled={isLoading || uploadedFiles.length === 0}
                  >
                    {isLoading ? 'DB에 저장 중...' : '문서 저장하기'}
                  </Button>
                </div>
              )}

              {/* 탭 2: 저장된 문서 */}
              {activeTab === 'saved' && (
                <div className="space-y-4">
                  <div className="max-h-96 overflow-y-auto space-y-2">
                    {savedDocuments.length === 0 ? (
                      <div className="text-center py-8">
                        <FileText className="w-12 h-12 text-slate-dark mx-auto mb-2" />
                        <p className="text-sm text-slate">저장된 문서가 없습니다</p>
                      </div>
                    ) : (
                      savedDocuments.map((doc, index) => {
                        // docId는 표시용 (확장자 없음)
                        const docId = doc.storage_id || doc.upload_id || doc.filename || `doc-${index}`

                        // actualDocumentId는 백엔드로 전송용 (.json 포함)
                        const actualDocumentId = doc.filename || `${doc.storage_id}.json`

                        let displayName = '문서'
                        if (doc.original_filenames && doc.original_filenames.length > 0) {
                          displayName = doc.original_filenames[0]
                        } else if (doc.storage_id) {
                          displayName = doc.storage_id
                        } else if (doc.filename) {
                          displayName = doc.filename.replace('.json', '')
                        } else if (doc.upload_id) {
                          displayName = doc.upload_id
                        }

                        return (
                          <div
                            key={index}
                            onClick={() => setSelectedDocument(actualDocumentId)}
                            className={`p-4 rounded-lg border cursor-pointer transition ${
                              selectedDocument === actualDocumentId
                                ? 'border-gold bg-gold/10'
                                : 'border-noir-border bg-noir-card hover:border-gold/50'
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <FileText className="w-4 h-4 text-gold flex-shrink-0" />
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-slate-light truncate">
                                      {displayName}
                                    </p>
                                    {doc.original_filenames && doc.original_filenames.length > 1 && (
                                      <p className="text-xs text-slate-dark truncate">
                                        외 {doc.original_filenames.length - 1}개 파일
                                      </p>
                                    )}
                                  </div>
                                  {selectedDocument === actualDocumentId && (
                                    <CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" />
                                  )}
                                </div>
                                <div className="flex items-center gap-3 text-xs text-slate-dark">
                                  <span className="flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    {new Date(doc.timestamp).toLocaleString('ko-KR')}
                                  </span>
                                  <span>{doc.file_count}개 파일</span>
                                </div>
                                {doc.question && (
                                  <p className="text-xs text-slate mt-2 line-clamp-2">
                                    {doc.question}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        )
                      })
                    )}
                  </div>

                  {selectedDocument && (
                    <div className="p-3 bg-gold/10 border border-gold rounded-lg">
                      <p className="text-xs text-gold font-medium mb-1">선택된 문서:</p>
                      <p className="text-sm text-slate-light">
                        {selectedDocument?.includes('.json')
                          ? selectedDocument.replace('.json', '')
                          : selectedDocument}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* 공통: 질문 영역 */}
              <div className="pt-4 border-t border-noir-border space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate mb-2 block">
                    질문하기
                  </label>
                  <Textarea
                    placeholder={
                      activeTab === 'saved' && selectedDocument
                        ? '선택한 문서에 대해 질문하세요'
                        : '무엇이 궁금하신가요?'
                    }
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  {samplePrompts.map((prompt) => (
                    <Button
                      key={prompt}
                      size="sm"
                      variant="outline"
                      onClick={() => handleSamplePrompt(prompt)}
                      disabled={isLoading || (activeTab === 'saved' && !selectedDocument)}
                    >
                      <Sparkles className="h-3 w-3 mr-1" />
                      {prompt}
                    </Button>
                  ))}
                </div>

                <Button
                  className="w-full"
                  onClick={handleSubmit}
                  disabled={
                    isLoading ||
                    !question.trim() ||
                    (activeTab === 'saved' && !selectedDocument)
                  }
                >
                  {isLoading ? '응답 생성 중...' : '질문하기'}
                </Button>
              </div>
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
              {isLoading && (
                <LoadingSpinner
                  text={
                    uploadMutation.isPending
                      ? '파일을 처리하고 있습니다...'
                      : 'AI가 답변을 생성하고 있습니다...'
                  }
                />
              )}

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
                      <p className="text-sm font-medium text-slate mb-2">
                        참고 출처:
                      </p>
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
                    {activeTab === 'upload'
                      ? '문서를 업로드하고 저장하세요'
                      : '문서를 선택하고 질문해주세요'}
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
