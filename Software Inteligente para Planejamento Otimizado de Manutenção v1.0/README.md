# Sistema Inteligente para Planejamento Otimizado de Manutenção

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![TRL](https://img.shields.io/badge/TRL-9-success.svg)](https://en.wikipedia.org/wiki/Technology_readiness_level)

Sistema de otimização multi-objetivo para planejamento de manutenção preditiva de transformadores usando **Cadeias de Markov** e **Algoritmo Genético NSGA-II**.

## Sumário

- [Visão Geral](#visão-geral)
- [Características](#características)
- [Instalação](#instalação)
- [Guia de Uso](#guia-de-uso)
- [Arquitetura](#arquitetura)
- [Configuração](#configuração)
- [Exemplos](#exemplos)
- [Documentação](#documentação)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## Visão Geral

Este sistema implementa uma abordagem inovadora para planejamento de manutenção preditiva, combinando:

- **Modelagem de Estados**: Cadeias de Markov para modelar transições entre estados de saúde dos equipamentos
- **Otimização Multi-Objetivo**: NSGA-II para encontrar o melhor compromisso entre custo e indisponibilidade
- **Análise de Dados em Tempo Real**: Processamento de dados de sensores (buchas de transformadores)
- **Visualizações Avançadas**: Fronteiras de Pareto, séries temporais e análises de criticidade

### Modelo de Estados

```
Normal → Degradado 1 → Degradado 2 → Degradado 3 → Falha
```

Cada estado possui:
- Taxa de transição (λᵢ)
- Custo operacional
- Horas de indisponibilidade

### Objetivos de Otimização

1. **Minimizar Custo Total**: Custo operacional + custo de manutenção
2. **Minimizar Indisponibilidade**: Horas de parada esperadas

## Características

### Core

- ✅ Modelagem de Markov com 5 estados de saúde
- ✅ Otimização NSGA-II configurável
- ✅ Análise da fronteira de Pareto
- ✅ Seleção automática de solução (ponto de joelho, custo mínimo, etc.)
- ✅ Logging estruturado
- ✅ Configuração via YAML

### Processamento de Dados

- ✅ Carregamento de CSV, Excel, Parquet e JSON
- ✅ Validação robusta de dados
- ✅ Pré-processamento automático
- ✅ Tratamento de valores faltantes
- ✅ Normalização de formatos

### Análise

- ✅ Cálculo de taxa de degradação (regressão linear)
- ✅ Classificação de estado de saúde
- ✅ Ranking de criticidade de equipamentos
- ✅ Predição de tempo até falha
- ✅ Simulação Monte Carlo de trajetórias

### Visualização

- ✅ Gráficos de fronteira de Pareto (2D e 3D)
- ✅ Séries temporais com tendências
- ✅ Análise dos equipamentos mais críticos
- ✅ Relatórios em texto, Excel e gráficos

## Instalação

### Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/your-repo/maintenance-optimization.git
cd maintenance-optimization

# 2. Crie um ambiente virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Instale o pacote em modo de desenvolvimento
pip install -e .
```

### Verificar Instalação

```bash
python -c "from src.models import MarkovChainModel; print('Instalação OK!')"
```

## Guia de Uso

### Uso Básico

```python
from src.data import DataLoader, DataPreprocessor
from src.models import MarkovChainModel
from src.optimization import MaintenanceProblem, NSGA2Solver, ParetoAnalyzer
import numpy as np

# 1. Carregar dados
loader = DataLoader()
data = loader.load_csv("data/input/ordens_servico.csv")

# 2. Pré-processar
preprocessor = DataPreprocessor()
data = preprocessor.normalize_numeric_columns(data)
data = preprocessor.add_default_unavailability_fields(data)

# 3. Criar modelo de Markov
markov = MarkovChainModel(n_states=5)
rates = np.array([0.01, 0.02, 0.03, 0.04])  # Taxas de transição
transition_matrix = markov.build_transition_matrix(rates)

# 4. Definir custos
operational_costs = np.array([100, 200, 300, 400, 500])
unavailability_costs = np.array([2, 4, 8, 16, 48])

# 5. Criar problema de otimização
problem = MaintenanceProblem(
    transition_matrix=transition_matrix,
    operational_costs=operational_costs,
    unavailability_costs=unavailability_costs,
    time_offset=30  # dias desde última medição
)

# 6. Resolver com NSGA-II
solver = NSGA2Solver()
pareto_front = solver.solve(problem)

# 7. Analisar resultados
analyzer = ParetoAnalyzer()
best_idx, best_solution = analyzer.select_best_solution(
    pareto_front,
    criterion="knee_point"
)

print(f"Melhor solução:")
print(f"  Tempo até manutenção: {best_solution['t']:.0f} dias")
print(f"  Custo: R$ {best_solution['Custo']:.2f}")
print(f"  Indisponibilidade: {best_solution['Indisponibilidade']:.2f} horas")

# 8. Salvar resultados
loader.save_dataframe(pareto_front, "data/output/fronteira_pareto.xlsx")
```

### Interface de Linha de Comando (CLI)

```bash
# Ver ajuda
python scripts/run_optimization.py --help

# Executar otimização
python scripts/run_optimization.py \
    --input data/input/ordens_servico.csv \
    --output data/output/resultados.xlsx \
    --selection-criterion knee_point

# Processar dados de sensores
python scripts/process_sensors.py \
    --input DataWide_20250101_20250201.parquet \
    --output data/output/entrada_sistema.json
```

## Arquitetura

```
Sistema de Manutenção Preditiva/
├── config/                      # Configurações YAML
│   ├── default.yaml             # Configuração geral
│   ├── field_mappings.yaml      # Mapeamento de campos
│   ├── nsga_params.yaml         # Parâmetros NSGA-II
│   └── thresholds.yaml          # Limiares de saúde
│
├── src/                         # Código fonte
│   ├── data/                    # Camada de dados
│   │   ├── loaders.py           # Carregamento de arquivos
│   │   ├── validators.py        # Validação de dados
│   │   └── preprocessors.py     # Pré-processamento
│   │
│   ├── models/                  # Modelos matemáticos
│   │   ├── markov.py            # Cadeia de Markov
│   │   └── degradation.py       # Modelo de degradação
│   │
│   ├── optimization/            # Otimização
│   │   ├── problem.py           # Definição do problema
│   │   ├── solver.py            # Solver NSGA-II
│   │   └── pareto.py            # Análise de Pareto
│   │
│   ├── visualization/           # Visualizações
│   │   └── ...                  # (módulos de plots)
│   │
│   └── utils/                   # Utilitários
│       ├── config_loader.py     # Carregador de config
│       ├── logging_config.py    # Configuração de logs
│       └── metrics.py           # Cálculo de métricas
│
├── scripts/                     # Scripts executáveis
│   ├── run_optimization.py      # CLI principal
│   └── process_sensors.py       # Processar sensores
│
├── data/                        # Dados
│   ├── input/                   # Dados de entrada
│   ├── output/                  # Resultados
│   └── examples/                # Exemplos
│
├── tests/                       # Testes unitários
├── docs/                        # Documentação
├── requirements.txt             # Dependências
├── setup.py                     # Instalação
└── README.md                    # Este arquivo
```

## Configuração

### Arquivos de Configuração

#### `config/default.yaml`

Configurações gerais do sistema (logging, caminhos, visualização).

#### `config/nsga_params.yaml`

Parâmetros do algoritmo NSGA-II:

```yaml
algorithm:
  population_size: 200
  max_evaluations: 4000

operators:
  crossover:
    type: "SBX"
    probability: 1.0
    distribution_index: 20

  mutation:
    type: "Polynomial"
    distribution_index: 20
```

#### `config/thresholds.yaml`

Limiares de classificação de saúde:

```yaml
bushings:
  corrente_fuga:
    normal:
      max: 0.5  # mA
    degradado1:
      min: 0.5
      max: 1.0
    # ... outros estados
```

#### `config/field_mappings.yaml`

Mapeamento de campos para diferentes tipos de análise (DGA, FQ).

### Variáveis de Ambiente

```bash
export MAINTENANCE_CONFIG_DIR=/caminho/para/config
export MAINTENANCE_LOG_LEVEL=INFO
```

## Exemplos

### Exemplo 1: Otimização de Uma Ordem de Serviço

```python
import numpy as np
from src.models import MarkovChainModel
from src.optimization import MaintenanceProblem, NSGA2Solver

# Dados da OS
rates = np.array([0.015, 0.025, 0.035, 0.045])
costs = np.array([150, 250, 350, 450, 600])
unavailability = np.array([3, 5, 10, 20, 50])

# Criar e resolver
markov = MarkovChainModel()
T = markov.build_transition_matrix(rates)

problem = MaintenanceProblem(T, costs, unavailability, time_offset=45)
solver = NSGA2Solver()
pareto = solver.solve(problem)

print(pareto.head())
```

### Exemplo 2: Processar Dados de Sensores

```python
from src.data import DataLoader
from src.models import DegradationModel
import pandas as pd

# Carregar dados de sensores
loader = DataLoader()
sensor_data = loader.load_parquet("DataWide_20250101_20250201.parquet")

# Analisar degradação de um equipamento
equipment_data = sensor_data[
    sensor_data["equipment_id"] == "SPGR.ATF1A"
]

degradation_model = DegradationModel()
analysis = degradation_model.analyze_equipment_health(
    equipment_id="SPGR.ATF1A",
    time_series=equipment_data,
    value_column="corrente_fuga",
    time_column="timestamp"
)

print(f"Estado: {analysis['state_name']}")
print(f"Taxa de degradação: {analysis['degradation_rate']:.6f} mA/dia")
print(f"Tempo até falha: {analysis['time_to_failure_days']} dias")
```

### Exemplo 3: Ranking de Equipamentos Críticos

```python
from src.models import DegradationModel

# Analisar múltiplos equipamentos
equipment_ids = ["SPGR.ATF1A", "SPGR.ATF1B", "SPGR.ATF2A"]
analyses = []

for eq_id in equipment_ids:
    eq_data = sensor_data[sensor_data["equipment_id"] == eq_id]
    analysis = degradation_model.analyze_equipment_health(
        eq_id, eq_data, "corrente_fuga"
    )
    analyses.append(analysis)

# Ranking por criticidade
top_critical = degradation_model.rank_equipment_by_criticality(
    analyses, top_n=3
)

for i, eq in enumerate(top_critical, 1):
    print(f"{i}. {eq['equipment_id']} - Score: {eq['criticality_score']:.2f}")
```

## Documentação

### Documentação Completa

A documentação completa está disponível em `docs/`:

- **Guia de Instalação**: `docs/guia_instalacao.md`
- **Manual do Usuário**: `docs/manual_usuario.md`
- **Referência da API**: `docs/api_reference.md`
- **Algoritmos**: `docs/algoritmos.md`
- **Roadmap**: `docs/roadmap.md`

### API Reference

#### MarkovChainModel

```python
from src.models import MarkovChainModel

model = MarkovChainModel(n_states=5)
T = model.build_transition_matrix(rates)
probs = model.calculate_state_probabilities(n_cycles=100)
mttf = model.calculate_mean_time_to_failure(initial_state=0)
```

#### NSGA2Solver

```python
from src.optimization import NSGA2Solver

solver = NSGA2Solver()
pareto_front = solver.solve(problem)
info = solver.get_algorithm_info()
```

#### ParetoAnalyzer

```python
from src.optimization import ParetoAnalyzer

analyzer = ParetoAnalyzer()
idx, solution = analyzer.select_best_solution(pareto_front, "knee_point")
analysis = analyzer.analyze_pareto_front(pareto_front)
```

## Testes

```bash
# Executar todos os testes
pytest tests/

# Executar com cobertura
pytest --cov=src tests/

# Executar testes específicos
pytest tests/test_markov.py
```

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Padrões de Código

- Siga o PEP 8
- Use type hints
- Documente funções e classes
- Escreva testes para novas funcionalidades

## Roadmap

- [x] Refatoração completa da arquitetura
- [x] Configuração via YAML
- [x] Logging estruturado
- [ ] Testes unitários completos (>80% cobertura)
- [ ] Interface Web (Dashboard)
- [ ] API REST
- [ ] Containerização (Docker)
- [ ] CI/CD Pipeline
- [ ] Documentação automática (Sphinx)

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autores

- Equipe de Manutenção Preditiva

## Agradecimentos

- Framework jMetal para otimização multi-objetivo
- Comunidade Python científico (NumPy, Pandas, Matplotlib)

## Contato

Para dúvidas e suporte:
- Email: suporte@exemplo.com
- Issues: https://github.com/your-repo/issues

---

**Versão:** 2.0.0
**TRL:** 9 (Pronto para Produção)
**Data:** 2025
