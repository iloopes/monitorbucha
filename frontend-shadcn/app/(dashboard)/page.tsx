'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, CheckCircle, Zap, Calendar } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    status: 'loading',
    equipmentCount: 0,
    optimizedCount: 0,
    upcomingMaintenance: 0,
  })

  useEffect(() => {
    // Fetch dashboard stats
    // This would be implemented with actual API calls
    setStats({
      status: 'online',
      equipmentCount: 0,
      optimizedCount: 0,
      upcomingMaintenance: 0,
    })
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Bem-vindo ao Sistema de Manutenção Preditiva
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Equipamentos</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Equipamentos cadastrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Otimizados</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Análises completadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Próximas Manutenções</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Nos próximos 7 dias
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
            <Badge variant="default" className="bg-green-500">
              Online
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              <p className="text-xs text-muted-foreground">
                API em funcionamento
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Primeiros Passos</CardTitle>
          <CardDescription>
            Comece aqui para configurar seu sistema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                1
              </div>
              <div>
                <p className="font-medium">Configurar Banco de Dados</p>
                <p className="text-sm text-muted-foreground">
                  Vá para Banco de Dados e configure sua conexão com SQL Server
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                2
              </div>
              <div>
                <p className="font-medium">Gerar Dados Sintéticos</p>
                <p className="text-sm text-muted-foreground">
                  Use a página Gerar Dados para criar dados de teste
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                3
              </div>
              <div>
                <p className="font-medium">Executar Otimização</p>
                <p className="text-sm text-muted-foreground">
                  Execute o algoritmo NSGA-II para gerar o calendário de manutenção
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                4
              </div>
              <div>
                <p className="font-medium">Visualizar Resultados</p>
                <p className="text-sm text-muted-foreground">
                  Consulte o Calendário e analise os dados no painel Visualizar Dados
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Dica</AlertTitle>
        <AlertDescription>
          Para mais informações sobre como usar o sistema, consulte a documentação completa
          ou abra o arquivo README.md no diretório raiz do projeto.
        </AlertDescription>
      </Alert>
    </div>
  )
}
