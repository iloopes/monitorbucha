-- ═══════════════════════════════════════════════════════════════════
-- Schema do Banco de Dados - Sistema de Manutenção Preditiva
-- ═══════════════════════════════════════════════════════════════════

USE MaintenanceDB;
GO

-- ───────────────────────────────────────────────────────────────────
-- Tabela: sensor_data
-- Descrição: Armazena dados de sensores das buchas de transformador
-- ───────────────────────────────────────────────────────────────────

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sensor_data' AND xtype='U')
CREATE TABLE sensor_data (
    id INT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    equipment_id VARCHAR(100) NOT NULL,
    localizacao VARCHAR(100),
    tipo_transformador VARCHAR(50),
    tensao_nominal FLOAT,

    -- Métricas principais
    corrente_fuga FLOAT NOT NULL,              -- mA
    tg_delta FLOAT,                            -- %
    capacitancia FLOAT,                        -- pF

    -- Estado e eventos
    estado_saude INT NOT NULL,                 -- 0=Normal, 1-3=Degradado, 4=Falha
    evento VARCHAR(50),                         -- NORMAL, ANOMALIA_DETECTADA, etc.

    -- Dados ambientais
    temperatura_ambiente FLOAT,                -- °C
    umidade_relativa FLOAT,                    -- %

    -- Metadados
    created_at DATETIME DEFAULT GETDATE(),

    -- Índices
    INDEX idx_equipment_timestamp (equipment_id, timestamp),
    INDEX idx_timestamp (timestamp),
    INDEX idx_estado_saude (estado_saude)
);
GO

-- ───────────────────────────────────────────────────────────────────
-- Tabela: maintenance_orders
-- Descrição: Ordens de serviço de manutenção
-- ───────────────────────────────────────────────────────────────────

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='maintenance_orders' AND xtype='U')
CREATE TABLE maintenance_orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    os_id VARCHAR(100) UNIQUE NOT NULL,
    equipment_id VARCHAR(100) NOT NULL,
    localizacao VARCHAR(100),
    motivo_manutencao VARCHAR(50),             -- DGA, FQ

    -- Estado atual
    mf_dga INT,                                -- Estado DGA
    mf_dga_data DATETIME,                      -- Data da medição DGA

    -- Taxas de transição de estados
    dga_taxa_n FLOAT,
    dga_taxa_d1 FLOAT,
    dga_taxa_d2 FLOAT,
    dga_taxa_d3 FLOAT,

    -- Custos por estado
    dga_custo_n FLOAT,
    dga_custo_d1 FLOAT,
    dga_custo_d2 FLOAT,
    dga_custo_d3 FLOAT,
    dga_custo_falha FLOAT,

    -- Indisponibilidade (horas)
    dga_indisponibilidade_n FLOAT,
    dga_indisponibilidade_d1 FLOAT,
    dga_indisponibilidade_d2 FLOAT,
    dga_indisponibilidade_d3 FLOAT,
    dga_indisponibilidade_falha FLOAT,

    -- Metadados
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME,

    -- Índices
    INDEX idx_equipment (equipment_id),
    INDEX idx_os_id (os_id),
    INDEX idx_created_at (created_at)
);
GO

-- ───────────────────────────────────────────────────────────────────
-- Tabela: optimization_results
-- Descrição: Resultados da otimização NSGA-II
-- ───────────────────────────────────────────────────────────────────

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='optimization_results' AND xtype='U')
CREATE TABLE optimization_results (
    id INT IDENTITY(1,1) PRIMARY KEY,
    os_id VARCHAR(100) NOT NULL,

    -- Resultado da otimização
    t_days INT NOT NULL,                       -- Dias até manutenção
    custo FLOAT NOT NULL,                      -- Custo total
    indisponibilidade FLOAT NOT NULL,          -- Indisponibilidade total

    -- Data ótima calculada
    data_otima DATETIME,

    -- Prioridade
    prioridade INT,                            -- 1 = maior prioridade

    -- Critério de seleção
    criterio_selecao VARCHAR(50),              -- knee_point, min_cost, etc.

    -- Metadados
    created_at DATETIME DEFAULT GETDATE(),
    execution_time_ms INT,                     -- Tempo de execução

    -- Chave estrangeira
    FOREIGN KEY (os_id) REFERENCES maintenance_orders(os_id) ON DELETE CASCADE,

    -- Índices
    INDEX idx_os_id (os_id),
    INDEX idx_prioridade (prioridade),
    INDEX idx_data_otima (data_otima)
);
GO

