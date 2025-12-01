# Guia Rápido - Sistema de Manutenção Preditiva v2.0

## ✅ Status da Instalação

- ✓ Python 3.11.9 instalado
- ✓ Virtual environment criado (`venv/`)
- ⏳ Instalando dependências...

## 🚀 Como Usar o Projeto

### 1. Ativar o Ambiente Virtual

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Verificar Instalação

```bash
# Teste rápido
python quick_test.py
```

### 3. Gerar Dados de Teste

```bash
# Gera arquivo CSV com dados sintéticos
python test_synthetic_data.py
```

Isso criará um arquivo em `data/input/dados_teste.csv`

### 4. Executar Otimização

```bash
# Otimização simples
python scripts/run_optimization.py \
    -i data/input/dados_teste.csv \
    -o data/output/resultados.xlsx

# Com critério específico
python scripts/run_optimization.py \
    -i data/input/dados_teste.csv \
    -o data/output/resultados.xlsx \
    --selection-criterion min_cost

# Ver todas as opções
python scripts/run_optimization.py --help
```

### 5. Consultar Resultados

Os resultados serão salvos em:
- `data/output/resultados.xlsx` - Calendário otimizado de manutenção
- `data/output/fronteiras_de_pareto.xlsx` - Fronteiras de Pareto para cada OS

## 📊 Estrutura de Dados

### Arquivo de Entrada (CSV)

Colunas obrigatórias:
- `OS_Id` - ID da ordem de serviço
- `MotivoManutencao` - Tipo de análise (DGA, FQ)
- `estado_atual` - Estado de saúde atual (0-4)
- `data_medicao` - Data da última medição

Colunas para taxas de transição:
- `taxa_0`, `taxa_1`, `taxa_2`, `taxa_3` - Taxas entre estados

Colunas para custos operacionais:
- `custo_0`, `custo_1`, `custo_2`, `custo_3`, `custo_4` - Custo por estado

Colunas para indisponibilidade:
- `indisponibilidade_0` a `indisponibilidade_4` - Horas de parada por estado

## 🔧 Configurações

Modificar em `config/`:

- **default.yaml** - Configurações gerais (logging, caminhos)
- **nsga_params.yaml** - Parâmetros do algoritmo (população, gerações)
- **thresholds.yaml** - Limiares de classificação de saúde
- **field_mappings.yaml** - Mapeamento de colunas

## 📈 Exemplo de Uso Completo

```bash
# 1. Ativar ambiente
venv\Scripts\activate

# 2. Gerar dados de teste
python test_synthetic_data.py

# 3. Executar otimização
python scripts/run_optimization.py \
    -i data/input/dados_teste.csv \
    -o data/output/resultados.xlsx \
    --top 5

# 4. Verificar resultados em data/output/
```

## 🗄️ Banco de Dados SQL Server (Opcional)

Se você tiver SQL Server instalado:

```bash
# Conectar e criar banco
python -c "
from src.database import SQLServerConnector, DatabaseManager

connector = SQLServerConnector(
    server='DESKTOP-0L1FQAQ\\KUZUSHI',
    database='MaintenanceDB',
    trusted_connection=True
)
connector.connect()
manager = DatabaseManager(connector)
manager.create_tables()
print('✓ Banco criado!')
"
```

## 📚 Documentação Completa

- Leia [README.md](README.md) para documentação completa
- Consulte [docs/](docs/) para guias detalhados
- Veja exemplos em [data/examples/](data/examples/)

## ⚡ Dicas

1. **Primeira execução:** Use dados pequenos para testar
2. **Parâmetros NSGA-II:** Aumente população/gerações para resultados melhores (mais lento)
3. **Logging:** Use `--log-level DEBUG` para mais informações
4. **Validação:** Use `--no-validation` apenas se tiver certeza dos dados

## 🆘 Problemas Comuns

### Erro: "ModuleNotFoundError"
- Verifique se o ambiente virtual está ativado
- Reinstale: `pip install -r requirements.txt`

### Erro: "Arquivo não encontrado"
- Verifique o caminho do arquivo de entrada
- Use caminhos absolutos ou relativos corretos

### Otimização lenta
- Reduza população/gerações em `config/nsga_params.yaml`
- Ou espere mais tempo (é normal para grandes datasets)

## 📞 Suporte

Para mais informações:
- Email: suporte@exemplo.com
- Issues: https://github.com/your-repo/issues
- Documentação: Consulte `docs/`

---

**Versão:** 2.0.0
**Python:** 3.11+
**Status:** ✓ Pronto para usar
