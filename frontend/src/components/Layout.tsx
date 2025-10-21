import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import DemoBanner from './DemoBanner'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-noir-bg">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DemoBanner />
        <Topbar />
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-2 lg:p-4 xl:p-6">
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

