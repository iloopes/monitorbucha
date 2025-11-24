# Guia de Instalação e Execução Local

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11 (conforme seu setup atual)
- macOS ou Linux (também suportados)

### Software Necessário
- **Python 3.8+** (testado com 3.9+)
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para versionamento)

---

## 1️⃣ Verificar Instalação do Python

Abra o **Prompt de Comando (CMD)** ou **PowerShell** e execute:

```bash
python --version
```

**Esperado:** Algo como `Python 3.9.x` ou superior

Se não funcionar, [baixe Python aqui](https://www.python.org/downloads/) e instale marcando a opção "Add Python to PATH"

---

## 2️⃣ Criar Ambiente Virtual (Recomendado)

Ambientes virtuais isolam dependências do projeto, evitando conflitos.

### No Prompt de Comando:

```bash
# Navegue até a pasta do projeto
cd "C:\Users\isl_7\OneDrive\Área de Trabalho\Software Inteligente para Planejamento Otimizado de Manutenção v1.0\Software Inteligente para Planejamento Otimizado de Manutenção v1.0"

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
venv\Scripts\activate

# (macOS/Linux)
source venv/bin/activate
```

Após ativar, você verá `(venv)` no início da linha de comando.

---

## 3️⃣ Instalar Dependências

Com o ambiente ativo, execute:

```bash
pip install --upgrade pip
```

Depois instale os pacotes necessários:

```bash
pip install pandas numpy jmetal openpyxl tqdm
```

### Detalhamento das Dependências:

| Pacote | Versão | Função |
|--------|--------|--------|
| **pandas** | ≥1.3.0 | Manipulação de dados (DataFrames) |
| **numpy** | ≥1.20.0 | Operações numéricas e álgebra linear |
| **jmetal** | ≥5.9.0 | Algoritmo NSGA-II de otimização |
| **openpyxl** | ≥3.0.0 | Escrever arquivos Excel |
| **tqdm** | ≥4.60.0 | Barra de progresso |

### Verificar Instalação:

```bash
pip list
```

Deve listar todos os pacotes acima.

---

## 4️⃣ Preparar Arquivos

A estrutura de pasta deve ser assim:

```
projeto/
├── ia_ManutencaoProgramadaOS.py
├── markov.py
├── otimizacao_libs.py
├── otimiza_os.ipynb
├── dados_testes_soad.csv        ← Arquivo de entrada
├── PeD1804_AECM.eam
├── venv/                         ← Seu ambiente virtual
├── fronteiras_de_pareto.xlsx     ← Saída (criado após execução)
└── ANALISE_COMPLETA.md           ← Documentação
```

### Arquivo de Dados (`dados_testes_soad.csv`)

Você precisa de um CSV com as colunas:

```
OS_Id,MotivoManutencao,MF_DGA,MF_FQ,MF_DGA_DATA,MF_FQ_DATA,DGA_TAXA_N,DGA_TAXA_D1,DGA_TAXA_D2,DGA_TAXA_D3,DGA_CUSTO_N,DGA_CUSTO_D1,DGA_CUSTO_D2,DGA_CUSTO_D3,DGA_CUSTO_F,FQ_TAXA_N,FQ_TAXA_D1,FQ_TAXA_D2,FQ_TAXA_D3,FQ_CUSTO_N,FQ_CUSTO_D1,FQ_CUSTO_D2,FQ_CUSTO_D3,FQ_CUSTO_F,...
```

**Colunas obrigatórias:**
- `OS_Id`: ID único da ordem de serviço
- `MotivoManutencao`: "Coleta e análise óleo cromatográfica" ou "Coleta e análise óleo: físico-química"
- `MF_DGA`: Estado atual (0=N, 1=D1, 2=D2, 3=D3)
- `MF_DGA_DATA`: Data da última coleta (ex: 2024-11-10)
- Taxas e custos conforme tipo de análise

---

## 5️⃣ Opção A: Executar via Python Script

### Criar arquivo `main.py`:

```python
import pandas as pd
from ia_ManutencaoProgramadaOS import ManutencaoProgramadaOS

# Ler dados
dados = pd.read_csv('dados_testes_soad.csv')

# Preencher indisponibilidades (conforme notebook)
dados['DGA_INDISPONIBILIDADE_N'] = 0
dados['DGA_INDISPONIBILIDADE_D1'] = 0
dados['DGA_INDISPONIBILIDADE_D2'] = 8
dados['DGA_INDISPONIBILIDADE_D3'] = 120
dados['DGA_INDISPONIBILIDADE_F'] = 720

dados['FQ_INDISPONIBILIDADE_N'] = 0
dados['FQ_INDISPONIBILIDADE_D1'] = 0
dados['FQ_INDISPONIBILIDADE_D2'] = 0
dados['FQ_INDISPONIBILIDADE_D3'] = 120
dados['FQ_INDISPONIBILIDADE_F'] = 720

# Converter para lista de dicts
dados_dict = dados.to_dict(orient='records')

# Executar otimização
ia = ManutencaoProgramadaOS()
resultado = ia.execute(data=dados_dict)

# Exibir resultado
print("\n=== CALENDÁRIO OTIMIZADO DE MANUTENÇÃO ===\n")
for item in resultado:
    print(f"OS {item['OS_Id']}: {item['DataOtima'].date()} | Prioridade: {item['Prioridade']+1}")

print("\nArquivo 'fronteiras_de_pareto.xlsx' gerado com sucesso!")
```

### Executar:

```bash
python main.py
```

---

## 5️⃣ Opção B: Usar Jupyter Notebook

Se preferir usar o notebook interativo (`otimiza_os.ipynb`):

### Instalar Jupyter:

```bash
pip install jupyter
```

### Executar Jupyter:

```bash
jupyter notebook
```

Isso abre um navegador em `http://localhost:8888`. Clique em `otimiza_os.ipynb` e execute as células com `Shift + Enter`.

---

## ⚠️ Problemas Comuns e Soluções

### Erro: "ModuleNotFoundError: No module named 'pandas'"

**Causa:** Dependências não instaladas

**Solução:**
```bash
pip install pandas numpy jmetal openpyxl tqdm
```

---

### Erro: "No such file or directory: 'dados_testes_soad.csv'"

**Causa:** Arquivo de dados não encontrado no caminho correto

**Solução:**
1. Verifique se o arquivo existe no mesmo diretório que os scripts Python
2. Se estiver em outro local, modifique o caminho:
```python
dados = pd.read_csv('../caminho/para/dados_testes_soad.csv')
```

---

### Erro: "jmetal not found"

**Causa:** Problema com instalação de jMetal

**Solução:**
```bash
pip uninstall jmetal
pip install jmetal==5.9.1
```

---

### Aviso: "SettingWithCopyWarning"

**Causa:** Pandas avisando sobre modificação de slice (linha notebook)

**Solução:** Não interfere na funcionalidade, apenas um aviso. Para eliminar:
```python
import pandas as pd
pd.options.mode.chained_assignment = None
```

---

### Erro: "OutOfMemoryError" durante NSGA-II

**Causa:** Muitas OS sendo processadas simultaneamente

**Solução:** Processar em lotes pequenos ou aumentar RAM disponível

---

## ✅ Verificação Final

Após executar, você deve ter:

```
✓ Arquivo 'fronteiras_de_pareto.xlsx' criado
✓ Console mostrando datas ótimas ordenadas por prioridade
✓ Sem erros ou exceções não tratadas
```

---

## 📊 Interpretar Resultados

O arquivo `fronteiras_de_pareto.xlsx` contém:

| Coluna | Significado |
|--------|------------|
| `t` | Dias até próxima manutenção |
| `Custo` | Indicador de custo operacional (normalizado) |
| `Indisponibilidade` | Indicador de tempo parado (normalizado) |
| `OS_id` | ID da ordem de serviço |

**Exemplo:**
```
t=365: Manutenção em 1 ano, custo baixo, mas mais paradas
t=730: Manutenção em 2 anos, custo alto, menos paradas
```

---

## 🚀 Próximos Passos

1. **Testar com seus dados reais** do EAM/SCADA
2. **Calibrar parâmetros** (taxas de transição) conforme histórico
3. **Validar resultados** comparando com manutenções anteriores
4. **Integrar com sistema de planejamento** (calendário, recursos)
5. **Monitorar eficácia** do calendário ao longo do tempo

---

## 💡 Dicas

- Use dados de **pelo menos 2 anos** para estimar taxas de transição
- **Recalibre mensalmente** com novos dados
- Considere **sazonalidade** (períodos de alta demanda)
- Exporte resultados para **Excel/PowerPoint** para apresentação

---

**Precisa de ajuda?** Verifique se todos os passos foram seguidos corretamente!

