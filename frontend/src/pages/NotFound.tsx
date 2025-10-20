import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'
import Button from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <Card className="max-w-md w-full">
        <CardContent className="p-12 text-center">
          <div className="text-6xl font-tight font-bold text-gold mb-4">404</div>
          <h1 className="text-2xl font-tight font-bold mb-2">
            페이지를 찾을 수 없습니다
          </h1>
          <p className="text-slate mb-6">
            요청하신 페이지가 존재하지 않거나 이동되었습니다.
          </p>
          <div className="flex items-center justify-center space-x-3">
            <Button variant="outline" onClick={() => window.history.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              뒤로 가기
            </Button>
            <Link to="/">
              <Button>
                <Home className="h-4 w-4 mr-2" />
                홈으로
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

