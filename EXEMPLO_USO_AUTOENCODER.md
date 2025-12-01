# 📖 Exemplo Prático: Usando o Autoencoder

Neste guia, vamos seguir passo a passo como usar o sistema de detecção de anomalias integrado.

## 🎯 Cenário

Você tem um transformador (SPGR.ATF1) monitorado por sensores. Quer:
1. Treinar um modelo para aprender o comportamento normal
2. Detectar quando algo está errado
3. Programar manutenção preventiva baseada em anomalias

## 📋 Pré-requisitos

- Servidor backend rodando: `http://localhost:8000`
- Frontend rodando: `http://localhost:3000`
- Dados de sensores no banco de dados
- Banco de dados configurado

## 🔄 Passo a Passo

### Passo 1: Gerar Dados Sintéticos

Se não tiver dados ainda:

1. Acesse: `http://localhost:3000/generate`
2. Preencha os parâmetros:
   - **Número de Buchas**: 5
   - **Dias**: 60
   - **Frequência**: 1 hora
   - **Taxa de Degradação**: medium
3. Clique em **"⚡ Gerar Dados Sintéticos"**
4. Aguarde conclusão (alguns minutos)

```
Status esperado:
✅ Dados gerados com sucesso
   5 equipamentos
   1440 pontos por equipamento
   Total: 7200 pontos
```

### Passo 2: Executar Otimização (Opcional)

Para ter calendário com datas ótimas:

1. Acesse: `http://localhost:3000/optimize`
2. Clique em **"🚀 Executar Otimização"**
3. Aguarde (pode levar alguns minutos)

```
Status esperado:
✅ Otimização concluída para 5 equipamentos
   Custo médio: R$ 3500
   Pontos Pareto: 15
```

### Passo 3: Treinar o Autoencoder

1. Acesse: `http://localhost:3000/anomalies`
2. Clique em **"🤖 Treinar Autoencoder"**
3. Aguarde até 2-3 minutos

```
A página mostrará:
🔄 Treinando Modelo...
[Depois]
✅ Modelo treinado com sucesso
   7200 amostras
   11 features
```

**O que acontece por trás:**
- Carrega todos os dados de sensores
- Normaliza os valores (StandardScaler)
- Cria janelas de 168 horas (1 semana)
- Treina rede neural MLP por 50 épocas
- Aprende a reconstruir dados normais

### Passo 4: Injetar Anomalias (Simulação)

Para testar, podemos simular uma anomalia:

```python
# Via Python (na sua máquina):
import pandas as pd
from datetime import datetime, timedelta
import pyodbc

# Conectar ao banco
conn = pyodbc.connect('DRIVER=ODBC Driver 17 for SQL Server;'
                      'SERVER=seu_servidor;'
                      'DATABASE=MaintenanceDB;'
                      'Trusted_Connection=yes')

# Inserir ponto anômalo (corrente muito alta)
cursor = conn.cursor()
now = datetime.now()

cursor.execute('''
    INSERT INTO sensor_data (
        timestamp, equipment_id, localizacao, tipo_transformador,
        tensao_nominal, corrente_fuga, tg_delta, capacitancia,
        estado_saude, evento, temperatura_ambiente, umidade_relativa
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    now,                           # timestamp
    'SPGR.ATF1',                   # equipment_id
    'SPGR',                        # localizacao
    'ATF',                         # tipo_transformador
    138.0,                         # tensao_nominal
    98.5,                          # corrente_fuga (ANÔMALO - muito alto!)
    0.35,                          # tg_delta
    310.0,                         # capacitancia
    2,                             # estado_saude
    'test',                        # evento
    28.5,                          # temperatura_ambiente
    65.0                           # umidade_relativa
))

conn.commit()
cursor.close()
conn.close()

print("✅ Anomalia injetada com sucesso!")
```

### Passo 5: Detectar Anomalias

1. Aguarde 1-2 minutos após injetar anomalia (para ter novos dados)
2. Clique em **"⚡ Detectar Anomalias"** na página de anomalias
3. Aguarde (1-2 minutos)

```
Status esperado:
✅ Detecção concluída
   Anomalias encontradas: 1
   Percentual: 0.5%
```

### Passo 6: Visualizar Resultados

#### No Dashboard de Anomalias

Cards mostram:
```
┌─────────────────────────────────────┐
│ 🚨 Anomalias Detectadas: 1          │
│ Erro Médio (Q): 0.0156             │
│ Distância T²: 0.0234               │
│ Total de Pontos: 200               │
└─────────────────────────────────────┘
```

Lista detalhada:
```
┌────────────────────────────────────────────────┐
│ SPGR.ATF1              [CRÍTICO]                │
│ 2025-11-26 14:35:00                            │
├────────────────────────────────────────────────┤
│ Q (Reconstrução): 0.0156                       │
│  └─ Limite: 0.0045                             │
│ T² (Latente): 0.0234                           │
│  └─ Limite: 0.0089                             │
│ Erro Reconstrução: 0.0156                      │
│ Distância Latente: 0.0234                      │
└────────────────────────────────────────────────┘
```

#### No Calendário

Você verá:
```
┌────────────────────────────────────────────────┐
│ ⚠️ Anomalias Detectadas nas Últimas 24h        │
│ 1 anomalia (0.5% dos dados)                    │
│                                                 │
│ Erro Médio (Q): 0.0156   Máximo: 0.0156       │
│ Distância T²: 0.0234     Máximo: 0.0234       │
└────────────────────────────────────────────────┘

SPGR.ATF1 🚨 1 anomalia(s)
├─ Data: 26 de novembro, 2025
├─ Dias para manutenção: 15 dias
├─ Custo estimado: R$ 5000
└─ Prioridade: 4 ⭐⭐⭐⭐
```

