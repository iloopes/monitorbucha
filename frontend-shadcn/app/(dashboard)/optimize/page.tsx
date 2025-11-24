'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { runOptimization, loadEquipmentList } from '@/lib/api'

export default function OptimizePage() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)
  const [results, setResults] = useState<any>(null)
  const [equipment, setEquipment] = useState<any[]>([])
  const [loadingEquipment, setLoadingEquipment] = useState(true)

  const [formData, setFormData] = useState({
    max_evaluations: 4000,
    population_size: 200,
    save_to_database: true,
    equipment_id: 'all',
  })

  useEffect(() => {
    const loadEquipment = async () => {
      try {
        const data = await loadEquipmentList()
        setEquipment(data.equipment || [])
      } catch (error) {
        setMessage({
          type: 'info',
          text: 'Nenhum equipamento encontrado. Gere dados primeiro.',
        })
      } finally {
        setLoadingEquipment(false)
      }
    }

    loadEquipment()
  }, [])

  const handleInputChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)
    setResults(null)

    try {
      const response = await runOptimization({
        max_evaluations: formData.max_evaluations,
        population_size: formData.population_size,
        save_to_database: formData.save_to_database,
        equipment_ids: formData.equipment_id === 'all' ? null : [formData.equipment_id],
      })

      setMessage({
        type: 'success',
        text: `✓ Otimização concluída com sucesso!\n📊 Equipamentos: ${response.summary?.total_optimized}\nCusto médio: R$ ${response.summary?.avg_cost?.toFixed(2)}\nPontos Pareto: ${response.summary?.total_pareto_points}`,
      })
      setResults(response)
    } catch (error) {
      setMessage({
        type: 'error',
        text: `✗ Erro ao executar otimização: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Otimização de Manutenção</h1>
        <p className="text-muted-foreground">
          Execute algoritmos de otimização (Markov + NSGA-II)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Parâmetros de Otimização</CardTitle>
          <CardDescription>
            Configure os parâmetros do algoritmo genético NSGA-II
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="equipment">Equipamento(s) para Otimizar</Label>
              <Select
                value={formData.equipment_id}
                onValueChange={(value) => handleInputChange('equipment_id', value)}
                disabled={loadingEquipment || loading}
              >
                <SelectTrigger id="equipment">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">🔄 Todos os Equipamentos</SelectItem>
                  {equipment.map((eq) => (
                    <SelectItem key={eq.equipment_id} value={eq.equipment_id}>
                      {eq.equipment_id} ({eq.localizacao})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="max-eval">Máximo de Avaliações</Label>
                <Input
                  id="max-eval"
                  type="number"
                  min="1000"
                  max="10000"
                  value={formData.max_evaluations}
                  onChange={(e) => handleInputChange('max_evaluations', parseInt(e.target.value))}
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="population">Tamanho da População</Label>
                <Input
                  id="population"
                  type="number"
                  min="50"
                  max="500"
                  value={formData.population_size}
                  onChange={(e) => handleInputChange('population_size', parseInt(e.target.value))}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="save-db"
                checked={formData.save_to_database}
                onCheckedChange={(checked) =>
                  handleInputChange('save_to_database', checked as boolean)
                }
                disabled={loading}
              />
              <Label htmlFor="save-db" className="cursor-pointer">
                Salvar Resultados no Banco de Dados
              </Label>
            </div>

            <Button type="submit" disabled={loading} size="lg" className="w-full">
              {loading ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Executando otimização... Por favor aguarde
                </>
              ) : (
                '⚡ Executar Otimização'
              )}
            </Button>
          </form>

          {message && (
            <Alert className={`mt-6 ${message.type === 'success' ? 'border-green-500 bg-green-50' : message.type === 'error' ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'}`}>
              {message.type === 'success' ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <AlertTitle className={message.type === 'success' ? 'text-green-900' : message.type === 'error' ? 'text-red-900' : 'text-blue-900'}>
                {message.type === 'success' ? 'Sucesso' : message.type === 'error' ? 'Erro' : 'Informação'}
              </AlertTitle>
              <AlertDescription className={message.type === 'success' ? 'text-green-800' : message.type === 'error' ? 'text-red-800' : 'text-blue-800'}>
                {message.text}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Resumo dos Resultados</CardTitle>
            <CardDescription>
              Estatísticas da otimização realizada
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2 rounded-lg bg-blue-50 p-4">
                <p className="text-sm font-medium text-muted-foreground">Equipamentos Otimizados</p>
                <p className="text-2xl font-bold">{results.summary?.total_optimized}</p>
              </div>

              <div className="space-y-2 rounded-lg bg-green-50 p-4">
                <p className="text-sm font-medium text-muted-foreground">Custo Médio</p>
                <p className="text-2xl font-bold">R$ {results.summary?.avg_cost?.toFixed(2)}</p>
              </div>

              <div className="space-y-2 rounded-lg bg-purple-50 p-4">
                <p className="text-sm font-medium text-muted-foreground">Pontos Pareto</p>
                <p className="text-2xl font-bold">{results.summary?.total_pareto_points}</p>
              </div>
            </div>

            {results.results && results.results.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Top 10 Equipamentos por Prioridade</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left py-2">Equipamento</th>
                        <th className="text-left py-2">Localização</th>
                        <th className="text-left py-2">Data Ótima</th>
                        <th className="text-right py-2">Custo</th>
                        <th className="text-center py-2">Prioridade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.results.slice(0, 10).map((item: any, idx: number) => (
                        <tr key={idx} className="border-b hover:bg-muted/50">
                          <td className="py-2 font-medium">{item.equipment_id}</td>
                          <td className="py-2">{item.localizacao}</td>
                          <td className="py-2">{new Date(item.data_otima).toLocaleDateString('pt-BR')}</td>
                          <td className="text-right py-2">R$ {item.custo?.toFixed(2)}</td>
                          <td className="text-center py-2">
                            <span className={`inline-block px-2 py-1 rounded text-white text-xs font-semibold ${item.prioridade >= 3 ? 'bg-red-500' : 'bg-green-500'}`}>
                              {item.prioridade}
                            </span>
                          </td>
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
