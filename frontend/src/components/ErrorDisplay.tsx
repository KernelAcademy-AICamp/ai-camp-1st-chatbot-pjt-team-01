import { AlertCircle, RefreshCw } from 'lucide-react'
import Button from './ui/Button'
import { Card, CardContent } from './ui/Card'

interface ErrorDisplayProps {
  message?: string
  onRetry?: () => void
  compact?: boolean
}

export default function ErrorDisplay({
  message = '데이터를 불러오지 못했어요.',
  onRetry,
  compact = false,
}: ErrorDisplayProps) {
  if (compact) {
    return (
      <div className="flex items-center justify-between p-4 rounded-md border border-red-500/20 bg-red-500/5">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <p className="text-sm text-red-400">{message}</p>
        </div>
        {onRetry && (
          <Button size="sm" variant="outline" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-1" />
            다시 시도
          </Button>
        )}
      </div>
    )
  }

  return (
    <Card className="border-red-500/20 bg-red-500/5">
      <CardContent className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">
          오류가 발생했습니다
        </h3>
        <p className="text-sm text-red-400 mb-4">{message}</p>
        {onRetry && (
          <Button onClick={onRetry}>
            <RefreshCw className="h-4 w-4 mr-2" />
            다시 시도할까요?
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