## 🔍 Interpretando Métricas

### Q (Erro de Reconstrução)

```
Baixo (< 0.005):     Comportamento normal
Médio (0.005-0.015): Ligeiramente anômalo
Alto (> 0.015):      Definitivamente anômalo
```

Significa: "Quanto erro o modelo tem ao reconstruir esses dados?"
- Dados normais = baixo erro
- Dados estranhos = alto erro

### T² (Distância no Espaço Latente)

```
Baixo (< 0.010):     Dentro da variância normal
Médio (0.010-0.025): Desvio moderado
Alto (> 0.025):      Desvio significativo
```

Significa: "Como essa representação comprimida se compara ao padrão normal?"
- Similar = baixo T²
- Diferente = alto T²

### Threshold

Calculado como o 95º percentil dos dados:
```
95% dos dados normais < threshold
5% dos dados têm anomalias
```

## 📊 Exemplo de Análise

Suponha que você detectou:
```
Q = 0.0156 (acima do limite 0.0045)
T² = 0.0234 (acima do limite 0.0089)
```

**Interpretação:**
1. ✅ O modelo não consegue reconstruir bem esses dados (Q alto)
2. ✅ A representação latente é muito diferente (T² alto)
3. ✅ Portanto: **DEFINITIVAMENTE ANÔMALO**

**Ações:**
- Investigar sensor do equipamento
- Verificar se há falha de medição
- Se confirmado real: antecipar manutenção
- Se falso alarme: reajustar threshold

## 🎛️ Personalizações

### Usar CNN em vez de MLP

Para dados com padrões sequenciais complexos:

1. Abra: `frontend-shadcn/app/(dashboard)/anomalies/page.tsx`
2. Na função `trainModel()`, altere:

```typescript
// Antes (MLP):
model_arch: 'mlp'

// Depois (CNN):
model_arch: 'cnn'
```

3. Clique novamente em "🤖 Treinar Autoencoder"

CNN é melhor para:
- Padrões sequenciais
- Degradação gradual
- Mudanças de comportamento

### Aumentar Sensibilidade

Para detectar anomalias mais cedo:

1. Ao clicar "⚡ Detectar Anomalias"
2. Aumentar threshold_percentile em seu código

```typescript
// Mais sensível (90º percentil = 10% de anomalias):
threshold_percentile: 90.0

// Normal (95º percentil = 5% de anomalias):
threshold_percentile: 95.0

// Menos sensível (98º percentil = 2% de anomalias):
threshold_percentile: 98.0
```

### Usar Mais Histórico

Para melhor treinamento com mais dados:

1. Edite `anomalies/page.tsx`
2. Aumente `window_size`:

```typescript
// 1 semana (padrão):
window_size: 168

// 2 semanas:
window_size: 336

// 1 mês:
window_size: 24 * 30 = 720
```

## 🧪 Testes Sugeridos

### Teste 1: Detecção Básica
```
1. Treinar modelo
2. Detectar (deve ter poucas ou nenhuma anomalia)
3. Injetar anomalia manualmente
4. Detectar novamente (deve encontrar)
```

### Teste 2: Diferentes Equipamentos
```
1. Treinar modelo com todos os dados
2. Detectar com equipment_id específico
3. Comparar anomalias entre equipamentos
```

### Teste 3: Falsos Positivos
```
1. Ajustar threshold_percentile
2. Observar mudança em número de anomalias
3. Validar manualmente se são reais
```

### Teste 4: Integração com Calendário
```
1. Executar otimização
2. Detectar anomalias
3. Visualizar calendário
4. Verificar se badges aparecem corretamente
```

## 📈 Monitoramento em Produção

Quando em operação:

1. **Diárias:**
   - Revisar anomalias detectadas
   - Validar se condizem com realidade

2. **Semanais:**
   - Revisar métricas médias
   - Retreinar se comportamento mudou

3. **Mensais:**
   - Análise completa do período
   - Correlacionar com eventos reais
   - Ajustar thresholds se necessário

4. **Trimestrais:**
   - Avaliar precisão do modelo
   - Considerar trocar arquitetura
   - Revisar documentação

## 🐛 Troubleshooting Comum

### Problema: "Modelo não foi treinado"
**Solução**: Clique em "🤖 Treinar Autoencoder" primeiro

### Problema: Nenhuma anomalia detectada
**Solução:**
- Reduzir threshold_percentile para 85-90
- Verificar se tem dados suficientes
- Treinar novamente com mais épocas

### Problema: Muitas anomalias falsas
**Solução:**
- Aumentar threshold_percentile para 97-98
- Verificar qualidade dos dados
- Aumentar window_size

### Problema: Modelo muito lento
**Solução:**
- Reduzir num_epochs (padrão 50)
- Usar MLP em vez de CNN
- Reduzir window_size

## 🚀 Próximas Extensões

Ideias para melhorias futuras:

1. **Explicabilidade SHAP**
   - Identificar quais features causam anomalia
   - Visualizar impacto de cada variável

2. **Alertas Automáticos**
   - Email/SMS quando anomalia detectada
   - Integração com Slack/Teams

3. **Retrainamento Automático**
   - Reentrenar diariamente com novos dados
   - Atualizar threshold automaticamente

4. **Previsão de Falha**
   - Combinar anomalias com séries temporais
   - Prever quanto tempo até falha

5. **Dashboard em Tempo Real**
   - Gráfico em tempo real de Q e T²
   - Alertas visuais instantâneos

---

**Boa sorte com seu sistema de anomalias! 🎯**

Para dúvidas, consulte: `AUTOENCODER_README.md`
