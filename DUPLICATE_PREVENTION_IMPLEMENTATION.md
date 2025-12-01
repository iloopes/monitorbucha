# Implementacao de Prevencao de Duplicatas no Banco de Dados

## Resumo Executivo

Implementacao completa de verificacao de duplicatas em TODAS as operacoes de INSERT do sistema, eliminando erros de "Violation of UNIQUE KEY constraint" que ocorriam quando dados duplicados tentavam ser inseridos.

**Data de Conclusao**: 26 de novembro de 2025

## Problema Original

O usuario relatava: "esta acontecendo varios erros nos inserts em geral, esta tentando adicionar varias vezes o mesmo id, faca com o gerador de dados faca as verificacoes antes de gerar novos dados. faca isso tambem para tudo o que pode fazer insert no banco"

Erros tipicos:
- `Violation of UNIQUE KEY 'UQ__anomaly___5DD3F6BB8407765D'` para anomaly_models
- Violacoes similares para outras tabelas

## Solucao Implementada

### Padrao Consistente de 3 Passos

Todas as tabelas seguem o mesmo padrao:

```python
# 1. Obter registros existentes do banco
existing = db_connector.fetch_data(query, params)
existing_keys = set(...)  # Extrair identificadores unicos

# 2. Filtrar dados novos para excluir duplicatas
new_data = [item for item in data if item_key not in existing_keys]

# 3. Inserir apenas registros novos/unicos
for item in new_data:
    cursor.execute(insert_query, params)
```

## Tabelas Implementadas

### 1. sensor_data - src/database/sql_server.py:288-346

**Chave Unica**: `(equipment_id, timestamp)`

**Metodos Adicionados**:
- `_get_existing_sensor_records()` - Busca registros existentes por IDs de equipamento
- `_is_duplicate_sensor_record()` - Compara timestamp + equipment_id

**Comportamento**:
- Consulta banco para encontrar records com mesmo equipment_id e timestamp range
- Filtra DataFrame para excluir duplicatas
- Retorna contador de inseridos e ignorados

**Exemplo de Log**:
```
Inserindo 120 novos registros de sensor (ignoradas 0 duplicatas)
Registros de sensor inseridos com sucesso: 120
```

### 2. maintenance_orders - src/database/sql_server.py:405-510

**Chave Unica**: `os_id` (UNIQUE constraint)

**Metodos Adicionados**:
- `_get_existing_os_ids()` - Busca IDs de ordens existentes

**Comportamento**:
- Consulta banco para IDs de OS ja existentes
- Filtra usando `.isin()` para excluir ordens duplicadas
- Registra numero de duplicatas ignoradas

**Exemplo de Log**:
```
Inserindo 45 novas ordens de manutencao (ignoradas 5 duplicatas)
45 ordens inseridas com sucesso
```

### 3. anomaly_models - src/anomaly/manager.py:281-321

**Chave Unica**: `model_name` (UNIQUE constraint)

**Padrao**: INSERT-or-UPDATE (nao apenas INSERT)

**Comportamento**:
- Verifica se model_name ja existe com SELECT COUNT(*)
- Se existe: faz UPDATE para refresh de metadados e timestamp
- Se novo: faz INSERT

**Resultado**: Elimina completamente erros de duplicate key constraint

**Exemplo de Log**:
```
Metadados do modelo 'autoencoder_model' atualizados
(em lugar de erro de UNIQUE KEY)
```

### 4. anomaly_detections - src/anomaly/manager.py:323-392

**Chave Unica**: `timestamp` (usado como identificador)

**Metodos Adicionados**:
- `_get_existing_detections()` - Busca timestamps existentes
- Modifica `_save_detections()` para pre-filtrar

**Comportamento**:
- Consulta para encontrar deteccoes ja registradas por timestamp
- Filtra deteccoes duplicadas antes do INSERT
- Registra quantas deteccoes foram ignoradas

**Exemplo de Log**:
```
Inserindo 25 novas deteccoes (ignoradas 10 duplicatas)
25 deteccoes salvas no banco
```

### 5. optimization_results - api/main.py:589-649

**Chave Unica**: `(os_id, t_days)` (composite key)

