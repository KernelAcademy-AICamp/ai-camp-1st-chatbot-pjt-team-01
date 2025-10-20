import { ReactNode } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card'
import Badge from './ui/Badge'

interface ChartCardProps {
  title: string
  description?: string
  source?: string
  children: ReactNode
}

export default function ChartCard({
  title,
  description,
  source,
  children,
}: ChartCardProps) {
  return (
    <Card className="hover:border-gold/30 transition-all">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            {description && (
              <CardDescription className="mt-1">{description}</CardDescription>
            )}
          </div>
          {source && (
            <Badge variant="secondary" className="text-xs">
              {source}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

