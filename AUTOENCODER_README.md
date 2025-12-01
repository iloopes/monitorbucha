# 🤖 Detecção de Anomalias com Autoencoder

Este documento explica como usar o módulo de detecção de anomalias integrado ao Sistema de Manutenção Preditiva.

## 📋 Visão Geral

O **Autoencoder com Janela Deslizante (Moving Window AutoEncoder - MWAE)** detecta anomalias em dados de transformadores em tempo real usando duas métricas principais:

- **Q (Erro de Reconstrução)**: Mede como bem o modelo consegue reconstruir os dados. Valores altos indicam comportamento anômalo.
- **T² (Distância no Espaço Latente)**: Mede a distância no espaço comprimido. Valores altos indicam desvios do padrão normal.

## 🏗️ Arquitetura

### Estrutura de Pastas

```
src/anomaly/
├── __init__.py
├── autoencoder.py      # Classes MLPAutoEncoder e CNNAutoEncoder
└── manager.py          # AnomalyManager para gerenciar treinamento e detecção
```

### Componentes

1. **MLPAutoEncoder**: Autoencoder com arquitetura Multi-Layer Perceptron
   - Simples e rápido
   - Bom para dados com padrões gerais
   - Menos consumo de memória

2. **CNNAutoEncoder**: Autoencoder com arquitetura Convolucional
   - Melhor para séries temporais
   - Captura padrões sequenciais
   - Requer mais memória

3. **AnomalyManager**: Gerenciador central
   - Treinamento do modelo
   - Detecção de anomalias
   - Persistência em banco de dados

## 🚀 Como Usar

### 1. Acessar a Interface Web

1. Navegue até `http://localhost:3000/anomalies`
2. Você verá o dashboard de anomalias com:
   - Resumo de estatísticas
   - Botões para treinar e detectar
   - Lista de anomalias detectadas

### 2. Treinar o Modelo

```
Clique em "🤖 Treinar Autoencoder"
```

**Parâmetros padrão:**
- Model: MLP
- Latent Dim: 5
- Window Size: 168 horas (1 semana)
- Epochs: 50
- Learning Rate: 0.001

O modelo usa dados de `sensor_data` para aprender o padrão normal de comportamento.

### 3. Detectar Anomalias

```
Clique em "⚡ Detectar Anomalias"
```

O modelo detectará desvios dos padrões aprendidos e classificará como:
- **Crítico**: Anomalias severas
- **Alto**: Desvios significativos
- **Médio**: Comportamento ligeiramente anômalo
- **Baixo**: Comportamento normal

### 4. Visualizar Resultados

#### No Dashboard de Anomalias
- Cards com resumo: total de anomalias, erro médio, distância latente
- Filtros por período: 6h, 12h, 24h, 48h, 168h
- Lista detalhada de cada anomalia detectada

#### No Calendário de Manutenção
- Badge vermelha indicando anomalias detectadas
- Número de anomalias por equipamento
- Resumo geral de anomalias nas últimas 24h

## 📊 API Endpoints

### Treinar Modelo
```
POST /api/anomaly/train

Body:
{
  "model_name": "my_model",
  "model_arch": "mlp",        # "mlp" ou "cnn"
  "latent_dim": 5,
  "window_size": 168,
  "num_epochs": 50,
  "learning_rate": 0.001
}
```

### Detectar Anomalias
```
POST /api/anomaly/detect

Body:
{
  "equipment_ids": ["SPGR.ATF1", "SPGR.ATF2"],  # opcional
  "threshold_percentile": 95.0,
  "save_to_database": true
}
```

### Listar Anomalias
```
GET /api/anomaly/list?hours=24&only_anomalies=true

Retorna:
{
  "status": "success",
  "total": 15,
  "anomalies": [...]
}
```

### Resumo de Anomalias
```
GET /api/anomaly/summary?hours=24

Retorna:
{
  "status": "success",
  "summary": {
    "total_points": 100,
    "anomalies_detected": 15,
    "anomaly_percentage": 15.0,
    "mean_Q": 0.0023,
    "mean_T2": 0.0045,
    "max_Q": 0.0156,
    "max_T2": 0.0234
  }
}
```

## 💾 Dados no Banco

### Tabela: `anomaly_detections`
```sql
- equipment_id: Identificador do equipamento
- timestamp: Data/hora da detecção
- Q: Erro de reconstrução
- T2: Distância no espaço latente
- Q_threshold: Limiar de Q
- T2_threshold: Limiar de T²
- is_anomaly: Booleano (anomalia detectada?)
- reconstruction_error: Erro de reconstrução bruto
- latent_distance: Distância latente bruta
- severity: 'crítico', 'alto', 'médio', 'baixo'
```

### Tabela: `anomaly_models`
```sql
- model_name: Nome do modelo
- model_arch: Arquitetura ("mlp" ou "cnn")
- latent_dim: Dimensão do espaço latente
- window_size: Tamanho da janela
- training_epochs: Número de épocas
- threshold_percentile: Percentil do threshold
- trained_at: Data do treinamento
```

## 📈 Fluxo Recomendado

