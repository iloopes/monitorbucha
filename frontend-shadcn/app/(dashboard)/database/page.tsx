'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { configureDatabaseConnection, initializeDatabase } from '@/lib/api'

export default function DatabasePage() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)
  const [formData, setFormData] = useState({
    server: 'DESKTOP-0L1FQAQ\\KUZUSHI',
    database: 'MaintenanceDB',
    trustedConnection: true,
    username: '',
    password: '',
  })

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleConfigureDatabase = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      const response = await configureDatabaseConnection({
        server: formData.server,
        database: formData.database,
        trusted_connection: formData.trustedConnection,
        username: formData.trustedConnection ? null : formData.username,
        password: formData.trustedConnection ? null : formData.password,
      })

      setMessage({
        type: 'success',
        text: `✓ ${response.message} (${response.server}/${response.database})`,
      })
    } catch (error) {
      setMessage({
        type: 'error',
        text: `✗ Erro ao conectar: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleInitializeDatabase = async () => {
    setLoading(true)
    setMessage(null)

    try {
      const response = await initializeDatabase()
      setMessage({
        type: 'success',
        text: `✓ ${response.message}\nTabelas: ${response.tables?.join(', ') || 'N/A'}`,
      })
    } catch (error) {
      setMessage({
        type: 'error',
        text: `✗ Erro ao criar tabelas: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configuração do Banco de Dados</h1>
        <p className="text-muted-foreground">
          Configure sua conexão com SQL Server
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Conexão do Banco de Dados</CardTitle>
          <CardDescription>
            Configure os parâmetros de conexão para seu SQL Server
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleConfigureDatabase} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="server">Servidor SQL Server</Label>
                <Input
                  id="server"
                  value={formData.server}
                  onChange={(e) => handleInputChange('server', e.target.value)}
                  placeholder="DESKTOP-0L1FQAQ\KUZUSHI"
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="database">Nome do Banco</Label>
                <Input
                  id="database"
                  value={formData.database}
                  onChange={(e) => handleInputChange('database', e.target.value)}
                  placeholder="MaintenanceDB"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="trusted"
                checked={formData.trustedConnection}
                onCheckedChange={(checked) =>
                  handleInputChange('trustedConnection', checked as boolean)
                }
                disabled={loading}
              />
              <Label htmlFor="trusted" className="cursor-pointer">
                Autenticação Windows (Trusted Connection)
              </Label>
            </div>

            {!formData.trustedConnection && (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="username">Usuário</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Conectando...
                  </>
                ) : (
                  'Conectar ao Banco'
                )}
              </Button>

              <Button
                type="button"
                variant="secondary"
                onClick={handleInitializeDatabase}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Criando...
                  </>
                ) : (
                  'Criar Tabelas'
                )}
              </Button>
            </div>
          </form>

          {message && (
            <Alert className={`mt-6 ${message.type === 'success' ? 'border-green-500 bg-green-50' : message.type === 'error' ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'}`}>
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

      <Card>
        <CardHeader>
          <CardTitle>Informações Importantes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>
            <strong>Autenticação Windows:</strong> Se habilitada, a conexão usará as credenciais do Windows autenticadas.
          </p>
          <p>
            <strong>Autenticação SQL:</strong> Desabilite para usar usuário e senha do SQL Server.
          </p>
          <p>
            <strong>Criar Tabelas:</strong> Clique em &quot;Criar Tabelas&quot; após a conexão ser estabelecida para inicializar o banco de dados.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
