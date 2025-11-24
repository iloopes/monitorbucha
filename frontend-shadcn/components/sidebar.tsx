'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  BarChart3,
  Database,
  Zap,
  Calendar,
  Eye,
  Settings,
  Home,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const menuItems = [
  { href: '/', label: 'Dashboard', icon: Home },
  { href: '/database', label: 'Banco de Dados', icon: Database },
  { href: '/generate', label: 'Gerar Dados', icon: Zap },
  { href: '/optimize', label: 'Otimizar', icon: BarChart3 },
  { href: '/calendar', label: 'Calendário', icon: Calendar },
  { href: '/data', label: 'Visualizar Dados', icon: Eye },
  { href: '/settings', label: 'Configurações', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r bg-card">
      <div className="space-y-4 py-4">
        <div className="px-4 py-2">
          <h2 className="text-lg font-semibold">Sistema de Manutenção</h2>
          <p className="text-xs text-muted-foreground">Preditiva 2.0</p>
        </div>

        <nav className="space-y-2 px-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}
