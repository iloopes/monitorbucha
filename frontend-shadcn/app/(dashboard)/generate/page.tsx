'use client'

import { useState } from 'react'
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
import { generateSyntheticData } from '@/lib/api'

export default function GeneratePage() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)
  const [results, setResults] = useState<any>(null)
  const [formData, setFormData] = useState({
    n_bushings: 10,
    days: 30,
    frequency_hours: 1,
    degradation_rate: 'medium',
    save_to_database: true,
    scenario_name: '',
  })

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
      const response = await generateSyntheticData({
        n_bushings: formData.n_bushings,
        days: formData.days,
        frequency_hours: formData.frequency_hours,
        degradation_rate: formData.degradation_rate,
        save_to_database: formData.save_to_database,
        scenario_name: formData.scenario_name || null,
      })

      setMessage({
        type: 'success',
        text: '✓ Dados gerados com sucesso!',
      })
      setResults(response)
    } catch (error) {
      setMessage({
        type: 'error',
        text: `✗ Erro ao gerar dados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Gerar Dados Sintéticos</h1>
        <p className="text-muted-foreground">
          Crie dados de teste para simulação e análise
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Parâmetros de Geração</CardTitle>
          <CardDescription>
            Configure os parâmetros para gerar dados sintéticos de buchas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="bushings">Número de Buchas</Label>
                <Input
                  id="bushings"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.n_bushings}
                  onChange={(e) => handleInputChange('n_bushings', parseInt(e.target.value))}
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="days">Período (dias)</Label>
                <Input
                  id="days"
                  type="number"
                  min="1"
                  max="365"
                  value={formData.days}
                  onChange={(e) => handleInputChange('days', parseInt(e.target.value))}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="frequency">Frequência (horas)</Label>
                <Input
                  id="frequency"
                  type="number"
                  min="1"
                  max="24"
                  value={formData.frequency_hours}
                  onChange={(e) => handleInputChange('frequency_hours', parseInt(e.target.value))}
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="degradation">Taxa de Degradação</Label>
                <Select
                  value={formData.degradation_rate}
                  onValueChange={(value) => handleInputChange('degradation_rate', value)}
                  disabled={loading}
                >
                  <SelectTrigger id="degradation">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Baixa</SelectItem>
                    <SelectItem value="medium">Média</SelectItem>
                    <SelectItem value="high">Alta</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="scenario">Nome do Cenário (opcional)</Label>
              <Input
                id="scenario"
                value={formData.scenario_name}
                onChange={(e) => handleInputChange('scenario_name', e.target.value)}
                placeholder="Ex: cenario_teste_01"
                disabled={loading}
              />
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
                Salvar no Banco de Dados
              </Label>
            </div>

            <Button type="submit" disabled={loading} size="lg" className="w-full">
              {loading ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Gerando dados... Por favor aguarde
                </>
              ) : (
                '🚀 Gerar Dados'
              )}
            </Button>
          </form>

          {message && (
            <Alert className={`mt-6 ${message.type === 'success' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
              {message.type === 'success' ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <AlertTitle className={message.type === 'success' ? 'text-green-900' : 'text-red-900'}>
                {message.type === 'success' ? 'Sucesso' : 'Erro'}
              </AlertTitle>
              <AlertDescription className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
                {message.text}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Resultados da Geração</CardTitle>
            <CardDescription>
              Estatísticas dos dados gerados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Cenário</p>
                <p className="text-lg font-semibold">{results.scenario_name}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-muted-foreground">Número de Buchas</p>
                <p className="text-lg font-semibold">{results.statistics?.n_bushings}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-muted-foreground">Período</p>
                <p className="text-lg font-semibold">{results.statistics?.days} dias</p>
              </div>

              <div>
                <p className="text-sm font-medium text-muted-foreground">Registros de Sensores</p>
                <p className="text-lg font-semibold">{results.statistics?.sensor_records}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-muted-foreground">Ordens de Serviço</p>
                <p className="text-lg font-semibold">{results.statistics?.maintenance_orders}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-muted-foreground">Status do Banco</p>
                <p className="text-lg font-semibold">
                  {results.database?.status === 'success' ? '✓ Salvo' : '⚠️ Não salvo'}
                </p>
              </div>
            </div>

            {results.database?.status === 'success' && (
              <div className="mt-4 space-y-2 text-sm">
                <p>
                  <strong>Sensores Inseridos:</strong> {results.database?.sensor_records_inserted}
                </p>
                <p>
                  <strong>Ordens Inseridas:</strong> {results.database?.orders_inserted}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
