import React, { useState, useEffect } from 'react'

interface DemoBannerProps {
  className?: string
}

const DemoBanner: React.FC<DemoBannerProps> = ({ className = '' }) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const checkDemoStatus = async () => {
      try {
        const response = await fetch('/api/demo/status')
        if (response.ok) {
          const data = await response.json()
          setIsVisible(data.demo === true)
        }
      } catch (error) {
        console.error('DEMO 상태 확인 실패:', error)
        setIsVisible(false)
      }
    }

    // 초기 확인
    checkDemoStatus()

    // 30초마다 폴링
    const interval = setInterval(checkDemoStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  if (!isVisible) return null

  return (
    <div className={`bg-yellow-400 text-yellow-900 px-4 py-2 text-center font-semibold text-sm ${className}`}>
      <div className="flex items-center justify-center gap-2">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        DEMO MODE - 샘플 데이터를 사용하고 있습니다
      </div>
    </div>
  )
}

export default DemoBanner
