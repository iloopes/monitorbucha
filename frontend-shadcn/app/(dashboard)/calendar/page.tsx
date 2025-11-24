'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader, AlertCircle } from 'lucide-react'
import { loadMaintenanceCalendar } from '@/lib/api'

export default function CalendarPage() {
  const [loading, setLoading] = useState(true)
  const [calendar, setCalendar] = useState<any[]>([])
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    loadCalendar()
  }, [])

  const loadCalendar = async () => {
    setLoading(true)
    try {
      const data = await loadMaintenanceCalendar()
      setCalendar(data.calendar || [])
      if (!data.calendar || data.calendar.length === 0) {
        setMessage('Nenhuma manutenção programada. Execute a otimização primeiro.')
      }
    } catch (error) {
      setMessage(`Erro ao carregar calendário: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'urgente':
        return 'border-l-4 border-l-red-500 bg-red-50'
      case 'proxima':
        return 'border-l-4 border-l-yellow-500 bg-yellow-50'
      case 'programada':
        return 'border-l-4 border-l-green-500 bg-green-50'
      case 'atrasado':
        return 'border-l-4 border-l-red-800 bg-red-100'
      default:
        return 'border-l-4 border-l-gray-500 bg-gray-50'
    }
  }

  const getUrgencyBadgeColor = (urgency: string) => {
    switch (urgency) {
      case 'urgente':
        return 'bg-red-500 text-white'
      case 'proxima':
        return 'bg-yellow-500 text-white'
      case 'programada':
        return 'bg-green-500 text-white'
      case 'atrasado':
        return 'bg-red-800 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">📅 Calendário de Manutenção</h1>
        <p className="text-muted-foreground">
          Visualize as manutenções programadas ordenadas por prioridade
        </p>
      </div>

      <div className="flex gap-3">
        <Button onClick={loadCalendar} disabled={loading} variant="outline">
          {loading ? (
            <>
              <Loader className="mr-2 h-4 w-4 animate-spin" />
              Carregando...
            </>
          ) : (
            '🔄 Atualizar Calendário'
          )}
        </Button>
      </div>

      {message && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {calendar.length > 0 && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{calendar.length} Manutenções Programadas</CardTitle>
              <CardDescription>
                Ordenadas por prioridade e data
              </CardDescription>
            </CardHeader>
          </Card>

          <div className="grid gap-4">
            {calendar.map((item, idx) => {
              const dataFormatada = new Date(item.data_otima).toLocaleDateString('pt-BR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })

              return (
                <Card key={idx} className={getUrgencyColor(item.urgencia || 'programada')}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-bold">{item.equipment_id}</h3>
                        <p className="text-sm text-muted-foreground">{item.localizacao}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${getUrgencyBadgeColor(item.urgencia || 'programada')}`}>
                        {item.urgencia || 'programada'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6 text-sm">
                      <div>
                        <p className="text-muted-foreground font-medium">📅 Data</p>
                        <p className="font-semibold">{dataFormatada}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground font-medium">⏱️ Dias</p>
                        <p className="font-semibold">{item.dias_ate_manutencao} dias</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground font-medium">🔧 Estado</p>
                        <p className="font-semibold">{item.estado_atual || 'N/A'}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground font-medium">💰 Custo</p>
                        <p className="font-semibold">R$ {item.custo?.toFixed(2) || 'N/A'}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground font-medium">⚠️ Prioridade</p>
                        <p className="font-semibold">{item.prioridade || 'N/A'}</p>
                      </div>

                      <div>
                        <p className="text-muted-foreground font-medium">📊 Indisponibilidade</p>
                        <p className="font-semibold">{item.indisponibilidade?.toFixed(4) || 'N/A'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
