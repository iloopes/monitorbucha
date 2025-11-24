"""
API REST para controle de buchas virtuais e geração de dados.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.data.synthetic_generator import VirtualBushingGenerator, BushinConfig
from src.database import SQLServerConnector, DatabaseManager
from src.utils import setup_logging
from src.optimization import MaintenanceOptimizer
from src.models import MarkovChainModel

# Configurar logging
logger = setup_logging(log_level="INFO")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Bucha Virtual",
    description="API para geração e controle de dados sintéticos de buchas de transformador",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
# Ajustar caminho relativo quando executado de api/
static_dir = Path(__file__).parent.parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Modelos Pydantic
class BushingConfigModel(BaseModel):
    """Modelo de configuração de bucha."""
    equipment_id: str
    localizacao: str = "SPGR"
    tipo_transformador: str = "ATF"
    tensao_nominal: float = 138.0
    estado_inicial: int = 0
    corrente_fuga_inicial: float = 0.3
    tg_delta_inicial: float = 0.3
    capacitancia_nominal: float = 300.0
    taxa_degradacao_corrente: float = 0.001
    taxa_degradacao_tg: float = 0.0005
    taxa_variacao_capacitancia: float = 0.01


class GenerationRequest(BaseModel):
    """Modelo de requisição de geração de dados."""
    n_bushings: int = 10
    days: int = 30
    frequency_hours: int = 1
    degradation_rate: str = "medium"  # low, medium, high
    save_to_database: bool = True
    scenario_name: Optional[str] = None


class DatabaseConfig(BaseModel):
    """Modelo de configuração do banco."""
    server: str
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    trusted_connection: bool = True


class OptimizationRequest(BaseModel):
    """Modelo de requisição de otimização."""
    equipment_ids: Optional[List[str]] = None  # None = otimizar todos
    max_evaluations: int = 4000
    population_size: int = 200
    save_to_database: bool = True


# Estado global do gerador
generator = VirtualBushingGenerator(seed=42)
db_connector: Optional[SQLServerConnector] = None


@app.get("/")
async def read_root():
    """Página inicial - servir frontend."""
    template_path = Path(__file__).parent.parent / "frontend" / "templates" / "index.html"
    return FileResponse(str(template_path))


@app.get("/api/health")
async def health_check():
    """Verifica o status da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.post("/api/database/configure")
async def configure_database(config: DatabaseConfig):
    """
    Configura a conexão com o banco de dados.
    """
    global db_connector

    try:
        db_connector = SQLServerConnector(
            server=config.server,
            database=config.database,
            username=config.username,
            password=config.password,
            trusted_connection=config.trusted_connection
        )

        db_connector.connect()
        logger.info("Banco de dados configurado com sucesso")

        return {
            "status": "success",
            "message": "Conexão com banco de dados estabelecida",
            "server": config.server,
            "database": config.database
        }

    except Exception as e:
        logger.error(f"Erro ao configurar banco: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/database/init")
