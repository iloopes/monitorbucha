'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader, AlertTriangle, TrendingUp, Activity } from 'lucide-react'
import { api } from '@/lib/api'

interface AnomalyData {
  id: string
  equipment_id: string
  timestamp: string
  Q: number
  T2: number
  Q_threshold: number
  T2_threshold: number
  is_anomaly: boolean
  severity: string
  reconstruction_error?: number
  latent_distance?: number
}

interface AnomalySummary {
  equipment_id: string
  hours: number
  total_points: number
  anomalies_detected: number
  anomaly_percentage: number
  mean_Q?: number
  mean_T2?: number
  max_Q?: number
  max_T2?: number
  severity_counts?: Record<string, number>
}

export default function AnomaliesPage() {
  const [loading, setLoading] = useState(false)
  const [training, setTraining] = useState(false)
  const [anomalies, setAnomalies] = useState<AnomalyData[]>([])
  const [summary, setSummary] = useState<AnomalySummary | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [selectedHours, setSelectedHours] = useState(24)
  const [trainingWindowSize, setTrainingWindowSize] = useState(168)

  useEffect(() => {
    loadAnomalies()
  }, [selectedHours])

  const trainModel = async () => {
    setTraining(true)
    setMessage(null)

    try {
      setMessage(`⏳ Iniciando treinamento (janela: ${trainingWindowSize}h)... Por favor aguarde (pode levar alguns minutos)`)

      const response = await api.post('/anomaly/train', {
        model_name: 'autoencoder_model',
        model_arch: 'mlp',
        latent_dim: 5,
        window_size: trainingWindowSize,
        num_epochs: 50,
        learning_rate: 1e-3,
        save_to_database: true
      })

      if (response.data.status === 'success') {
        setMessage(`✅ Modelo treinado: ${response.data.message}`)
        // Polling para status de treinamento
        let isCompleted = false
        let pollCount = 0
        const maxPolls = 120  // Máximo 10 minutos (5s * 120)

        while (!isCompleted && pollCount < maxPolls) {
          await new Promise(resolve => setTimeout(resolve, 5000))  // Esperar 5s
          pollCount++

          try {
            const statusRes = await fetch('http://localhost:8000/api/anomaly/training-status')
            const statusData = await statusRes.json()

            if (statusData.latest_logs && statusData.latest_logs.length > 0) {
              const latestLog = statusData.latest_logs[statusData.latest_logs.length - 1]
              setMessage(`📊 ${latestLog}`)
            }

            if (statusData.status === 'completed') {
              isCompleted = true
              setMessage(`✅ Treinamento concluído! ${response.data.message}`)
              // Carregar anomalias após treinamento
              setTimeout(loadAnomalies, 1000)
            } else if (statusData.status === 'error') {
              isCompleted = true
              setMessage(`❌ Erro durante treinamento: ${statusData.message}`)
            }
          } catch (pollError) {
            // Continua tentando mesmo com erro de poll
            console.log('Status check:', pollError)
          }
        }

        if (!isCompleted && pollCount >= maxPolls) {
          setMessage(`✅ Treinamento aparentemente concluído (timeout de polling). Verifique os logs.`)
          setTimeout(loadAnomalies, 1000)
        }
      } else {
        setMessage(`❌ Erro ao treinar: ${response.data.message}`)
      }
    } catch (error) {
      setMessage(`❌ Erro: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setTraining(false)
    }
  }

  const detectAnomalies = async () => {
    setLoading(true)
    try {
      const response = await api.post('/anomaly/detect', {
        model_name: 'autoencoder_model',
        threshold_percentile: 95,
        save_to_database: true,
        window_size: trainingWindowSize
      })

      if (response.data.status === 'success') {
        setMessage('✅ Detecção concluída com sucesso')
        loadAnomalies()
      } else {
        setMessage(`❌ Erro na detecção: ${response.data.message}`)
      }
    } catch (error) {
      setMessage(`Erro: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  const loadAnomalies = async () => {
    setLoading(true)
    try {
      const [anomaliesRes, summaryRes] = await Promise.all([
        api.get(`/anomaly/list?hours=${selectedHours}&only_anomalies=true`),
        api.get(`/anomaly/summary?hours=${selectedHours}`)
      ])

      if (anomaliesRes.data.status === 'success') {
        setAnomalies(anomaliesRes.data.anomalies || [])
      }

      if (summaryRes.data.status === 'success') {
        setSummary(summaryRes.data.summary)
      }

      if (anomaliesRes.data.anomalies?.length === 0) {
        setMessage('Nenhuma anomalia detectada nos dados atuais')
      }
    } catch (error) {
      setMessage(`Erro ao carregar dados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'crítico':
        return 'bg-red-500 text-white'
      case 'alto':
        return 'bg-orange-500 text-white'
      case 'médio':
        return 'bg-yellow-500 text-white'
      case 'baixo':
        return 'bg-blue-500 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">🔍 Detecção de Anomalias</h1>
        <p className="text-muted-foreground">
          Analise anomalias detectadas pelo autoencoder em tempo real
        </p>
      </div>

      {/* Cards de Resumo */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Anomalias Detectadas</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.anomalies_detected}</div>
              <p className="text-xs text-muted-foreground">{summary.anomaly_percentage.toFixed(1)}% dos dados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Erro Médio (Q)</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(summary.mean_Q || 0).toFixed(4)}</div>
              <p className="text-xs text-muted-foreground">Máximo: {(summary.max_Q || 0).toFixed(4)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Distância T² Médio</CardTitle>
              <Activity className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(summary.mean_T2 || 0).toFixed(4)}</div>
              <p className="text-xs text-muted-foreground">Máximo: {(summary.max_T2 || 0).toFixed(4)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Pontos</CardTitle>
              <Activity className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_points}</div>
              <p className="text-xs text-muted-foreground">Últimas {summary.hours}h</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Controles */}
      <div className="space-y-4">
        <div className="flex flex-wrap gap-3">
          <Button onClick={trainModel} disabled={training} variant="default">
            {training ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Treinando Modelo...
              </>
            ) : (
              '🤖 Treinar Autoencoder'
            )}
          </Button>

          <Button onClick={detectAnomalies} disabled={loading} variant="outline">
            {loading ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Detectando...
              </>
            ) : (
              '⚡ Detectar Anomalias'
            )}
          </Button>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Visualizar Anomalias dos Últimos:</label>
            <div className="flex gap-2">
              {[6, 12, 24, 48, 168].map(hours => (
                <Button
                  key={hours}
                  onClick={() => setSelectedHours(hours)}
                  variant={selectedHours === hours ? 'default' : 'outline'}
                  size="sm"
                  title={`Mostrar anomalias dos últimos ${hours} horas`}
                >
                  {hours}h
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Opcoes de Janela de Tempo para Treinamento */}
        <Card className="bg-blue-50 border-2 border-blue-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">⚙️ CONFIGURAÇÃO DO TREINAMENTO - Como o modelo aprende</CardTitle>
            <CardDescription className="text-xs mt-1">
              Selecione antes de clicar em "🤖 Treinar Autoencoder"
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-baseline justify-between">
                <label className="text-sm font-semibold">Janela de Tempo de Treinamento:</label>
                <span className="text-lg font-bold text-blue-600">{trainingWindowSize}h</span>
              </div>
              <div className="flex gap-2 flex-wrap">
                {[6, 12, 24, 48, 168].map(hours => (
                  <button
                    key={`train-${hours}`}
                    onClick={() => setTrainingWindowSize(hours)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      trainingWindowSize === hours
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-white border border-blue-300 text-blue-700 hover:bg-blue-50'
                    }`}
                    title={`Treinar com ${hours} horas de dados históricos`}
                  >
                    {hours}h
                  </button>
                ))}
              </div>
              <div className="bg-white p-3 rounded border border-blue-200 mt-3">
                <p className="text-xs text-gray-700 font-medium mb-1">💡 O que significa:</p>
                <p className="text-xs text-gray-600">
                  {trainingWindowSize <= 12 && "Detecção rápida com menos contexto histórico. Use para anomalias imediatas."}
                  {trainingWindowSize === 24 && "Um dia completo de dados. Captura padrões diários naturais."}
                  {trainingWindowSize === 48 && "Dois dias de dados. Bom para padrões que repetem a cada 24h."}
                  {trainingWindowSize >= 168 && "Uma semana completa. Melhor generalização com mais dados."}
                </p>
              </div>
              <p className="text-xs text-gray-600 border-t border-blue-200 pt-2">
                ℹ️ Depois de treinar, clique em "⚡ Detectar Anomalias" para processar os dados
              </p>
            </div>
          </CardContent>
        </Card>

      </div>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* Lista de Anomalias */}
      {anomalies.length > 0 && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{anomalies.length} Anomalias Detectadas</CardTitle>
              <CardDescription>
                Últimas {selectedHours} horas
              </CardDescription>
            </CardHeader>
          </Card>

          <div className="grid gap-4">
            {anomalies.slice(0, 50).map((anomaly, idx) => (
              <Card key={idx} className="border-l-4 border-l-red-500 bg-red-50">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-bold">{anomaly.equipment_id}</h3>
                      <p className="text-sm text-muted-foreground">
                        {new Date(anomaly.timestamp).toLocaleString('pt-BR')}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${getSeverityColor(anomaly.severity)}`}>
                      {anomaly.severity}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 md:grid-cols-4 text-sm">
                    <div>
                      <p className="text-muted-foreground font-medium">Q (Reconstrução)</p>
                      <p className="font-semibold">{anomaly.Q?.toFixed(6) || 'N/A'}</p>
                      <p className="text-xs text-muted-foreground">Limite: {anomaly.Q_threshold?.toFixed(6)}</p>
                    </div>

                    <div>
                      <p className="text-muted-foreground font-medium">T² (Latente)</p>
                      <p className="font-semibold">{anomaly.T2?.toFixed(6) || 'N/A'}</p>
                      <p className="text-xs text-muted-foreground">Limite: {anomaly.T2_threshold?.toFixed(6)}</p>
                    </div>

                    <div>
                      <p className="text-muted-foreground font-medium">Erro Reconstrução</p>
                      <p className="font-semibold">{anomaly.reconstruction_error?.toFixed(6) || 'N/A'}</p>
                    </div>

                    <div>
                      <p className="text-muted-foreground font-medium">Distância Latente</p>
                      <p className="font-semibold">{anomaly.latent_distance?.toFixed(6) || 'N/A'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {anomalies.length > 50 && (
            <p className="text-center text-muted-foreground text-sm">
              Mostrando 50 de {anomalies.length} anomalias
            </p>
          )}
        </div>
      )}
    </div>
  )
}
