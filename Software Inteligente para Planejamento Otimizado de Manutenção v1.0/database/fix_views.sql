-- ═══════════════════════════════════════════════════════════════════
-- Script de Correção das Views
-- Execute este script para corrigir os erros das views
-- ═══════════════════════════════════════════════════════════════════

USE MaintenanceDB;
GO

PRINT 'Corrigindo views...';
GO

-- ───────────────────────────────────────────────────────────────────
-- Recriar View: vw_critical_equipment
-- ───────────────────────────────────────────────────────────────────

IF EXISTS (SELECT * FROM sys.views WHERE name='vw_critical_equipment')
BEGIN
    DROP VIEW vw_critical_equipment;
    PRINT 'View vw_critical_equipment removida';
END
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

PRINT 'View vw_critical_equipment criada com sucesso';
GO

-- ───────────────────────────────────────────────────────────────────
-- Recriar View: vw_maintenance_calendar
-- ───────────────────────────────────────────────────────────────────

IF EXISTS (SELECT * FROM sys.views WHERE name='vw_maintenance_calendar')
BEGIN
    DROP VIEW vw_maintenance_calendar;
    PRINT 'View vw_maintenance_calendar removida';
END
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

PRINT 'View vw_maintenance_calendar criada com sucesso';
GO

-- ───────────────────────────────────────────────────────────────────
-- Verificação
-- ───────────────────────────────────────────────────────────────────

PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT 'Views corrigidas com sucesso!';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '';

-- Listar todas as views
SELECT 'Views criadas:' AS Info;
SELECT name AS ViewName FROM sys.views ORDER BY name;
GO

PRINT 'Correccao concluida!';
GO