async def initialize_database():
    """
    Inicializa o banco de dados (cria tabelas).
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado. Use /api/database/configure primeiro."
        )

    try:
        manager = DatabaseManager(db_connector)
        manager.create_tables()

        logger.info("Tabelas criadas com sucesso")

        return {
            "status": "success",
            "message": "Tabelas criadas no banco de dados",
            "tables": ["sensor_data", "maintenance_orders", "optimization_results"]
        }

    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bushings/add")
async def add_bushing(config: BushingConfigModel):
    """
    Adiciona uma bucha virtual ao gerador.
    """
    try:
        bushing_config = BushinConfig(
            equipment_id=config.equipment_id,
            localizacao=config.localizacao,
            tipo_transformador=config.tipo_transformador,
            tensao_nominal=config.tensao_nominal,
            estado_inicial=config.estado_inicial,
            corrente_fuga_inicial=config.corrente_fuga_inicial,
            tg_delta_inicial=config.tg_delta_inicial,
            capacitancia_nominal=config.capacitancia_nominal,
            taxa_degradacao_corrente=config.taxa_degradacao_corrente,
            taxa_degradacao_tg=config.taxa_degradacao_tg,
            taxa_variacao_capacitancia=config.taxa_variacao_capacitancia,
        )

        generator.add_bushing(bushing_config)

        return {
            "status": "success",
            "message": f"Bucha {config.equipment_id} adicionada",
            "total_bushings": len(generator.configs)
        }

    except Exception as e:
        logger.error(f"Erro ao adicionar bucha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/data/generate")
async def generate_data(request: GenerationRequest):
    """
    Gera dados sintéticos de buchas.
    """
    try:
        scenario_name = request.scenario_name or f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Gerando cenário: {scenario_name}")

        # Gerar dados
        sensor_data, maintenance_orders = generator.generate_scenario(
            scenario_name=scenario_name,
            n_bushings=request.n_bushings,
            days=request.days,
            degradation_rate=request.degradation_rate
        )

        result = {
            "status": "success",
            "scenario_name": scenario_name,
            "statistics": {
                "n_bushings": request.n_bushings,
                "days": request.days,
                "sensor_records": len(sensor_data),
                "maintenance_orders": len(maintenance_orders),
                "date_range": {
                    "start": sensor_data['timestamp'].min().isoformat(),
                    "end": sensor_data['timestamp'].max().isoformat()
                }
            }
        }

        # Salvar no banco se solicitado
        if request.save_to_database:
            if not db_connector:
                return {
                    **result,
                    "database": {
                        "status": "skipped",
                        "reason": "Banco de dados não configurado"
                    }
                }

            try:
                manager = DatabaseManager(db_connector)

                sensor_inserted = manager.insert_sensor_data(sensor_data)
                orders_inserted = manager.insert_maintenance_orders(maintenance_orders)

                result["database"] = {
                    "status": "success",
                    "sensor_records_inserted": sensor_inserted,
                    "orders_inserted": orders_inserted
                }

                logger.info(
                    f"Dados salvos no banco: "
                    f"{sensor_inserted} sensores, {orders_inserted} OS"
                )

            except Exception as e:
                logger.error(f"Erro ao salvar no banco: {e}")
                result["database"] = {
                    "status": "error",
                    "error": str(e)
                }

        return result

    except Exception as e:
        logger.error(f"Erro ao gerar dados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/sensor")
async def get_sensor_data(
    equipment_id: Optional[str] = Query(None, description="ID do equipamento"),
    limit: int = Query(100, description="Número de registros")
):
    """
    Busca dados de sensores do banco.
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado"
        )

    try:
        manager = DatabaseManager(db_connector)
        data = manager.get_sensor_data(equipment_id=equipment_id)

        # Limitar número de registros
        data = data.head(limit)

        return {
            "status": "success",
            "count": len(data),
            "data": data.to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"Erro ao buscar dados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/orders")
