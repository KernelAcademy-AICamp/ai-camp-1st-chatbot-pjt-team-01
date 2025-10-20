import { Search, Bell, User } from 'lucide-react'
import Button from './ui/Button'

export default function Topbar() {
  return (
    <div className="h-16 border-b border-noir-border bg-noir-card flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-dark" />
          <input
            type="text"
            placeholder="검색... (⌘K)"
            className="w-full h-10 pl-10 pr-4 rounded-md border border-noir-border bg-noir-bg text-sm text-white placeholder:text-slate-dark focus:outline-none focus:ring-2 focus:ring-gold"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-3 ml-6">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-gold rounded-full" />
        </Button>
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
}

