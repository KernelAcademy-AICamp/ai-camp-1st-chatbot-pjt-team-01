import { Link, useLocation } from 'react-router-dom'
import { Home, MessageSquare, BookOpen, TrendingUp, FileText, Archive, PlayCircle, History, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState, useEffect } from 'react'

const baseNavigation = [
  { name: '최신 경제 대시보드', href: '/', icon: Home },
  { name: '요약/Q&A', href: '/qa', icon: MessageSquare },
  { name: '자료 추천', href: '/recommend', icon: BookOpen },
  { name: '문제 생성', href: '/problems', icon: FileText },
  { name: '문제 풀기', href: '/problems/quiz', icon: PlayCircle },
  { name: '문제 보관함', href: '/problems/history', icon: Archive },
  { name: '내 퀴즈 기록', href: '/my-attempts', icon: History },
]

const adminNavigation = [
  { name: 'Admin(데모)', href: '/admin', icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()
  const [isDemoMode, setIsDemoMode] = useState(false)

  useEffect(() => {
    const checkDemoStatus = async () => {
      try {
        const response = await fetch('/api/demo/status')
        if (response.ok) {
          const data = await response.json()
          setIsDemoMode(data.demo === true)
        }
      } catch (error) {
        console.error('DEMO 상태 확인 실패:', error)
        setIsDemoMode(false)
      }
    }

    checkDemoStatus()
    // 30초마다 폴링
    const interval = setInterval(checkDemoStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const navigation = isDemoMode 
    ? [...baseNavigation, ...adminNavigation]
    : baseNavigation

  return (
    <div className="w-64 bg-noir-card border-r border-noir-border flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-noir-border">
        <TrendingUp className="h-6 w-6 text-gold mr-3" />
        <h1 className="text-lg font-tight font-bold text-white tracking-tight">
          Noir Luxe
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-all',
                isActive
                  ? 'bg-gold text-noir-bg'
                  : 'text-slate-light hover:bg-noir-bg hover:text-white'
              )}
            >
              <Icon className="h-5 w-5 mr-3" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-noir-border">
        <p className="text-xs text-slate-dark text-center">
          © 2024 Noir Luxe Economy
        </p>
      </div>
    </div>
  )
}