-- ───────────────────────────────────────────────────────────────────
-- Tabela: pareto_frontier
-- Descrição: Pontos da fronteira de Pareto
-- ───────────────────────────────────────────────────────────────────

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pareto_frontier' AND xtype='U')
CREATE TABLE pareto_frontier (
    id INT IDENTITY(1,1) PRIMARY KEY,
    os_id VARCHAR(100) NOT NULL,

    -- Ponto da fronteira
    t_days INT NOT NULL,
    custo FLOAT NOT NULL,
    indisponibilidade FLOAT NOT NULL,

    -- Metadados
    created_at DATETIME DEFAULT GETDATE(),

    -- Chave estrangeira
    FOREIGN KEY (os_id) REFERENCES maintenance_orders(os_id) ON DELETE CASCADE,

    -- Índice
    INDEX idx_os_id (os_id)
);
GO

-- ───────────────────────────────────────────────────────────────────
-- Views úteis
-- ───────────────────────────────────────────────────────────────────

-- View: Últimas leituras por equipamento
IF EXISTS (SELECT * FROM sys.views WHERE name='vw_latest_sensor_readings')
DROP VIEW vw_latest_sensor_readings;
GO

CREATE VIEW vw_latest_sensor_readings AS
SELECT
    s1.*
FROM sensor_data s1
INNER JOIN (
    SELECT
        equipment_id,
        MAX(timestamp) as max_timestamp
    FROM sensor_data
    GROUP BY equipment_id
) s2 ON s1.equipment_id = s2.equipment_id
    AND s1.timestamp = s2.max_timestamp;
GO

-- View: Equipamentos críticos (estado >= 2)
IF EXISTS (SELECT * FROM sys.views WHERE name='vw_critical_equipment')
DROP VIEW vw_critical_equipment;
GO

CREATE VIEW vw_critical_equipment AS
SELECT TOP 100 PERCENT
    equipment_id,
    localizacao,
    estado_saude,
    corrente_fuga,
    timestamp,
    temperatura_ambiente,
    umidade_relativa
FROM vw_latest_sensor_readings
WHERE estado_saude >= 2
ORDER BY estado_saude DESC, corrente_fuga DESC;
GO

-- View: Calendário de manutenção
IF EXISTS (SELECT * FROM sys.views WHERE name='vw_maintenance_calendar')
DROP VIEW vw_maintenance_calendar;
GO

CREATE VIEW vw_maintenance_calendar AS
SELECT TOP 100 PERCENT
    mo.os_id,
    mo.equipment_id,
    mo.localizacao,
    mo.mf_dga AS estado_atual,
    opt.data_otima,
    opt.prioridade,
    opt.custo,
    opt.indisponibilidade,
    DATEDIFF(day, GETDATE(), opt.data_otima) AS dias_ate_manutencao
FROM maintenance_orders mo
INNER JOIN optimization_results opt ON mo.os_id = opt.os_id
WHERE opt.data_otima >= GETDATE()
ORDER BY opt.prioridade DESC;
GO

-- ═══════════════════════════════════════════════════════════════════
-- Procedures úteis
-- ═══════════════════════════════════════════════════════════════════

-- Procedure: Limpar dados antigos
IF EXISTS (SELECT * FROM sys.procedures WHERE name='sp_cleanup_old_data')
DROP PROCEDURE sp_cleanup_old_data;
GO

CREATE PROCEDURE sp_cleanup_old_data
    @days_to_keep INT = 90
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @cutoff_date DATETIME = DATEADD(day, -@days_to_keep, GETDATE());

    -- Deletar dados de sensores antigos
    DELETE FROM sensor_data
    WHERE timestamp < @cutoff_date;

    -- Retornar estatísticas
    SELECT
        @@ROWCOUNT AS rows_deleted,
        @cutoff_date AS cutoff_date;
END;
GO

-- ═══════════════════════════════════════════════════════════════════
-- Dados de exemplo (opcional)
-- ═══════════════════════════════════════════════════════════════════

-- Descomentar para inserir dados de exemplo
/*
INSERT INTO sensor_data (timestamp, equipment_id, localizacao, corrente_fuga, tg_delta, capacitancia, estado_saude, evento, temperatura_ambiente, umidade_relativa)
VALUES
    (GETDATE(), 'SPGR.ATF1', 'SPGR', 0.35, 0.28, 295.5, 0, 'NORMAL', 25.5, 65.0),
    (GETDATE(), 'SPGR.ATF2', 'SPGR', 0.82, 0.45, 310.2, 1, 'NORMAL', 26.0, 62.5),
    (GETDATE(), 'SPGR.ATF3', 'SPGR', 1.85, 0.92, 330.8, 2, 'ANOMALIA_DETECTADA', 27.5, 58.0);
*/

PRINT 'Schema criado com sucesso!';
GO
