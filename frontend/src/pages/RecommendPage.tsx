import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { BookOpen, Star, ExternalLink } from 'lucide-react'
import { getRecommendations, createBookmark, getBookmarks } from '@/lib/api'
import { RecommendItem } from '@/lib/types'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorDisplay from '@/components/ErrorDisplay'

export default function RecommendPage() {
  const [topic, setTopic] = useState('')
  const [level, setLevel] = useState<'beginner' | 'intermediate' | 'advanced'>(
    'beginner'
  )
  const [purpose, setPurpose] = useState<'report' | 'study' | 'data' | 'api'>('study')
  const [recommendations, setRecommendations] = useState<RecommendItem[]>([])

  const mutation = useMutation({
    mutationFn: () =>
      getRecommendations({
        topic,
        level,
        purpose,
      }),
    onSuccess: (response) => {
      setRecommendations(response.data.items)
    },
  })

  const bookmarkMutation = useMutation({
    mutationFn: (item: RecommendItem) =>
      createBookmark({
        title: item.title,
        url: item.url,
        tags: item.tags,
      }),
  })

  const { data: bookmarksData } = useQuery({
    queryKey: ['bookmarks'],
    queryFn: async () => (await getBookmarks()).data,
  })

  const handleSubmit = () => {
    if (!topic.trim()) return
    mutation.mutate()
  }

  const handleBookmark = (item: RecommendItem) => {
    bookmarkMutation.mutate(item)
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">자료 추천</h1>
        <p className="text-slate">학습 목적에 맞는 경제 자료를 추천받으세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Form */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2 text-gold" />
                추천 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Topic */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  주제
                </label>
                <Input
                  placeholder="예: GDP, 인플레이션, 금리"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              {/* Level */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  수준
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'beginner', label: '입문' },
                    { value: 'intermediate', label: '중급' },
                    { value: 'advanced', label: '고급' },
                  ].map((opt) => (
                    <Button
                      key={opt.value}
                      size="sm"
                      variant={level === opt.value ? 'default' : 'outline'}
                      onClick={() => setLevel(opt.value as any)}
                    >
                      {opt.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Purpose */}
              <div>
                <label className="block text-sm font-medium text-slate-light mb-2">
                  목적
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'report', label: '리포트' },
                    { value: 'study', label: '학습' },
                    { value: 'data', label: '데이터' },
                    { value: 'api', label: 'API' },
                  ].map((opt) => (
                    <Button
                      key={opt.value}
                      size="sm"
                      variant={purpose === opt.value ? 'default' : 'outline'}
                      onClick={() => setPurpose(opt.value as any)}
                    >
                      {opt.label}
                    </Button>
                  ))}
                </div>
              </div>

              <Button
                className="w-full"
                onClick={handleSubmit}
                disabled={mutation.isPending || !topic.trim()}
              >
                {mutation.isPending ? '추천 중...' : '자료 추천받기'}
              </Button>
            </CardContent>
          </Card>

          {/* Bookmarks */}
          {bookmarksData && bookmarksData.bookmarks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-base">
                  <Star className="h-4 w-4 mr-2 text-gold" />
                  즐겨찾기 ({bookmarksData.bookmarks.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {bookmarksData.bookmarks.slice(0, 5).map((bookmark: any) => (
                    <a
                      key={bookmark.id}
                      href={bookmark.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-2 rounded hover:bg-noir-bg transition-colors"
                    >
                      <p className="text-sm text-white hover:text-gold transition-colors line-clamp-1">
                        {bookmark.title}
                      </p>
                    </a>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-4">
          {mutation.isPending && <LoadingSpinner text="자료를 추천하고 있습니다..." />}

          {mutation.error && (
            <ErrorDisplay
              message={mutation.error.message}
              onRetry={handleSubmit}
            />
          )}

          {recommendations.length > 0 && (
            <>
              <h2 className="text-xl font-tight font-semibold">
                추천 자료 ({recommendations.length}개)
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.map((item, idx) => (
                  <Card
                    key={idx}
                    className="hover:border-gold/50 transition-all group"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-gold transition-colors">
                            {item.title}
                          </h3>
                          <p className="text-sm text-slate-light mb-3 line-clamp-3">
                            {item.summary}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 mb-3">
                        {item.tags.map((tag, tagIdx) => (
                          <Badge key={tagIdx} variant="secondary">
                            {tag}
                          </Badge>
                        ))}
                      </div>

                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1"
                          onClick={() => window.open(item.url, '_blank')}
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          바로가기
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleBookmark(item)}
                          disabled={bookmarkMutation.isPending}
                        >
                          <Star
                            className={`h-4 w-4 ${
                              bookmarkMutation.isSuccess
                                ? 'fill-gold text-gold'
                                : ''
                            }`}
                          />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}

          {!mutation.isPending &&
            !mutation.error &&
            recommendations.length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <BookOpen className="h-16 w-16 text-slate-dark mx-auto mb-4" />
                  <p className="text-slate">
                    주제를 입력하고 "자료 추천받기"를 클릭하세요
                  </p>
                </CardContent>
              </Card>
            )}
        </div>
      </div>
    </div>
  )
}

