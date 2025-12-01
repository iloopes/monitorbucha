# 🏗️ Arquitetura do Sistema de Anomalias

## 📐 Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE MANUTENÇÃO PREDITIVA             │
│                         Com Detecção de Anomalias               │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   Sensores em         │
                    │   Tempo Real          │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Banco de Dados     │
                    │   (sensor_data)      │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
  ┌──────────┐         ┌────────────┐         ┌──────────┐
  │ Anomalias│         │ Markov +   │         │Dashboard │
  │(Detecção)│         │ NSGA-II    │         │(Dados)   │
  └──────────┘         │(Otimização)│         └──────────┘
        │              └────────────┘              │
        │                      │                  │
        └──────────┬───────────┴──────────────────┘
                   │
        ┌──────────▼───────────┐
        │   Frontend React     │
        │  (Dashboard / UI)    │
        └──────────────────────┘
```

## 🔄 Fluxo de Detecção de Anomalias

```
FLUXO COMPLETO:

1. COLETA DE DADOS
   ├─ Sensores monitoram transformador
   ├─ Dados salvos em sensor_data
   └─ Atualizado a cada hora

2. TREINAMENTO
   ├─ Usuário clica "Treinar Autoencoder"
   ├─ Backend carrega dados históricos (168h)
   ├─ Normaliza com StandardScaler
   ├─ Cria janelas (window_size = 168)
   ├─ Treina MLP ou CNN por 50 épocas
   └─ Salva metadados em anomaly_models

3. DETECÇÃO
   ├─ Usuário clica "Detectar Anomalias"
   ├─ Backend carrega novos dados
   ├─ Para cada janela:
   │  ├─ Passa pelo modelo
   │  ├─ Calcula erro de reconstrução (Q)
   │  ├─ Calcula distância latente (T²)
   │  ├─ Compara com threshold
   │  └─ Marca como anômalo ou normal
   └─ Salva em anomaly_detections

4. VISUALIZAÇÃO
   ├─ Dashboard de Anomalias mostra:
   │  ├─ Cards resumidos (Q, T², contagem)
   │  ├─ Lista detalhada com filtros
   │  └─ Gráficos de distribuição
   ├─ Calendário integrado mostra:
   │  ├─ Badges nos equipamentos anômalos
   │  └─ Resumo geral de anomalias
   └─ API disponível para integração

5. AÇÃO
   ├─ Usuário identifica anomalia
   ├─ Investiga causa
   └─ Executa manutenção preventiva