```
1. Gerar dados sintéticos
   ↓
2. Treinar modelo (🤖 Treinar Autoencoder)
   ↓
3. Executar otimização (NSGA-II + Markov)
   ↓
4. Detectar anomalias (⚡ Detectar Anomalias)
   ↓
5. Visualizar calendário com anomalias
   ↓
6. Consultar dashboard de anomalias para detalhes
```

## ⚙️ Personalização

### Alterar Arquitetura

Para usar CNN em vez de MLP:

```typescript
// Frontend (anomalies/page.tsx)
const response = await api.post('/anomaly/train', {
  model_arch: 'cnn',  // Alterar para 'cnn'
  latent_dim: 5,
  window_size: 168,
  num_epochs: 50
})
```

### Ajustar Threshold

Threshold mais alto = menos anomalias detectadas
```typescript
const response = await api.post('/anomaly/detect', {
  threshold_percentile: 98.0  // Mais restritivo
})
```

### Aumentar Dados de Treinamento

Aumentar `window_size` para usar mais histórico:
```typescript
window_size: 24 * 30  // 30 dias ao invés de 7
```

## 🔧 Troubleshooting

### Erro: "Modelo não foi treinado"
**Solução**: Clique em "🤖 Treinar Autoencoder" antes de detectar

### Erro: "Nenhum dado de sensor encontrado"
**Solução**: Gere dados sintéticos primeiro em "Gerar Dados"

### Poucas anomalias detectadas
**Solução**:
- Reduzir `threshold_percentile` (ex: 90.0)
- Treinar com mais épocas
- Usar CNN em vez de MLP

### Muitas anomalias (false positives)
**Solução**:
- Aumentar `threshold_percentile` (ex: 98.0)
- Aumentar `window_size` para mais contexto
- Reduzir `num_epochs` para evitar overfitting

## 📚 Métricas Principais

### Q (Erro de Reconstrução)
- **Baixo**: Dados normais, padrão aprendido corretamente
- **Alto**: Desvio significativo do padrão normal

### T² (Distância no Espaço Latente)
- **Baixo**: Dentro da variância do padrão normal
- **Alto**: Representação latente anômala

### Limiar (Threshold)
- Calculado como `percentile(metrica, threshold_percentile)`
- Padrão: 95º percentil (5% dos dados acima)

## 🎯 Casos de Uso

1. **Detecção Precoce de Falhas**
   - Identifica padrões anômalos antes que virem falhas
   - Dispara alertas para manutenção preventiva

2. **Validação de Dados**
   - Detecta falhas de sensores
   - Identifica dados corrompidos ou outliers

3. **Monitoramento em Tempo Real**
   - Acompanha mudanças gradativas
   - Aprende novos padrões normais

4. **Análise Histórica**
   - Identifica períodos de operação anômala
   - Correlaciona com eventos de manutenção

## 🔗 Integração com Calendário

O calendário de manutenção agora mostra:

1. **Badge de Anomalias**: "🚨 2 anomalia(s)" próximo ao nome do equipamento
2. **Resumo de Anomalias**: Card com estatísticas gerais
3. **Filtros Temporais**: Análise de diferentes períodos

Exemplo de card no calendário:
```
SPGR.ATF1 [🚨 3 anomalia(s)]
SPGR - Substation Guarulhos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Data: Quinta-feira, 26 de novembro de 2025
⏱️ Dias: 15 dias
🔧 Estado: 2
💰 Custo: R$ 5000.00
⚠️ Prioridade: 4
📊 Indisponibilidade: 2.5000
```

## 📦 Dependências

As seguintes bibliotecas são usadas:
- `torch`: Deep learning
- `scikit-learn`: Normalização de dados
- `pandas`: Manipulação de dados
- `numpy`: Operações numéricas
- `pyodbc`: Conexão com SQL Server

```bash
pip install torch scikit-learn pandas numpy pyodbc
```

## 🎓 Referências Teóricas

### Autoencoder
Um autoencoder é uma rede neural que comprime (encoda) dados em um espaço latente menor e depois reconstrói (decoda) os dados originais. Na detecção de anomalias:

- Dados normais são bem reconstruídos
- Dados anômalos têm alto erro de reconstrução

### Janela Deslizante (Moving Window)
Processa dados em janelas temporais sequenciais, permitindo:

- Captura de padrões sequenciais
- Detecção de anomalias em séries temporais
- Análise de mudanças gradativas

### NSGA-II + Autoencoder
Combinação poderosa:

- **NSGA-II**: Otimiza quando fazer manutenção
- **Autoencoder**: Detecta quando há problema

Fluxo: Anomalia → Disparar otimização → Agendar manutenção

## 💡 Dicas e Boas Práticas

1. **Treinar regularmente**: Retreine o modelo a cada novo ciclo de dados
2. **Monitorar métricas**: Acompanhe Q e T² para mudanças de padrão
3. **Validar alertas**: Verifique false positives e ajuste thresholds
4. **Manter histórico**: Armazene dados de treino para análises futuras
5. **Combinar métodos**: Use anomalias + otimização + calendário para máxima eficácia

---

**Versão**: 1.0
**Última atualização**: 2025-11-26
**Autor**: Sistema de Manutenção Preditiva 2.0