async def get_maintenance_orders(
    equipment_id: Optional[str] = Query(None, description="ID do equipamento")
):
    """
    Busca ordens de serviço do banco.
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado"
        )

    try:
        manager = DatabaseManager(db_connector)
        orders = manager.get_maintenance_orders(equipment_id=equipment_id)

        return {
            "status": "success",
            "count": len(orders),
            "orders": orders.to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"Erro ao buscar ordens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bushings/list")
async def list_bushings():
    """
    Lista todas as buchas configuradas.
    """
    bushings = [
        {
            "equipment_id": config.equipment_id,
            "localizacao": config.localizacao,
            "tipo_transformador": config.tipo_transformador,
            "tensao_nominal": config.tensao_nominal,
            "estado_inicial": config.estado_inicial,
            "corrente_fuga_inicial": config.corrente_fuga_inicial,
        }
        for config in generator.configs
    ]

    return {
        "status": "success",
        "count": len(bushings),
        "bushings": bushings
    }


@app.delete("/api/bushings/clear")
async def clear_bushings():
    """
    Remove todas as buchas configuradas.
    """
    count = len(generator.configs)
    generator.configs = []

    return {
        "status": "success",
        "message": f"{count} buchas removidas",
        "total_bushings": 0
    }


@app.get("/api/equipment/list")
async def list_equipment():
    """
    Lista todos os equipamentos disponíveis no banco de dados.
    """
    logger.info("Endpoint /api/equipment/list chamado")
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado"
        )

    try:
        manager = DatabaseManager(db_connector)

        query = """
        SELECT DISTINCT equipment_id, localizacao
        FROM maintenance_orders
        ORDER BY equipment_id
        """

        equipment_df = manager.connector.fetch_data(query)

        if equipment_df.empty:
            return {
                "status": "success",
                "equipment": [],
                "count": 0
            }

        equipment_list = equipment_df.to_dict(orient='records')

        return {
            "status": "success",
            "equipment": equipment_list,
            "count": len(equipment_list)
        }

    except Exception as e:
        logger.error(f"Erro ao listar equipamentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize/run")
async def run_optimization(request: OptimizationRequest):
    """
    Executa otimização de manutenção usando Markov + NSGA-II.
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado. Configure primeiro em /api/database/configure"
        )

    try:
        logger.info("Iniciando otimização de manutenção...")

        # Buscar ordens de serviço do banco
        manager = DatabaseManager(db_connector)

        if request.equipment_ids:
            # Otimizar equipamentos específicos
            all_orders = []
            for eq_id in request.equipment_ids:
                orders = manager.get_maintenance_orders(equipment_id=eq_id)
                all_orders.append(orders)
            orders_df = pd.concat(all_orders, ignore_index=True) if all_orders else pd.DataFrame()
        else:
            # Otimizar todas as ordens de serviço
            orders_df = manager.get_maintenance_orders()

        if orders_df.empty:
            return {
                "status": "error",
                "message": "Nenhuma ordem de serviço encontrada no banco de dados",
                "hint": "Gere dados sintéticos primeiro usando /api/data/generate"
            }

        logger.info(f"Otimizando {len(orders_df)} ordens de serviço...")

        # Criar otimizador
        optimizer = MaintenanceOptimizer(
            max_evaluations=request.max_evaluations,
            population_size=request.population_size
        )

        # Executar otimização para cada OS
        results = []
        pareto_data = []

        for idx, row in orders_df.iterrows():
            try:
                os_id = row['os_id']
                logger.info(f"Otimizando OS {os_id} ({idx+1}/{len(orders_df)})")

                # Extrair parâmetros da OS
                transition_rates = [
                    row['dga_taxa_n'],
                    row['dga_taxa_d1'],
                    row['dga_taxa_d2'],
                    row['dga_taxa_d3']
                ]

                operational_costs = [
                    row['dga_custo_n'],
                    row['dga_custo_d1'],
                    row['dga_custo_d2'],
                    row['dga_custo_d3'],
                    row['dga_custo_falha']
                ]

                unavailabilities = [
                    row['dga_indisponibilidade_n'],
                    row['dga_indisponibilidade_d1'],
                    row['dga_indisponibilidade_d2'],
                    row['dga_indisponibilidade_d3'],
                    row['dga_indisponibilidade_falha']
                ]

                # Executar otimização
                pareto_front = optimizer.optimize(
                    transition_rates=transition_rates,
                    operational_costs=operational_costs,
                    unavailabilities=unavailabilities,
                    initial_state=row['mf_dga']
                )

                # Selecionar melhor solução (menor custo)
                best_solution = min(pareto_front, key=lambda x: x['cost'])

                # Calcular data ótima
                data_manutencao_otima = row['mf_dga_data'] + timedelta(days=int(best_solution['t_days']))

                # Adicionar resultado
                result = {
                    "os_id": os_id,
                    "equipment_id": row['equipment_id'],
                    "localizacao": row['localizacao'],
                    "estado_atual": row['mf_dga'],
                    "t_days": best_solution['t_days'],
                    "custo": best_solution['cost'],
                    "indisponibilidade": best_solution['unavailability'],
                    "data_otima": data_manutencao_otima.isoformat(),
                    "prioridade": 5 - row['mf_dga'],  # Maior prioridade para estados mais degradados
                    "pareto_size": len(pareto_front)
                }
                results.append(result)

                # Salvar pontos do Pareto para visualização
                for point in pareto_front:
                    pareto_data.append({
                        "os_id": os_id,
                        "equipment_id": row['equipment_id'],
                        "t_days": point['t_days'],
                        "custo": point['cost'],
                        "indisponibilidade": point['unavailability']
                    })

            except Exception as e:
                logger.error(f"Erro ao otimizar OS {row['os_id']}: {e}", exc_info=True)
                continue

        # Salvar resultados no banco se solicitado
        if request.save_to_database and results:
            results_df = pd.DataFrame(results)

            # Inserir resultados de otimização
            insert_query = """
            INSERT INTO optimization_results (
                os_id, t_days, custo, indisponibilidade, data_otima,
                prioridade, criterio_selecao
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor = db_connector.connection.cursor()
            inserted = 0

            for _, result in results_df.iterrows():
                try:
                    cursor.execute(insert_query, (
                        result['os_id'],
                        result['t_days'],
                        result['custo'],
                        result['indisponibilidade'],
                        result['data_otima'],
                        result['prioridade'],
                        'min_cost'
                    ))
                    inserted += 1
                except Exception as e:
                    logger.warning(f"Erro ao inserir resultado: {e}")
                    continue

            db_connector.connection.commit()
            logger.info(f"{inserted} resultados de otimização salvos no banco")

            # Salvar pontos do Pareto
            if pareto_data:
                pareto_df = pd.DataFrame(pareto_data)
                pareto_insert_query = """
                INSERT INTO pareto_frontier (
                    os_id, t_days, custo, indisponibilidade
                ) VALUES (?, ?, ?, ?)
                """

                for _, point in pareto_df.iterrows():
                    try:
                        cursor.execute(pareto_insert_query, (
                            point['os_id'],
                            point['t_days'],
                            point['custo'],
                            point['indisponibilidade']
                        ))
                    except:
                        pass

                db_connector.connection.commit()

        # Ordenar por prioridade
        results.sort(key=lambda x: x['prioridade'], reverse=True)

        return {
            "status": "success",
            "message": f"Otimização concluída para {len(results)} equipamentos",
            "summary": {
                "total_optimized": len(results),
                "avg_cost": sum(r['custo'] for r in results) / len(results) if results else 0,
                "avg_unavailability": sum(r['indisponibilidade'] for r in results) / len(results) if results else 0,
                "total_pareto_points": len(pareto_data)
            },
            "results": results[:50]  # Retornar primeiros 50 para não sobrecarregar
        }

    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calendar")
async def get_maintenance_calendar():
    """
    Retorna o calendário de manutenção otimizado.
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado"
        )

    try:
        # Buscar do banco usando a view criada no schema.sql
        query = """
        SELECT
            mo.os_id,
            mo.equipment_id,
            mo.localizacao,
            mo.mf_dga as estado_atual,
            opt.data_otima,
            opt.t_days,
            opt.custo,
            opt.indisponibilidade,
            opt.prioridade,
            DATEDIFF(day, GETDATE(), opt.data_otima) as dias_ate_manutencao
        FROM maintenance_orders mo
        INNER JOIN optimization_results opt ON mo.os_id = opt.os_id
        WHERE opt.data_otima >= GETDATE()
        ORDER BY opt.prioridade DESC, opt.data_otima ASC
        """

        manager = DatabaseManager(db_connector)
        calendar_df = manager.connector.fetch_data(query)

        if calendar_df.empty:
            return {
                "status": "success",
                "message": "Nenhuma manutenção programada encontrada",
                "calendar": []
            }

        # Converter para lista de dicionários
        calendar = calendar_df.to_dict(orient='records')

        # Adicionar categorias de urgência
        for item in calendar:
            dias = item['dias_ate_manutencao']
            if dias < 0:
                item['urgencia'] = 'atrasado'
            elif dias <= 7:
                item['urgencia'] = 'urgente'
            elif dias <= 30:
                item['urgencia'] = 'proxima'
            else:
                item['urgencia'] = 'programada'

        return {
            "status": "success",
            "total": len(calendar),
            "calendar": calendar
        }

    except Exception as e:
        logger.error(f"Erro ao buscar calendário: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pareto/{equipment_id}")
