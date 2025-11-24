'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Loader, AlertCircle } from 'lucide-react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { getSensorData, getMaintenanceOrders, getParetoFront, loadEquipmentList } from '@/lib/api'

export default function DataPage() {
  const [activeTab, setActiveTab] = useState<'sensor' | 'orders' | 'pareto'>('sensor')
  const [loading, setLoading] = useState(false)
  const [loadingEquipment, setLoadingEquipment] = useState(false)
  const [data, setData] = useState<any>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [paretoEquipment, setParetoEquipment] = useState('')
  const [equipmentList, setEquipmentList] = useState<any[]>([])

  const loadSensorData = async () => {
    setLoading(true)
    setMessage(null)
    try {
      const result = await getSensorData(50)
      setData(result)
      if (!result.data || result.data.length === 0) {
        setMessage('Nenhum dado de sensor encontrado.')
      }
    } catch (error) {
      setMessage(`Erro ao carregar dados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  const loadOrders = async () => {
    setLoading(true)
    setMessage(null)
    try {
      const result = await getMaintenanceOrders()
      setData(result)
      if (!result.orders || result.orders.length === 0) {
        setMessage('Nenhuma ordem de serviço encontrada.')
      }
    } catch (error) {
      setMessage(`Erro ao carregar ordens: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  const loadEquipment = async () => {
    setLoadingEquipment(true)
    try {
      const result = await loadEquipmentList()
      setEquipmentList(result.equipment || [])
      if (!result.equipment || result.equipment.length === 0) {
        setMessage('Nenhum equipamento encontrado no banco de dados.')
      }
    } catch (error) {
      setMessage(`Erro ao carregar equipamentos: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoadingEquipment(false)
    }
  }

  const loadPareto = async () => {
    if (!paretoEquipment.trim()) {
      setMessage('Por favor, selecione um equipamento.')
      return
    }

    setLoading(true)
    setMessage(null)
    try {
      const result = await getParetoFront(paretoEquipment)
      setData(result)
      if (!result.pareto_points || result.pareto_points.length === 0) {
        setMessage('Nenhum ponto de Pareto encontrado para este equipamento.')
      }
    } catch (error) {
      setMessage(`Erro ao carregar Pareto: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'sensor') {
      loadSensorData()
    } else if (activeTab === 'orders') {
      loadOrders()
    } else if (activeTab === 'pareto') {
      loadEquipment()
    }
  }, [activeTab])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">📈 Visualização de Dados</h1>
        <p className="text-muted-foreground">
          Consulte dados de sensores, ordens de serviço e fronteira de Pareto
        </p>
      </div>

      <div className="flex gap-3 flex-wrap">
        <Button
          variant={activeTab === 'sensor' ? 'default' : 'outline'}
          onClick={() => setActiveTab('sensor')}
        >
          Dados de Sensores
        </Button>
        <Button
          variant={activeTab === 'orders' ? 'default' : 'outline'}
          onClick={() => setActiveTab('orders')}
        >
          Ordens de Serviço
        </Button>
        <Button
          variant={activeTab === 'pareto' ? 'default' : 'outline'}
          onClick={() => setActiveTab('pareto')}
        >
          Fronteira de Pareto
        </Button>
      </div>

      {message && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {activeTab === 'sensor' && (
        <Card>
          <CardHeader>
            <CardTitle>Dados de Sensores</CardTitle>
            <CardDescription>Últimos 50 registros de sensores</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={loadSensorData} disabled={loading} variant="outline" className="mb-4">
              {loading ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Carregando...
                </>
              ) : (
                '🔄 Recarregar'
              )}
            </Button>

            {data?.data && data.data.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-2">Timestamp</th>
                      <th className="text-left py-2 px-2">Equipamento</th>
                      <th className="text-right py-2 px-2">Corrente (mA)</th>
                      <th className="text-right py-2 px-2">TG Delta (%)</th>
                      <th className="text-right py-2 px-2">Capacitância (pF)</th>
                      <th className="text-left py-2 px-2">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.data.map((row: any, idx: number) => (
                      <tr key={idx} className="border-b hover:bg-muted/50">
                        <td className="py-2 px-2 text-xs">{new Date(row.timestamp).toLocaleString('pt-BR')}</td>
                        <td className="py-2 px-2 font-medium">{row.equipment_id}</td>
                        <td className="py-2 px-2 text-right">{row.corrente_fuga?.toFixed(4)}</td>
                        <td className="py-2 px-2 text-right">{row.tg_delta?.toFixed(4)}</td>
                        <td className="py-2 px-2 text-right">{row.capacitancia?.toFixed(2)}</td>
                        <td className="py-2 px-2">{row.estado_saude || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'orders' && (
        <Card>
          <CardHeader>
            <CardTitle>Ordens de Serviço</CardTitle>
            <CardDescription>Todas as ordens de serviço registradas</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={loadOrders} disabled={loading} variant="outline" className="mb-4">
              {loading ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Carregando...
                </>
              ) : (
                '🔄 Recarregar'
              )}
            </Button>

            {data?.orders && data.orders.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-2">OS ID</th>
                      <th className="text-left py-2 px-2">Equipamento</th>
                      <th className="text-left py-2 px-2">Localização</th>
                      <th className="text-left py-2 px-2">Estado</th>
                      <th className="text-left py-2 px-2">Data Medição</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.orders.map((order: any, idx: number) => (
                      <tr key={idx} className="border-b hover:bg-muted/50">
                        <td className="py-2 px-2 font-medium">{order.os_id}</td>
                        <td className="py-2 px-2">{order.equipment_id}</td>
                        <td className="py-2 px-2">{order.localizacao}</td>
                        <td className="py-2 px-2">{order.mf_dga || 'N/A'}</td>
                        <td className="py-2 px-2 text-xs">{new Date(order.mf_dga_data).toLocaleString('pt-BR')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'pareto' && (
        <Card>
          <CardHeader>
            <CardTitle>Fronteira de Pareto</CardTitle>
            <CardDescription>Trade-off entre Custo e Indisponibilidade</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="equipment-select">Selecione um Equipamento</Label>
              <div className="flex gap-2">
                <Select
                  value={paretoEquipment}
                  onValueChange={setParetoEquipment}
                  disabled={loadingEquipment || equipmentList.length === 0}
                >
                  <SelectTrigger id="equipment-select" className="flex-1">
                    <SelectValue placeholder={loadingEquipment ? 'Carregando equipamentos...' : 'Selecione um equipamento'} />
                  </SelectTrigger>
                  <SelectContent>
                    {equipmentList.map((eq) => (
                      <SelectItem key={eq.equipment_id} value={eq.equipment_id}>
                        {eq.equipment_id} ({eq.localizacao})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  onClick={loadPareto}
                  disabled={loading || !paretoEquipment}
                  className="flex-shrink-0"
                >
                  {loading ? (
                    <>
                      <Loader className="mr-2 h-4 w-4 animate-spin" />
                      Carregando...
                    </>
                  ) : (
                    'Buscar'
                  )}
                </Button>
              </div>
              {equipmentList.length === 0 && !loadingEquipment && (
                <p className="text-sm text-muted-foreground">
                  Nenhum equipamento disponível. Gere dados primeiro.
                </p>
              )}
            </div>

            {data?.pareto_points && data.pareto_points.length > 0 && (
              <div className="space-y-6">
                {/* Pareto Frontier Scatter Chart */}
                <div className="w-full h-80 bg-muted/30 rounded-lg p-4">
                  <h3 className="text-sm font-semibold mb-4">Fronteira de Pareto - Custo vs Indisponibilidade</h3>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="custo" type="number" name="Custo (R$)" />
                      <YAxis dataKey="indisponibilidade" type="number" name="Indisponibilidade" />
                      <Tooltip
                        cursor={{ strokeDasharray: '3 3' }}
                        contentStyle={{ backgroundColor: '#f0f0f0', border: '1px solid #ccc' }}
                        formatter={(value: any) => {
                          if (typeof value === 'number') {
                            return value > 100 ? `R$ ${value.toFixed(2)}` : value.toFixed(6)
                          }
                          return value
                        }}
                      />
                      <Legend />
                      <Scatter
                        name="Pontos de Pareto"
                        data={data.pareto_points}
                        fill="#8884d8"
                        shape="circle"
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>

                {/* Time vs Cost Line Chart */}
                <div className="w-full h-80 bg-muted/30 rounded-lg p-4">
                  <h3 className="text-sm font-semibold mb-4">Custo ao Longo do Tempo</h3>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.pareto_points}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="t_days"
                        label={{ value: 'Tempo (dias)', position: 'insideBottomRight', offset: -5 }}
                      />
                      <YAxis
                        label={{ value: 'Custo (R$)', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip
                        formatter={(value: any) => {
                          if (typeof value === 'number' && value > 100) {
                            return `R$ ${value.toFixed(2)}`
                          }
                          return value
                        }}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="custo"
                        stroke="#82ca9d"
                        name="Custo (R$)"
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Data Table */}
                <div className="overflow-x-auto">
                  <h3 className="text-sm font-semibold mb-4">Dados Detalhados</h3>
                  <table className="w-full text-sm">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left py-2 px-2">Tempo (dias)</th>
                        <th className="text-right py-2 px-2">Custo (R$)</th>
                        <th className="text-right py-2 px-2">Indisponibilidade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.pareto_points.map((point: any, idx: number) => (
                        <tr key={idx} className="border-b hover:bg-muted/50">
                          <td className="py-2 px-2">{point.t_days}</td>
                          <td className="py-2 px-2 text-right">R$ {point.custo?.toFixed(2)}</td>
                          <td className="py-2 px-2 text-right">{point.indisponibilidade?.toFixed(6)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
