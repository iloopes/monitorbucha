'use client'

import { useEffect, useState } from 'react'
import { checkAPIHealth } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, CheckCircle } from 'lucide-react'

export function Header() {
  const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading')
  const [version, setVersion] = useState<string>('')

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await checkAPIHealth()
        if (data.status === 'healthy') {
          setStatus('online')
          setVersion(data.version)
        } else {
          setStatus('offline')
        }
      } catch (error) {
        setStatus('offline')
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <header className="border-b bg-card">
      <div className="flex h-16 items-center justify-between px-6">
        <div>
          <h1 className="text-2xl font-bold">🔌 Sistema de Manutenção Preditiva</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {status === 'online' ? (
              <>
                <CheckCircle className="h-5 w-5 text-green-500" />
                <Badge variant="default" className="bg-green-500">
                  Online v{version}
                </Badge>
              </>
            ) : (
              <>
                <AlertCircle className="h-5 w-5 text-red-500" />
                <Badge variant="destructive">Offline</Badge>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
