# 📊 Guia de Logs e Status de Treinamento

## Problema Resolvido: "Treinamento Trava sem Feedback"

### O Que Estava Acontecendo

O treinamento **ESTAVA FUNCIONANDO**, mas:
- O frontend não sabia que estava em progresso
- A resposta do servidor só voltava após 10-15 minutos (fim do treinamento)
- Usuário pensava que "travou" ou congelou

### A Solução Implementada

Agora temos **3 camadas de feedback**:

```
┌─────────────────────────────────────────────────────────┐
│               TREINAMENTO EM ANDAMENTO                  │
├─────────────────────────────────────────────────────────┤
│ 1. Backend escreve logs em arquivo                      │
│    └─ /logs/maintenance_system.log                      │
│                                                          │
│ 2. Novo endpoint `/api/anomaly/training-status`        │
│    └─ Lê logs e retorna status em tempo real           │
│                                                          │
│ 3. Frontend faz polling a cada 5 segundos              │
│    └─ Exibe mensagens de progresso para o usuário      │
└─────────────────────────────────────────────────────────┘
```

## Como Funciona Agora

### 1️⃣ Você Clica em "🤖 Treinar Autoencoder"

```
Frontend envia requisição POST /api/anomaly/train
↓
Mensagem na tela: "⏳ Iniciando treinamento... Por favor aguarde"
```

### 2️⃣ Backend Começa o Treinamento

```
Backend inicia imediatamente e escreve logs:
   2025-11-26 14:52:23 - Iniciando treinamento...
   2025-11-26 14:52:24 - MovingWindowAutoEncoder inicializado
   2025-11-26 14:54:02 - Época 10/50 - Train Loss: 0.789380
   2025-11-26 14:56:30 - Época 20/50 - Train Loss: 0.726167
   2025-11-26 14:59:00 - Época 30/50 - Train Loss: 0.724267
   ... (continua...)
   2025-11-26 15:10:00 - Época 50/50 - Train Loss: 0.720956
   2025-11-26 15:10:01 - Treinamento concluído
   2025-11-26 15:10:02 - Metadados do modelo 'autoencoder_model' salvos
```

### 3️⃣ Frontend Faz Polling (a cada 5 segundos)

```
Frontend chama: GET /api/anomaly/training-status

Resposta:
{
  "status": "training",
  "message": "Modelo em treinamento...",
  "latest_logs": [
    "MovingWindowAutoEncoder inicializado",
    "Época 10/50 - Train Loss: 0.789380",
    "Época 20/50 - Train Loss: 0.726167",
    "Época 30/50 - Train Loss: 0.724267"
  ]
}
```

### 4️⃣ Tela Mostra Progresso

```
⏳ Iniciando treinamento... Por favor aguarde

(aguarda 5s)

📊 Época 10/50 - Train Loss: 0.789380

(aguarda 5s)

📊 Época 20/50 - Train Loss: 0.726167

... (e assim por diante)

(após conclusão)

✅ Treinamento concluído! Autoencoder treinado com sucesso
```

## 📝 O Que Você Verá

### Durante o Treinamento

✅ **Mensagens de Progresso**
```
⏳ Iniciando treinamento... Por favor aguarde
📊 Época 10/50 - Train Loss: 0.789380
📊 Época 20/50 - Train Loss: 0.726167
📊 Época 30/50 - Train Loss: 0.724267
📊 Época 40/50 - Train Loss: 0.723214
📊 Época 50/50 - Train Loss: 0.720956
✅ Treinamento concluído!
```

### Se Algo Der Errado

❌ **Mensagens de Erro**
```
❌ Erro: Nenhum dado de sensor encontrado no banco
❌ Erro durante treinamento: ModelError: Dimensão incompatível
```

### Timeout (>10 minutos)

⚠️ **Mensagem de Fallback**
```
✅ Treinamento aparentemente concluído (timeout de polling). Verifique os logs.
```

## 🔍 Monitorando os Logs

### Em Tempo Real (Windows PowerShell)

```powershell
# Abrir janela PowerShell
Get-Content -Path "logs\maintenance_system.log" -Tail 20 -Wait
```

### Em Tempo Real (Windows CMD)

```cmd
# Usar Notepad++ ou abrir o arquivo em editor que atualiza automaticamente
# C:\...\logs\maintenance_system.log
```

### Procurar por Logs de Treinamento Específicos

```powershell
# Filtrar apenas linhas com "Época" ou "Treinamento"
Get-Content "logs\maintenance_system.log" | Where-Object { $_ -match "Época|Treinamento" }
```

## ⏱️ Tempos Esperados

### Com 7200 Pontos de Dados (5 buchas × 60 dias)

| Componente | Tempo Estimado |
|------------|----------------|
| Carregar dados | <5s |
| Normalizar | <5s |
| **Época 1-10** | **~2 min** |
| **Época 11-20** | **~2 min** |
| **Época 21-30** | **~2 min** |
| **Época 31-40** | **~2 min** |
| **Época 41-50** | **~2 min** |
| Salvar modelo | <5s |
| **TOTAL** | **~13 min** |

### Com Mais Dados

- 10 buchas × 60 dias → ~18-20 min
- 20 buchas × 60 dias → ~25-30 min

### Nota sobre CPU

Se seu computador for lento ou tiver muitos processos:
- Pode levar mais tempo
- Logs aparecerao menos frequentemente
- **Mas o treinamento continua acontecendo!**

## 🔧 Configurações de Treinamento

Se quiser treinar mais rápido (menos acurado):

```
Reduzir num_epochs: 50 → 20-30
Reduzir window_size: 168 → 84-120
Aumentar learning_rate: 0.001 → 0.01 (cuidado!)
```

Se quiser treinar mais devagar (mais acurado):

```
Aumentar num_epochs: 50 → 75-100
Aumentar window_size: 168 → 336
Reduzir learning_rate: 0.001 → 0.0005
```

## 🆘 Troubleshooting

### "Nenhuma mensagem aparece por muito tempo"

**Causa**: Treinamento realmente está rodando, logs aparecem a cada época (~2min)

**Solução**: Espere! Abra `logs\maintenance_system.log` para confirmar progresso

### "Status check: Error"

**Causa**: Erro ao ler arquivo de logs (raro)

**Solução**: Continua tentando. Erro é não-bloqueante.

### "Erro: Nenhum dado de sensor encontrado"

**Causa**: Nenhum dado gerado ainda

**Solução**: Vá em "Gerar Dados" primeiro

### "❌ Erro durante treinamento: Viola violação de restrição UNIQUE"

**Causa**: Modelo com mesmo nome já existe no banco

**Solução**:
1. Mude o `model_name` para algo único
2. Ou delete o modelo antigo do banco

## 📊 Estrutura do Log

Cada linha de log tem este formato:

```
2025-11-26 14:52:23 - src.anomaly.manager - INFO - Iniciando treinamento do autoencoder (mlp)...
└─ Data  └─ Hora ─ Módulo ─ Nível ─ Mensagem
```

### Níveis de Log

- **INFO** ✅ Informação normal (tudo ok)
- **WARNING** ⚠️ Aviso (algo suspeito mas continuou)
- **ERROR** ❌ Erro (algo quebrou, deve ser investigado)

## 🎯 Resumo

**Antes**: Clica, nada acontece, espera 15min, resultado de repente
**Agora**: Clica, vê "iniciando", vê progresso a cada ~2min, resultado no final

---

**Última atualização**: 26 de novembro de 2025
**Versão**: 2.0 (com feedback em tempo real)
