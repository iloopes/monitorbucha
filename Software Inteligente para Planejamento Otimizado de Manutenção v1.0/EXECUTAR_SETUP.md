# 🚀 Guia Rápido - Setup do Banco de Dados

## Seu Servidor SQL

**Servidor:** `DESKTOP-0L1FQAQ\KUZUSHI`
**Banco:** `MaintenanceDB`

## Opção 1: Executar via SQL Server Management Studio (SSMS)

### Passo a Passo:

1. **Abrir SSMS**
   - Iniciar SQL Server Management Studio

2. **Conectar ao Servidor**
   - Servidor: `DESKTOP-0L1FQAQ\KUZUSHI`
   - Autenticação: Windows Authentication
   - Clicar em "Connect"

3. **Executar Script**
   - File → Open → File...
   - Selecionar: `database/setup_database.sql`
   - Pressionar F5 ou clicar em "Execute"

4. **Verificar**
   - Expandir "Databases" no Object Explorer
   - Verificar se "MaintenanceDB" aparece
   - Expandir "MaintenanceDB" → "Tables"
   - Deve ver: sensor_data, maintenance_orders, optimization_results, pareto_frontier

## Opção 2: Executar via Linha de Comando (SQLCMD)

```cmd
cd "C:\Users\isl_7\Desktop\Software Inteligente para Planejamento Otimizado de Manutenção v1.0\Software Inteligente para Planejamento Otimizado de Manutenção v1.0"

sqlcmd -S DESKTOP-0L1FQAQ\KUZUSHI -E -i database\setup_database.sql
```

## Opção 3: Executar via API (Recomendado)

### 1. Instalar Dependências

```bash
pip install fastapi uvicorn pyodbc
```

### 2. Iniciar API

```bash
cd api
python main.py
```

### 3. Abrir Frontend

Navegador: http://localhost:8000

### 4. Configurar no Frontend

1. Preencher:
   - Servidor: `DESKTOP-0L1FQAQ\KUZUSHI`
   - Banco: `MaintenanceDB`
   - ✓ Marcar "Autenticação Windows"

2. Clicar em "Conectar ao Banco"

3. Clicar em "Criar Tabelas"

## Opção 4: Executar via Python

```python
from src.database import SQLServerConnector, DatabaseManager

# Conectar
connector = SQLServerConnector(
    server="DESKTOP-0L1FQAQ\\KUZUSHI",
    database="MaintenanceDB",
    trusted_connection=True
)
connector.connect()

# Criar tabelas
manager = DatabaseManager(connector)
manager.create_tables()

print("✓ Banco de dados configurado!")
```

## Verificar Instalação

### Via SSMS:

```sql
USE MaintenanceDB;

-- Listar tabelas
SELECT name FROM sys.tables;

-- Listar views
SELECT name FROM sys.views;

-- Contar registros (deve ser 0 inicialmente)
SELECT COUNT(*) FROM sensor_data;
```

### Via Python:

```python
from src.database import SQLServerConnector

connector = SQLServerConnector(
    server="DESKTOP-0L1FQAQ\\KUZUSHI",
    database="MaintenanceDB",
    trusted_connection=True
)
connector.connect()

# Verificar tabelas
if connector.table_exists("sensor_data"):
    print("✓ Tabela sensor_data existe!")

if connector.table_exists("maintenance_orders"):
    print("✓ Tabela maintenance_orders existe!")
```

## Problemas Comuns

### Erro: "Servidor não encontrado"

**Solução:**
1. Verificar se SQL Server está rodando:
   - Services → SQL Server (KUZUSHI) → Start

2. Verificar nome do servidor:
   ```cmd
   sqlcmd -L
   ```

### Erro: "Login failed"

**Solução:**
- Usar Autenticação Windows (trusted_connection=True)
- Ou criar um usuário SQL:
  ```sql
  CREATE LOGIN seu_usuario WITH PASSWORD = 'sua_senha';
  USE MaintenanceDB;
  CREATE USER seu_usuario FOR LOGIN seu_usuario;
  GRANT ALL TO seu_usuario;
  ```

### Erro: "Database already exists"

**Solução:**
- O banco já foi criado antes
- Para recriar, execute:
  ```sql
  USE master;
  DROP DATABASE MaintenanceDB;
  -- Depois execute setup_database.sql novamente
  ```

## Próximos Passos

Após criar o banco:

### 1. Gerar Dados de Teste

**Via Frontend:**
- http://localhost:8000
- Configurar parâmetros
- Clicar em "Gerar Dados"

**Via Python:**
```python
from src.data.synthetic_generator import VirtualBushingGenerator
from src.database import SQLServerConnector, DatabaseManager

# Gerar
generator = VirtualBushingGenerator(seed=42)
sensor_data, orders = generator.generate_scenario(
    "teste_inicial", 5, 7, "medium"
)

# Salvar
connector = SQLServerConnector(
    server="DESKTOP-0L1FQAQ\\KUZUSHI",
    database="MaintenanceDB",
    trusted_connection=True
)
connector.connect()

manager = DatabaseManager(connector)
manager.insert_sensor_data(sensor_data)
manager.insert_maintenance_orders(orders)

print(f"✓ {len(sensor_data)} registros inseridos!")
```

### 2. Consultar Dados

```sql
-- Ver últimas leituras
SELECT TOP 10 * FROM sensor_data
ORDER BY timestamp DESC;

-- Ver equipamentos críticos
SELECT * FROM vw_critical_equipment;

-- Ver ordens de serviço
SELECT * FROM maintenance_orders;
```

### 3. Executar Otimização

```bash
python scripts/run_optimization.py \
    --input "banco_de_dados" \
    --output data/output/resultados.xlsx
```

## Estrutura Criada

```
MaintenanceDB/
├── Tables/
│   ├── sensor_data              (dados de sensores)
│   ├── maintenance_orders       (ordens de serviço)
│   ├── optimization_results     (resultados NSGA-II)
│   └── pareto_frontier          (fronteira de Pareto)
│
├── Views/
│   ├── vw_latest_sensor_readings      (últimas leituras)
│   ├── vw_critical_equipment          (equipamentos críticos)
│   └── vw_maintenance_calendar        (calendário de manutenção)
│
└── Stored Procedures/
    └── sp_cleanup_old_data      (limpeza de dados antigos)
```

## Contato

Para problemas ou dúvidas, consulte:
- BUCHA_VIRTUAL_README.md
- README.md

---

**Servidor:** DESKTOP-0L1FQAQ\KUZUSHI
**Status:** Pronto para uso! ✓