```

## 📁 Estrutura de Pastas

```
Software_Bucha/
├── api/
│   ├── main.py
│   │   ├─ Imports:
│   │   │  └─ from src.anomaly import AnomalyManager
│   │   ├─ Modelos Pydantic:
│   │   │  ├─ AnomalyTrainingRequest
│   │   │  └─ AnomalyDetectionRequest
│   │   └─ Endpoints (150+ linhas):
│   │      ├─ POST /api/anomaly/train
│   │      ├─ POST /api/anomaly/detect
│   │      ├─ GET /api/anomaly/list
│   │      └─ GET /api/anomaly/summary
│   └─ ...
│
├── src/
│   ├── anomaly/  [NOVO]
│   │   ├── __init__.py
│   │   ├── autoencoder.py (250+ linhas)
│   │   │   ├─ class MLPAutoEncoder(nn.Module)
│   │   │   │  ├─ encoder: Linear → ReLU → Linear
│   │   │   │  └─ decoder: Linear → ReLU → Linear
│   │   │   ├─ class CNNAutoEncoder(nn.Module)
│   │   │   │  ├─ encoder: Conv1d → ReLU → MaxPool1d
│   │   │   │  └─ decoder: ConvTranspose1d → ReLU
│   │   │   └─ class MovingWindowAutoEncoder
│   │   │      ├─ fit(data, window_size, num_epochs, ...)
│   │   │      ├─ detect(data, threshold_percentile, ...)
│   │   │      ├─ _create_windows()
│   │   │      └─ get_anomaly_summary()
│   │   └── manager.py (280+ linhas)
│   │       └─ class AnomalyManager
│   │          ├─ train_autoencoder(...)
│   │          ├─ detect_anomalies(...)
│   │          ├─ get_anomalies(...)
│   │          ├─ _ensure_tables_exist()
│   │          ├─ _save_model_metadata()
│   │          └─ _save_detections()
│   ├── database/
│   │   └── sql_server.py
│   │       └─ class DatabaseManager
│   │          └─ Integração com anomaly_detections
│   ├── models/
│   ├── optimization/
│   ├── data/
│   └── utils/
│
├── frontend-shadcn/
│   ├── app/(dashboard)/
│   │   ├── anomalies/  [NOVO]
│   │   │   └── page.tsx (400+ linhas)
│   │   │      ├─ Card: Resumo de anomalias
│   │   │      ├─ Button: Treinar / Detectar
│   │   │      ├─ Filtros: 6h, 12h, 24h, 48h, 168h
│   │   │      └─ Lista: Detalhes de anomalias
│   │   ├── calendar/
│   │   │   └── page.tsx [ATUALIZADO]
│   │   │      ├─ Card: Resumo de anomalias integrado
│   │   │      ├─ Badge: 🚨 Anomalias por equipamento
│   │   │      └─ getEquipmentAnomalies()
│   │   └── ...
│   ├── components/
│   │   └── sidebar.tsx [ATUALIZADO]
│   │       └─ Menu item: "Anomalias" (AlertTriangle icon)
│   ├── lib/
│   │   └── api.ts [ATUALIZADO]
│   │       ├─ trainAnomalyModel()
│   │       ├─ detectAnomalies()
│   │       ├─ listAnomalies()
│   │       └─ getAnomalySummary()
│   └── ...
│
├── AUTOENCODER_README.md [NOVO] (500+ linhas)
├── EXEMPLO_USO_AUTOENCODER.md [NOVO] (350+ linhas)
├── ARQUITETURA_AUTOENCODER.md [NOVO] (este arquivo)
└── IMPLEMENTACAO_AUTOENCODER.txt [NOVO]
```

## 🔌 Integrações

### Backend - Banco de Dados

```
SQL Server
├── sensor_data (existente)
│   └─ Alimenta treinamento e detecção
│
├── maintenance_orders (existente)
│   └─ Contexto para manutenção
│
├── optimization_results (existente)
│   └─ Calendário de manutenção
│
├── anomaly_detections [NOVO]
│   ├─ equipment_id, timestamp
│   ├─ Q, T2 (métricas)
│   ├─ is_anomaly, severity
│   └─ Created_at
│
└── anomaly_models [NOVO]
    ├─ model_name, model_arch
    ├─ latent_dim, window_size
    ├─ training_epochs
    └─ trained_at
```

### Frontend - Componentes React

```
Sidebar
├─ Home
├─ Database
├─ Generate Data
├─ Optimize
├─ Calendar [INTEGRADO COM ANOMALIAS]
├─ Anomalies [NOVO] ← Clique para ir ao dashboard
├─ Data View
└─ Settings

Anomalies Page [NOVO]
├─ Layout Principal
│  ├─ Header
│  ├─ Cards Resumidos (4 cards)
│  ├─ Controles (Treinar + Detectar + Filtros)
│  ├─ Alert (mensagens)
│  └─ Lista de Anomalias
│
Calendar Page [ATUALIZADO]
├─ Header
├─ Controles
├─ Alert
├─ Card: Resumo de Anomalias ← NOVO
│  ├─ Contagem total
│  ├─ Percentual
│  └─ Métricas (Q, T² médios e máximos)
└─ Lista de Manutenções
   └─ Badge 🚨 com contagem de anomalias
```

## 🧠 Arquitetura do Autoencoder

### MLPAutoEncoder

```
INPUT LAYER (11 features)
      ↓
LINEAR (11 → 32)
      ↓
RELU
      ↓
LINEAR (32 → 16)
      ↓
RELU
      ↓
LINEAR (16 → 8)
      ↓
RELU
      ↓
LINEAR (8 → 5)  ← LATENT SPACE (5 dimensões)
      ↓
LINEAR (5 → 8)
      ↓
RELU
      ↓
LINEAR (8 → 16)
      ↓
RELU
      ↓
LINEAR (16 → 32)
      ↓
RELU
      ↓
LINEAR (32 → 11)
      ↓
OUTPUT LAYER (11 features)
```

Parâmetros:
- Input: 11 features (correntes, ângulos, capacitância, tan delta)
- Encoder: [32, 16, 8] → 5
- Decoder: 5 → [8, 16, 32] → 11
- Total de pesos: ~2000

### CNNAutoEncoder

```
INPUT (1, seq_len)
      ↓
ENCODER:
  Conv1d(1, 16, k=3)
      ↓
  ReLU
      ↓
  MaxPool1d(2)
      ↓
  Conv1d(16, 8, k=3)
      ↓
  ReLU
      ↓
  MaxPool1d(2)
      ↓
  Conv1d(8, 4, k=3)
      ↓
  ReLU
      ↓
  Flatten → Linear → 5  ← LATENT SPACE
      ↓