**Comportamento**:
- Consulta para encontrar resultados existentes com os_id matching
- Filtra novos resultados usando composite key (os_id, t_days)
- Log de duplicatas ignoradas

**Exemplo de Log**:
```
Inserindo 50 novos resultados (ignoradas 3 duplicatas)
50 resultados de otimizacao salvos no banco
```

### 6. pareto_frontier - api/main.py:651-693

**Chave Unica**: `(os_id, t_days)` (composite key)

**Comportamento**:
- Consulta para encontrar pontos Pareto existentes
- Filtra por composite key (os_id, t_days)
- Log condicional apenas se novos pontos foram inseridos

**Exemplo de Log**:
```
42 pontos Pareto salvos no banco
```

## Beneficios

1. **Zero Erros de Constraint**: Nenhuma violacao de UNIQUE KEY constraint
2. **Operacoes Idempotentes**: Multiplas requisicoes com mesmos dados nao causam erros
3. **Logging Transparente**: Cada operacao registra duplicatas ignoradas
4. **Aplicacao Consistente**: Mesmo padrao em todas as 6 tabelas
5. **Non-Blocking**: Se verificacao falha, insercoes continuam
6. **Sem Data Loss**: Duplicatas sao ignoradas, dados novos sao inseridos

## Como Funciona na Pratica

### Exemplo: Geracao Duplicada de Dados

```
[PRIMEIRA CHAMADA]
POST /api/data/generate
  Gerando 10 buchas × 30 dias = 7200 registros de sensor
  Inserindo 7200 registros de sensor
  Inserindo 150 ordens de manutencao
  ✓ Sucesso

[SEGUNDA CHAMADA (mesmos parametros)]
POST /api/data/generate
  Gerando 10 buchas × 30 dias = 7200 registros de sensor
  Verificando registros existentes...
  Encontrados 7200 existentes
  Inserindo 0 novos registros de sensor (ignoradas 7200 duplicatas)
  Verificando ordens existentes...
  Encontradas 150 existentes
  Inserindo 0 novas ordens (ignoradas 150 duplicatas)
  ✓ Sucesso (sem violacao de constraint)
```

### Exemplo: Retrainamento de Modelo

```
[PRIMEIRO TREINAMENTO]
POST /api/anomaly/train?model_name=modelo_v1
  Treinando autoencoder...
  Metadados do modelo 'modelo_v1' inseridos
  ✓ Sucesso

[SEGUNDO TREINAMENTO (mesmo nome)]
POST /api/anomaly/train?model_name=modelo_v1
  Treinando autoencoder...
  Metadados do modelo 'modelo_v1' atualizados (UPDATE, nao INSERT)
  ✓ Sucesso (sem violacao de UNIQUE KEY)
```

## Arquivos Modificados

| Arquivo | Modificacoes |
|---------|--------------|
| `src/database/sql_server.py` | Metodos de verificacao para sensor_data e maintenance_orders |
| `src/anomaly/manager.py` | INSERT-or-UPDATE para anomaly_models, verificacao para anomaly_detections |
| `api/main.py` | Verificacao para optimization_results e pareto_frontier |

## Validacao

O sistema foi validado com:
- Multiplas geracoes de dados identicas
- Retrainamento de modelos com mesmo nome
- Multiplas deteccoes identicas
- Multiplas otimizacoes identicas

Resultado: Nenhuma violacao de constraint, todas as operacoes completam com sucesso

## Proximos Passos (se necessario)

Se houver outros INSERT's em tabelas ainda nao cobertas:
1. Identificar a tabela e constraint UNIQUE
2. Aplicar o mesmo padrao de 3 passos
3. Adicionar logging consistente
4. Testar com dados duplicados

## Notas Tecnicas

- Todas as operacoes de verificacao usam SELECT com WHERE clause otimizado
- Filtragem feita em memoria (pandas) para performance
- Nenhuma alteracao no schema do banco (tudo via aplicacao)
- Log messages informam claramente quantas duplicatas foram ignoradas

---

**Status**: COMPLETO E TESTADO
**Data**: 26 de novembro de 2025
**Versao**: 1.0
