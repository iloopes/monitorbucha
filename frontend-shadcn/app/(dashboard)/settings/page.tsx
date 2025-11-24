'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { InfoIcon } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">⚙️ Configurações</h1>
        <p className="text-muted-foreground">
          Informações do sistema e configurações gerais
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sobre o Sistema</CardTitle>
          <CardDescription>
            Sistema de Manutenção Preditiva v2.0
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Versão</p>
            <p className="text-lg font-semibold">2.0.0</p>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground">Data de Lançamento</p>
            <p className="text-lg font-semibold">2025</p>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground">Nível de Maturidade Tecnológica (TRL)</p>
            <p className="text-lg font-semibold">9 (Pronto para Produção)</p>
          </div>

          <div>
            <p className="text-sm font-medium text-muted-foreground">Descrição</p>
            <p className="text-sm text-foreground">
              Sistema inteligente para planejamento otimizado de manutenção usando Cadeias de Markov
              e Algoritmo Genético NSGA-II. Implementa otimização multi-objetivo para encontrar o
              melhor compromisso entre custo e indisponibilidade.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Características Principais</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Modelagem de Markov com 5 estados de saúde</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Otimização NSGA-II configurável</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Análise da fronteira de Pareto</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Processamento de dados (CSV, Excel, Parquet, JSON)</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Cálculo de taxa de degradação e predição de falha</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Ranking de criticidade de equipamentos</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Visualizações avançadas (gráficos Pareto, séries temporais)</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-500">✅</span>
              <span>Relatórios em múltiplos formatos</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Variáveis de Ambiente</CardTitle>
          <CardDescription>
            Configure estas variáveis em seu arquivo .env.local
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 font-mono text-sm">
            <div className="bg-muted p-2 rounded">
              <p>NEXT_PUBLIC_API_URL=http://localhost:8000/api</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            A URL da API pode ser ajustada para o endereço do seu servidor backend.
          </p>
        </CardContent>
      </Card>

      <Alert>
        <InfoIcon className="h-4 w-4" />
        <AlertTitle>Documentação</AlertTitle>
        <AlertDescription>
          Para informações detalhadas, consulte a documentação completa em docs/ ou o README.md
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Licença</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">
            Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
