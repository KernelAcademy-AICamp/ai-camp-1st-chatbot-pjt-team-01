import { ExternalLink, Calendar } from 'lucide-react'
import { Card, CardContent } from './ui/Card'
import Badge from './ui/Badge'
import { formatDate } from '@/lib/utils'
import { NewsItem } from '@/lib/types'

interface NewsCardProps {
  news: NewsItem
  onClick?: () => void
}

export default function NewsCard({ news, onClick }: NewsCardProps) {
  return (
    <Card
      className="hover:border-gold/50 transition-all cursor-pointer group"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <Badge variant="outline" className="text-xs">
            {news.source}
          </Badge>
          <ExternalLink className="h-4 w-4 text-slate-dark group-hover:text-gold transition-colors" />
        </div>

        <h3 className="text-base font-semibold text-white mb-2 group-hover:text-gold transition-colors line-clamp-2">
          {news.title}
        </h3>

        <p className="text-sm text-slate-light mb-3 line-clamp-2">
          {news.summary}
        </p>

        <div className="flex items-center text-xs text-slate-dark">
          <Calendar className="h-3 w-3 mr-1" />
          {formatDate(news.published_at)}
        </div>
      </CardContent>
    </Card>
  )
}

