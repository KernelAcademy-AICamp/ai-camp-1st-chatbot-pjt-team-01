import { useQuery } from '@tanstack/react-query'
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { getKPIs, getTrends, getNews } from '@/lib/api'
import KpiCard from '@/components/KpiCard'
import ChartCard from '@/components/ChartCard'
import NewsCard from '@/components/NewsCard'
import ErrorDisplay from '@/components/ErrorDisplay'
import Skeleton from '@/components/ui/Skeleton'

export default function Dashboard() {
  const {
    data: kpis,
    isLoading: kpisLoading,
    error: kpisError,
    refetch: refetchKpis,
  } = useQuery({
    queryKey: ['kpis'],
    queryFn: async () => (await getKPIs()).data,
  })

  const {
    data: trends,
    isLoading: trendsLoading,
    error: trendsError,
    refetch: refetchTrends,
  } = useQuery({
    queryKey: ['trends'],
    queryFn: async () => (await getTrends()).data,
  })

  const {
    data: news,
    isLoading: newsLoading,
    error: newsError,
    refetch: refetchNews,
  } = useQuery({
    queryKey: ['news'],
    queryFn: async () => (await getNews()).data,
  })

  return (
    <div className="space-y-6 animation-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-tight font-bold mb-2">경제 대시보드</h1>
        <p className="text-slate">최신 경제 지표를 한눈에 확인하세요</p>
      </div>

      {/* KPI Cards */}
      <div>
        <h2 className="text-xl font-tight font-semibold mb-4">주요 지표</h2>
        {kpisError ? (
          <ErrorDisplay
            message="지표 데이터를 불러오지 못했습니다."
            onRetry={refetchKpis}
            compact
          />
        ) : kpisLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <KpiCard
              title="소비자물가지수"
              value={kpis.cpi}
              change={kpis.cpi_change}
              source="통계청"
              isPercentage
            />
            <KpiCard
              title="GDP 성장률 (q/q)"
              value={kpis.gdp_qoq}
              change={kpis.gdp_qoq}
              source="한국은행"
              isPercentage
            />
            <KpiCard
              title="GDP 성장률 (y/y)"
              value={kpis.gdp_yoy}
              change={kpis.gdp_yoy}
              source="한국은행"
              isPercentage
            />
            <KpiCard
              title="실업률"
              value={kpis.unemployment}
              change={kpis.unemployment_change}
              source="통계청"
              isPercentage
            />
            <KpiCard
              title="기준금리"
              value={kpis.base_rate}
              change={kpis.base_rate_change}
              source="한국은행"
              unit="%"
            />
            <KpiCard
              title="USD/KRW"
              value={kpis.usdkrw}
              change={kpis.usdkrw_change}
              source="서울외환중개"
              unit="원"
            />
            <KpiCard
              title="KOSPI"
              value={kpis.kospi}
              change={kpis.kospi_change}
              source="한국거래소"
              decimals={2}
            />
            <KpiCard
              title="S&P 500"
              value={kpis.spx}
              change={kpis.spx_change}
              source="S&P"
              decimals={2}
            />
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPI & Unemployment Trend */}
        <ChartCard
          title="물가 & 실업률 추이"
          description="최근 36개월"
          source="통계청"
        >
          {trendsError ? (
            <ErrorDisplay
              message="차트 데이터를 불러오지 못했습니다."
              onRetry={refetchTrends}
              compact
            />
          ) : trendsLoading ? (
            <Skeleton className="h-80" />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={trends.cpi_series}>
                <defs>
                  <linearGradient id="colorCpi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#C8A96A" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#C8A96A" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2225" />
                <XAxis
                  dataKey="date"
                  stroke="#64748B"
                  style={{ fontSize: '12px' }}
                />
                <YAxis stroke="#64748B" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#121416',
                    border: '1px solid #1F2225',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#94A3B8' }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#C8A96A"
                  fill="url(#colorCpi)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Base Rate & GDP */}
        <ChartCard
          title="금리 & GDP 성장률"
          description="최근 36개월"
          source="한국은행"
        >
          {trendsError ? (
            <ErrorDisplay
              message="차트 데이터를 불러오지 못했습니다."
              onRetry={refetchTrends}
              compact
            />
          ) : trendsLoading ? (
            <Skeleton className="h-80" />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={trends.rate_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2225" />
                <XAxis
                  dataKey="date"
                  stroke="#64748B"
                  style={{ fontSize: '12px' }}
                />
                <YAxis stroke="#64748B" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#121416',
                    border: '1px solid #1F2225',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#94A3B8' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#C8A96A"
                  strokeWidth={2}
                  name="기준금리"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>

      {/* News */}
      <div>
        <h2 className="text-xl font-tight font-semibold mb-4">경제 뉴스</h2>
        {newsError ? (
          <ErrorDisplay
            message="뉴스를 불러오지 못했습니다."
            onRetry={refetchNews}
            compact
          />
        ) : newsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {news.items.map((item: any, idx: number) => (
              <NewsCard
                key={idx}
                news={item}
                onClick={() => window.open(item.url, '_blank')}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