DECODER:
  Linear → Reshape
      ↓
  ConvTranspose1d(4, 8, k=2, s=2)
      ↓
  ReLU
      ↓
  ConvTranspose1d(8, 16, k=2, s=2)
      ↓
  ReLU
      ↓
  ConvTranspose1d(16, 1, k=3)
      ↓
OUTPUT (1, seq_len)
```

Melhor para:
- Padrões sequenciais
- Degradação gradual
- Mudanças de comportamento

## 📊 Fluxo de Dados

```
TREINO:
sensor_data
  │
  └─→ Normalizar (StandardScaler)
       │
       └─→ Criar janelas (168h)
            │
            └─→ MLP/CNN Treinamento
                 │
                 ├─→ Forward pass
                 ├─→ Calcular MSELoss
                 ├─→ Backward pass
                 └─→ Update pesos
            │
            └─→ Salvar weights
                 │
                 └─→ anomaly_models

DETECÇÃO:
sensor_data (novos)
  │
  └─→ Normalizar (usar scaler do treino)
       │
       └─→ Criar janelas
            │
            └─→ MLP/CNN Forward
                 │
                 ├─→ Reconstruction (decoder)
                 └─→ Latent codes (encoder)
            │
            └─→ Calcular Métricas
                 │
                 ├─→ Q = MSE(input, output)
                 └─→ T² = sum(latent²)
            │
            └─→ Comparar com Threshold (95º percentil)
                 │
                 ├─→ Se Q > Q_threshold OU T² > T2_threshold
                 │   └─→ ANOMALIA
                 └─→ Senão
                     └─→ NORMAL
            │
            └─→ Salvar em anomaly_detections
```

## 🔄 Iteração do Treinamento

```
ÉPOCA 1:
  [Batch 1] loss = 0.0234
  [Batch 2] loss = 0.0198
  [Batch 3] loss = 0.0187
  Época 1 completa: avg_loss = 0.0206

ÉPOCA 2:
  [Batch 1] loss = 0.0189
  [Batch 2] loss = 0.0156
  [Batch 3] loss = 0.0143
  Época 2 completa: avg_loss = 0.0163

...

ÉPOCA 50:
  [Batch 1] loss = 0.0023
  [Batch 2] loss = 0.0019
  [Batch 3] loss = 0.0017
  Época 50 completa: avg_loss = 0.0020

✅ Treinamento Concluído!
Modelo aprendeu a reconstruir bem dados normais.
```

## 🎯 Matriz de Decisão

```
        T² Normal (< threshold)  |  T² Anômalo (> threshold)
─────────────────────────────────┼────────────────────────────
Q Normal | Normal                | Possível Anomalia Latente
(Q <θ)  | ✅ Comportamento OK   | ⚠️  Suspeito
─────────────────────────────────┼────────────────────────────
Q Anômalo| Possível Anomalia    | Definitiva Anomalia
(Q >θ)  | ⚠️  Suspeito          | 🚨 ANOMALIA CONFIRMADA
```

## 📈 Exemplo de Detecção

```
Dados Normais:
  Q = 0.0032  (< 0.0045) ✅
  T² = 0.0067 (< 0.0089) ✅
  Resultado: NORMAL ✅

Dados Ligeiramente Anômalos:
  Q = 0.0078  (> 0.0045) ⚠️
  T² = 0.0045 (< 0.0089) ✅
  Resultado: SUSPEITO ⚠️

Dados Definitivamente Anômalos:
  Q = 0.0156  (> 0.0045) 🚨
  T² = 0.0234 (> 0.0089) 🚨
  Resultado: ANOMALIA 🚨
```

## 🔐 Segurança e Performance

### Performance
```
Treino:
  - 7200 amostras
  - 168h window_size
  - 50 épocas
  - GPU (se disponível): ~1-2 minutos
  - CPU: ~5-10 minutos

Detecção:
  - 100 novos pontos
  - Forward pass: <50ms
  - Cálculo de métricas: <10ms
  - Total: <100ms
```

### Segurança
```
✅ Entrada validada (Pydantic)
✅ SQL injection protegido (parameterized queries)
✅ Normalização de dados
✅ Validação de tipos
✅ Error handling com try/except
```

## 🚀 Otimizações Futuras

```
Memória:
  └─ Quantização de pesos (int8)
  └─ Compressão de modelos
  └─ Streaming de dados

Velocidade:
  └─ ONNX runtime
  └─ TorchScript JIT
  └─ Batch processing

Acurácia:
  └─ Ensemble de modelos
  └─ Transfer learning
  └─ Fine-tuning adapatativo
```

---

**Diagrama atualizado**: 2025-11-26
**Versão**: 1.0