async def get_pareto_front(equipment_id: str):
    """
    Retorna a fronteira de Pareto para um equipamento específico.
    """
    if not db_connector:
        raise HTTPException(
            status_code=400,
            detail="Banco de dados não configurado"
        )

    try:
        # Buscar OS ID do equipamento
        query_os = """
        SELECT os_id FROM maintenance_orders
        WHERE equipment_id = ?
        ORDER BY created_at DESC
        """

        manager = DatabaseManager(db_connector)
        os_result = manager.connector.fetch_data(query_os, (equipment_id,))

        if os_result.empty:
            return {
                "status": "error",
                "message": f"Equipamento {equipment_id} não encontrado"
            }

        os_id = os_result.iloc[0]['os_id']

        # Buscar pontos do Pareto
        query_pareto = """
        SELECT t_days, custo, indisponibilidade
        FROM pareto_frontier
        WHERE os_id = ?
        ORDER BY custo ASC
        """

        pareto_df = manager.connector.fetch_data(query_pareto, (os_id,))

        if pareto_df.empty:
            return {
                "status": "error",
                "message": "Fronteira de Pareto não encontrada. Execute a otimização primeiro."
            }

        return {
            "status": "success",
            "equipment_id": equipment_id,
            "os_id": os_id,
            "pareto_points": pareto_df.to_dict(orient='records')
        }

    except Exception as e:
        logger.error(f"Erro ao buscar Pareto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
