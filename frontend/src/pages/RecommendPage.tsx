import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, BookOpen, TrendingUp } from 'lucide-react'
import { api } from '@/lib/api'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorDisplay from '@/components/ErrorDisplay'

interface TermSearchResult {
  term: string
  english: string
  definition: string
  similarity: number
  similarity_percent: number
}

interface SearchResponse {
  query: string
  results: TermSearchResult[]
  count: number
}

export default function RecommendPage() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState<TermSearchResult[]>([])
  const [lastQuery, setLastQuery] = useState('')

  const searchMutation = useMutation({
    mutationFn: async (searchQuery: string) => {
      const response = await api.post<SearchResponse>('/term-search/', {
        query: searchQuery,
        top_k: 3,
      })
      return response.data
    },
    onSuccess: (data) => {
      setSearchResults(data.results)
      setLastQuery(data.query)
    },
  })

  const handleSearch = () => {
    if (!query.trim()) return
    searchMutation.mutate(query)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const getSimilarityColor = (percent: number) => {
    if (percent >= 80) return 'text-emerald-400'
    if (percent >= 60) return 'text-yellow-400'
    return 'text-slate-light'
  }

  const getSimilarityBg = (percent: number) => {
    if (percent >= 80) return 'bg-emerald-500/20 border-emerald-500/30'
    if (percent >= 60) return 'bg-yellow-500/20 border-yellow-500/30'
    return 'bg-slate-700/20 border-slate-600/30'
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-tight font-bold mb-3 flex items-center justify-center">
          <BookOpen className="h-9 w-9 mr-3 text-gold" />
          경제 용어 검색
        </h1>
        <p className="text-slate-light text-lg">
          궁금한 경제 용어를 검색하고 AI가 찾아드립니다
        </p>
      </div>

      {/* Search Input */}
      <Card className="border-2 border-gold/30 shadow-lg">
        <CardContent className="p-6">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-light" />
              <Input
                placeholder="예: 인플레이션이란?, GDP 의미, 금리 설명..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pl-11 h-12 text-base"
                disabled={searchMutation.isPending}
              />
            </div>
            <Button
              onClick={handleSearch}
              disabled={searchMutation.isPending || !query.trim()}
              className="h-12 px-8"
              size="lg"
            >
              {searchMutation.isPending ? '검색 중...' : '검색'}
            </Button>
          </div>

          {/* Examples */}
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-slate-light">💡 추천 검색:</span>
            {['인플레이션이란?', 'GDP 의미', '금리 설명', '환율 정의'].map(
              (example) => (
                <button
                  key={example}
                  onClick={() => {
                    setQuery(example)
                    searchMutation.mutate(example)
                  }}
                  className="text-xs px-3 py-1 rounded-full bg-noir-bg border border-slate-dark hover:border-gold/50 text-slate-light hover:text-gold transition-colors"
                  disabled={searchMutation.isPending}
                >
                  {example}
                </button>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {searchMutation.isPending && (
        <LoadingSpinner text="AI가 관련 경제 용어를 검색하고 있습니다..." />
      )}

      {/* Error State */}
      {searchMutation.error && (
        <ErrorDisplay
          message={(searchMutation.error as any).message}
          onRetry={handleSearch}
        />
      )}

      {/* Search Results */}
      {searchResults.length > 0 && !searchMutation.isPending && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-tight font-bold flex items-center">
              <TrendingUp className="h-6 w-6 mr-2 text-gold" />
              검색 결과
            </h2>
            <span className="text-slate-light text-sm">
              "{lastQuery}" 검색 결과 {searchResults.length}개
            </span>
          </div>

          <div className="space-y-4">
            {searchResults.map((result, idx) => (
              <Card
                key={idx}
                className={`border-2 hover:shadow-xl transition-all group ${getSimilarityBg(
                  result.similarity_percent
                )}`}
              >
                <CardContent className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gold/20 text-gold font-bold text-lg">
                        {idx + 1}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white group-hover:text-gold transition-colors">
                          {result.term}
                        </h3>
                        {result.english && (
                          <p className="text-sm text-slate-light mt-1">
                            {result.english}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Similarity Badge */}
                    <div
                      className={`flex flex-col items-end ${getSimilarityColor(
                        result.similarity_percent
                      )}`}
                    >
                      <div className="text-3xl font-bold">
                        {result.similarity_percent.toFixed(1)}%
                      </div>
                      <div className="text-xs text-slate-light">유사도</div>
                    </div>
                  </div>

                  {/* Definition */}
                  <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gold/50 rounded-full"></div>
                    <p className="text-slate-light leading-relaxed pl-4 text-base">
                      {result.definition}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!searchMutation.isPending &&
        !searchMutation.error &&
        searchResults.length === 0 && (
          <Card>
            <CardContent className="p-16 text-center">
              <Search className="h-20 w-20 text-slate-dark mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-white mb-2">
                경제 용어를 검색해보세요
              </h3>
              <p className="text-slate-light">
                위 검색창에 궁금한 경제 용어를 입력하면
                <br />
                AI가 가장 관련성 높은 용어를 찾아드립니다
              </p>
            </CardContent>
          </Card>
        )}
    </div>
  )
}
