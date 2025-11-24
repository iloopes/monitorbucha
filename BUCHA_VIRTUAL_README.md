# Sistema de Bucha Virtual

## Visão Geral

O **Sistema de Bucha Virtual** é um componente do Sistema de Manutenção Preditiva que permite gerar dados sintéticos de buchas de transformador e armazená-los em um banco de dados SQL Server. Inclui uma interface web para controle total da geração de dados.

## Características

- ✅ **Gerador de Dados Sintéticos**: Simula comportamento real de buchas
- ✅ **Integração SQL Server**: Armazena dados em banco profissional
- ✅ **API REST**: FastAPI para controle programático
- ✅ **Interface Web**: Frontend moderno e intuitivo
- ✅ **Degradação Realista**: Modela deterioração ao longo do tempo
- ✅ **Eventos Aleatórios**: Simula anomalias ocasionais
- ✅ **Múltiplos Cenários**: Suporta diferentes taxas de degradação

## Arquitetura

```
Sistema de Bucha Virtual/
├── src/data/synthetic_generator.py    # Gerador de dados
├── src/database/sql_server.py         # Integração SQL Server
├── api/main.py                        # API REST (FastAPI)
├── frontend/                          # Interface Web
│   ├── templates/index.html
│   └── static/
│       ├── style.css
│       └── app.js
├── config/database.yaml               # Configuração DB
└── database/schema.sql                # Schema do banco
```

## Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Novas dependências adicionadas:
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `pydantic` - Validação de dados
- `pyodbc` - Conector SQL Server

### 2. Instalar SQL Server Driver

**Windows:**
- Baixe o ODBC Driver 17 para SQL Server:
  https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Linux:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list)"
sudo apt-get update
sudo apt-get install -y msodbcsql17
```

### 3. Configurar SQL Server

Edite `config/database.yaml`:

```yaml
sqlserver:
  server: "localhost"
  database: "MaintenanceDB"
  trusted_connection: true  # ou false para user/password
  username: ""
  password: ""
```

### 4. Criar Banco de Dados

Execute o script SQL:

```sql
CREATE DATABASE MaintenanceDB;
GO

USE MaintenanceDB;
GO

-- Execute database/schema.sql
```

Ou use a API (após iniciar o servidor):
```bash
POST http://localhost:8000/api/database/init
```

## Uso

### Iniciar o Sistema

#### 1. Iniciar API

```bash
# Usando uvicorn diretamente
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou usando python
python api/main.py
```

A API estará disponível em: http://localhost:8000

#### 2. Acessar Frontend

Abra o navegador em: http://localhost:8000

#### 3. Configurar Banco de Dados

No frontend:
1. Preencha as credenciais do SQL Server
2. Clique em "Conectar ao Banco"
3. Clique em "Criar Tabelas"

### Gerar Dados

#### Via Frontend

1. Configure os parâmetros:
   - Número de buchas (1-100)
   - Período em dias (1-365)
   - Frequência de medição (horas)
   - Taxa de degradação (baixa/média/alta)

2. Clique em "Gerar Dados"

3. Os dados serão automaticamente salvos no banco de dados

#### Via API

```python
import requests

# Gerar dados
response = requests.post(
    'http://localhost:8000/api/data/generate',
    json={
        'n_bushings': 10,
        'days': 30,
        'frequency_hours': 1,
        'degradation_rate': 'medium',
        'save_to_database': True,
        'scenario_name': 'cenario_teste'
    }
)

print(response.json())
```

#### Via Python

```python
from src.data.synthetic_generator import VirtualBushingGenerator
from src.database import SQLServerConnector, DatabaseManager

# Criar gerador
generator = VirtualBushingGenerator(seed=42)

# Gerar cenário
sensor_data, maintenance_orders = generator.generate_scenario(
    scenario_name="teste",
    n_bushings=10,
    days=30,
    degradation_rate="medium"
)

# Salvar no banco
connector = SQLServerConnector(
    server="localhost",
    database="MaintenanceDB",
    trusted_connection=True
)
connector.connect()

manager = DatabaseManager(connector)
manager.create_tables()
manager.insert_sensor_data(sensor_data)
manager.insert_maintenance_orders(maintenance_orders)

print(f"Dados salvos: {len(sensor_data)} registros de sensores")
```

## API Endpoints

### Health Check
```http
GET /api/health
```

### Configurar Banco de Dados
```http
POST /api/database/configure
Content-Type: application/json

{
  "server": "localhost",
  "database": "MaintenanceDB",
  "trusted_connection": true
}
```

### Inicializar Banco de Dados
```http
POST /api/database/init
```

### Gerar Dados
```http
POST /api/data/generate
Content-Type: application/json

{
  "n_bushings": 10,
  "days": 30,
  "frequency_hours": 1,
  "degradation_rate": "medium",
  "save_to_database": true,
  "scenario_name": "cenario_01"
}
```

### Buscar Dados de Sensores
```http
GET /api/data/sensor?equipment_id=SPGR.ATF1&limit=100
```

### Buscar Ordens de Serviço
```http
GET /api/data/orders?equipment_id=SPGR.ATF1
```

### Listar Buchas
```http
GET /api/bushings/list
```

## Modelo de Dados

### Tabela: sensor_data

Armazena leituras de sensores das buchas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INT | ID único |
| timestamp | DATETIME | Data/hora da leitura |
| equipment_id | VARCHAR | ID do equipamento |
| localizacao | VARCHAR | Localização física |
| corrente_fuga | FLOAT | Corrente de fuga (mA) |
| tg_delta | FLOAT | Tangente Delta (%) |
| capacitancia | FLOAT | Capacitância (pF) |
| estado_saude | INT | 0-4 (Normal a Falha) |
| temperatura_ambiente | FLOAT | Temperatura (°C) |
| umidade_relativa | FLOAT | Umidade (%) |

### Tabela: maintenance_orders

Ordens de serviço geradas a partir dos dados.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| os_id | VARCHAR | ID único da OS |
| equipment_id | VARCHAR | Equipamento |
| mf_dga | INT | Estado atual |
| mf_dga_data | DATETIME | Data da medição |
| dga_taxa_* | FLOAT | Taxas de transição |
| dga_custo_* | FLOAT | Custos por estado |
| dga_indisponibilidade_* | FLOAT | Horas de indisponibilidade |

## Configuração de Bucha

### Parâmetros Principais

```python
from src.data.synthetic_generator import BushinConfig

