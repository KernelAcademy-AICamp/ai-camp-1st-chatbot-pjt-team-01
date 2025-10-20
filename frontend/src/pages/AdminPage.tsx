import React, { useState, useEffect } from 'react'
import { useToast } from '../components/Toast'

interface DemoStatus {
  demo: boolean
  message: string
  counts: Record<string, number | string>
  settings: {
    demo_mode: boolean
    app_name: string
    mongo_db: string
  }
}

const AdminPage: React.FC = () => {
  const [status, setStatus] = useState<DemoStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const { showSuccess, showError, ToastContainer } = useToast()

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/demo/status')
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      } else {
        throw new Error('DEMO 상태 조회 실패')
      }
    } catch (error) {
      console.error('DEMO 상태 조회 실패:', error)
      showError('DEMO 상태를 조회할 수 없습니다.')
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  const handleReset = async () => {
    if (!confirm('데이터베이스를 초기화하시겠습니까?')) return

    setLoading(true)
    try {
      const response = await fetch('/api/demo/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        showSuccess(data.message || '데이터베이스가 초기화되었습니다.')
        fetchStatus() // 상태 새로고침
      } else {
        throw new Error('초기화 실패')
      }
    } catch (error) {
      console.error('초기화 실패:', error)
      showError('데이터베이스 초기화에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleSeed = async () => {
    if (!confirm('샘플 데이터를 삽입하시겠습니까?')) return

    setLoading(true)
    try {
      const response = await fetch('/api/demo/seed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        showSuccess(data.message || '샘플 데이터가 삽입되었습니다.')
        fetchStatus() // 상태 새로고침
      } else {
        throw new Error('데이터 삽입 실패')
      }
    } catch (error) {
      console.error('데이터 삽입 실패:', error)
      showError('샘플 데이터 삽입에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  if (!status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">DEMO 상태를 확인하는 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ToastContainer />
      
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">DEMO 관리 패널</h1>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${status.demo ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {status.demo ? 'DEMO 모드 활성화' : 'DEMO 모드 비활성화'}
              </span>
            </div>
          </div>

          {/* 상태 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">시스템 정보</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">앱 이름:</span>
                  <span className="font-medium">{status.settings.app_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">데이터베이스:</span>
                  <span className="font-medium">{status.settings.mongo_db}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">DEMO 모드:</span>
                  <span className={`font-medium ${status.settings.demo_mode ? 'text-green-600' : 'text-red-600'}`}>
                    {status.settings.demo_mode ? '활성화' : '비활성화'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">데이터 통계</h3>
              <div className="space-y-2">
                {Object.entries(status.counts).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-600 capitalize">{key}:</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 관리 버튼 */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">데이터 관리</h3>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handleReset}
                disabled={loading}
                className="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold transition-colors duration-200 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    처리 중...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                    </svg>
                    Demo Reset
                  </>
                )}
              </button>

              <button
                onClick={handleSeed}
                disabled={loading}
                className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold transition-colors duration-200 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    처리 중...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Seed Sample
                  </>
                )}
              </button>

              <button
                onClick={fetchStatus}
                disabled={loading}
                className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold transition-colors duration-200 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                </svg>
                새로고침
              </button>
            </div>
          </div>

          {/* 메시지 */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">
              <strong>안내:</strong> {status.message}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminPage
