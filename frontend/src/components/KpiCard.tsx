import { ArrowUp, ArrowDown, TrendingUp } from 'lucide-react'
import { Card, CardContent } from './ui/Card'
import { cn, formatNumber, formatPct } from '@/lib/utils'
import Badge from './ui/Badge'

interface KpiCardProps {
  title: string
  value: number
  change: number
  unit?: string
  source?: string
  decimals?: number
  isPercentage?: boolean
}

export default function KpiCard({
  title,
  value,
  change,
  unit = '',
  source = '출처',
  decimals = 2,
  isPercentage = false,
}: KpiCardProps) {
  const isPositive = change > 0
  const isNegative = change < 0

  const formattedValue = isPercentage
    ? `${formatNumber(value, decimals)}%`
    : `${formatNumber(value, decimals)}${unit}`

  return (
    <Card className="relative overflow-hidden hover:border-gold/30 transition-all group">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-gold" />
            <h3 className="text-sm font-medium text-slate-light">{title}</h3>
          </div>
          {source && (
            <Badge variant="secondary" className="text-xs">
              {source}
            </Badge>
          )}
        </div>

        <div className="space-y-2">
          <div className="text-3xl font-tight font-bold text-white tracking-tight">
            {formattedValue}
          </div>

          <div className="flex items-center space-x-2">
            {isPositive && (
              <>
                <ArrowUp className="h-4 w-4 text-green-400" />
                <span className="text-sm font-medium text-green-400">
                  {formatPct(change, decimals)}
                </span>
              </>
            )}
            {isNegative && (
              <>
                <ArrowDown className="h-4 w-4 text-red-400" />
                <span className="text-sm font-medium text-red-400">
                  {formatPct(change, decimals)}
                </span>
              </>
            )}
            {!isPositive && !isNegative && (
              <span className="text-sm text-slate">변동 없음</span>
            )}
            <span className="text-xs text-slate-dark">전월 대비</span>
          </div>
        </div>

        {/* Hover effect */}
        <div
          className={cn(
            'absolute inset-0 bg-gradient-to-br from-gold/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none'
          )}
        />
      </CardContent>
    </Card>
  )
}