config = BushinConfig(
    equipment_id="SPGR.ATF1",
    localizacao="SPGR",
    tipo_transformador="ATF1",
    tensao_nominal=138.0,  # kV

    # Estado inicial
    estado_inicial=0,  # 0=Normal
    corrente_fuga_inicial=0.3,  # mA
    tg_delta_inicial=0.3,  # %
    capacitancia_nominal=300.0,  # pF

    # Degradação
    taxa_degradacao_corrente=0.001,  # mA/dia
    taxa_degradacao_tg=0.0005,  # %/dia
    taxa_variacao_capacitancia=0.01,  # %/dia

    # Ruído
    ruido_corrente=0.05,  # mA
    ruido_tg=0.02,  # %
    ruido_capacitancia=5.0  # pF
)
```

### Taxa de Degradação

- **Baixa** (0.0005 mA/dia): Equipamento novo, manutenção regular
- **Média** (0.001 mA/dia): Equipamento normal
- **Alta** (0.003 mA/dia): Equipamento envelhecido, condições adversas

## Cenários de Uso

### 1. Teste de Sistema

Gerar dados para testar o sistema de otimização:

```python
generator = VirtualBushingGenerator(seed=42)
sensor_data, orders = generator.generate_scenario(
    scenario_name="teste_sistema",
    n_bushings=5,
    days=7,
    degradation_rate="medium"
)
```

### 2. Treinamento de Modelo

Gerar grande volume de dados para ML:

```python
generator = VirtualBushingGenerator()
sensor_data, orders = generator.generate_scenario(
    scenario_name="treinamento_ml",
    n_bushings=100,
    days=365,
    degradation_rate="medium"
)
```

### 3. Demonstração

Simular cenário com equipamentos em diferentes estados:

```python
generator = VirtualBushingGenerator(seed=123)

# 70% normal, 20% degradado1, 10% degradado2
for i in range(10):
    estado = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
    config = BushinConfig(
        equipment_id=f"DEMO.EQ{i}",
        estado_inicial=estado,
        corrente_fuga_inicial=0.3 + (estado * 0.3)
    )
    generator.add_bushing(config)

sensor_data = generator.generate_data(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)
```

## Integração com Sistema Principal

### Fluxo Completo

1. **Gerar Dados** → Bucha Virtual
2. **Salvar no Banco** → SQL Server
3. **Buscar Dados** → API ou SQL
4. **Executar Otimização** → scripts/run_optimization.py
5. **Visualizar Resultados** → Frontend

### Exemplo de Integração

```python
from src.data.synthetic_generator import VirtualBushingGenerator
from src.database import SQLServerConnector, DatabaseManager
from src.data import DataLoader
from src.optimization import NSGA2Solver, ParetoAnalyzer

# 1. Gerar dados
generator = VirtualBushingGenerator()
sensor_data, orders = generator.generate_scenario(
    "integracao_completa", 10, 30, "medium"
)

# 2. Salvar no banco
connector = SQLServerConnector()
connector.connect()
manager = DatabaseManager(connector)
manager.insert_sensor_data(sensor_data)
manager.insert_maintenance_orders(orders)

# 3. Executar otimização
# Use scripts/run_optimization.py ou código próprio

# 4. Resultados ficam salvos no banco
```

## Troubleshooting

### Erro: Driver não encontrado

```
pyodbc.Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server'")
```

**Solução**: Instale o ODBC Driver 17 (veja seção de instalação)

### Erro: Conexão recusada

```
pyodbc.Error: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]TCP Provider: No connection could be made')
```

**Solução**:
1. Verifique se SQL Server está rodando
2. Confirme servidor/porta corretos
3. Verifique firewall
4. Habilite TCP/IP no SQL Server Configuration Manager

### Erro: Permissão negada

```
pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC SQL Server Driver]Login failed for user")
```

**Solução**:
1. Verifique credenciais
2. Use Trusted Connection se possível
3. Garanta que usuário tem permissões no banco

## Performance

### Otimizações

- **Inserção em lote**: Use `batch_size` em `config/database.yaml`
- **Índices**: Schema inclui índices otimizados
- **Conexão persistente**: Reutilize `SQLServerConnector`

### Benchmarks

| Operação | Registros | Tempo |
|----------|-----------|-------|
| Gerar dados | 10 buchas, 30 dias | ~2s |
| Inserir sensores | 7.200 registros | ~5s |
| Buscar últimas leituras | 100 equipamentos | ~0.1s |

## Próximos Passos

- [ ] Adicionar mais métricas (temperatura óleo, pressão, etc.)
- [ ] Suportar outros tipos de equipamentos
- [ ] Exportar dados para CSV/Excel
- [ ] Visualizações em tempo real
- [ ] Alertas automáticos
- [ ] Dashboard de monitoramento

## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQL Server ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/)
- [PyODBC Documentation](https://github.com/mkleehammer/pyodbc/wiki)

---

**Versão:** 2.0.0
**Data:** 2025
**Autor:** Equipe de Manutenção Preditiva
