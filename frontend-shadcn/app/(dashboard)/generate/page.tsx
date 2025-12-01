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
    enable_anomalies: false,
    anomaly_rate: 5,
    anomaly_type: 'spike',
    randomize_anomaly_types: false,
    anomaly_type_list: ['spike', 'drift', 'noise', 'shift'],
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
        anomaly_rate: formData.enable_anomalies ? formData.anomaly_rate : null,
        anomaly_type: formData.anomaly_type,
        anomaly_equipments: null, // Could be expanded for specific equipment selection
        randomize_anomaly_types: formData.randomize_anomaly_types,
        anomaly_type_list: formData.randomize_anomaly_types ? formData.anomaly_type_list : null,
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

            <div className="border-t pt-4 mt-4">
              <div className="flex items-center space-x-2 mb-4">
                <Checkbox
                  id="enable-anomalies"
                  checked={formData.enable_anomalies}
                  onCheckedChange={(checked) =>
                    handleInputChange('enable_anomalies', checked as boolean)
                  }
                  disabled={loading}
                />
                <Label htmlFor="enable-anomalies" className="cursor-pointer font-semibold">
                  🚨 Injetar Anomalias (para testes)
                </Label>
              </div>

              {formData.enable_anomalies && (
                <div className="space-y-4 bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <div className="space-y-2">
                    <Label htmlFor="anomaly-rate">Taxa de Anomalias (%)</Label>
                    <div className="flex items-center space-x-2">
                      <Input
                        id="anomaly-rate"
                        type="number"
                        min="1"
                        max="50"
                        value={formData.anomaly_rate}
                        onChange={(e) => handleInputChange('anomaly_rate', parseInt(e.target.value))}
                        disabled={loading}
                      />
                      <span className="text-sm text-muted-foreground">{formData.anomaly_rate}% dos dados</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="randomize-types"
                      checked={formData.randomize_anomaly_types}
                      onCheckedChange={(checked) =>
                        handleInputChange('randomize_anomaly_types', checked as boolean)
                      }
                      disabled={loading}
                    />
                    <Label htmlFor="randomize-types" className="cursor-pointer text-sm">
                      Aleatorizar Tipos de Anomalias
                    </Label>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="anomaly-type">
                      {formData.randomize_anomaly_types ? 'Tipo de Anomalia (ignorado - tipos aleatorizados)' : 'Tipo de Anomalia'}
                    </Label>
                    <Select
                      value={formData.anomaly_type}
                      onValueChange={(value) => handleInputChange('anomaly_type', value)}
                      disabled={loading || formData.randomize_anomaly_types}
                    >
                      <SelectTrigger id="anomaly-type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="spike">Pico (Spike) - Aumento súbito de 2.5-3.5x</SelectItem>
                        <SelectItem value="drift">Desvio (Drift) - Aumento gradual de 1.5-2.0x</SelectItem>
                        <SelectItem value="noise">Ruído (Noise) - Aumento de variação</SelectItem>
                        <SelectItem value="shift">Mudança (Shift) - Aumento permanente</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <p className="text-xs text-muted-foreground italic">
                    ℹ️ Anomalias injetadas serão marcadas com eventos "SPIKE_ANOMALICO", "DRIFT_ANOMALICO", etc.
                    {formData.randomize_anomaly_types && ' Tipos aleatorizados entre: spike, drift, noise, shift'}
                  </p>
                </div>
              )}
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

            {results.anomalies && (
              <div className="mt-6 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-sm font-semibold text-orange-900 mb-2">🚨 Anomalias Injetadas</p>
                <div className="space-y-2 text-sm">
                  <p>
                    <strong>Tipo:</strong> {results.anomalies.type}
                  </p>
                  <p>
                    <strong>Taxa Solicitada:</strong> {results.anomalies.rate_requested}%
                  </p>
                  <p>
                    <strong>Anomalias Injetadas:</strong> {results.anomalies.count_actual} ({results.anomalies.percentage_actual}%)
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
