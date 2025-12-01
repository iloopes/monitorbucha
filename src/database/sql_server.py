"""
Integração com SQL Server para armazenamento de dados de buchas.
"""

import pyodbc
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from ..utils.logging_config import get_logger
from ..utils.config_loader import get_config_loader

logger = get_logger(__name__)


class SQLServerConnector:
    """Conector para SQL Server."""

    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "ODBC Driver 17 for SQL Server",
        trusted_connection: bool = False,
    ):
        """
        Inicializa o conector SQL Server.

        Args:
            server: Nome do servidor SQL Server.
            database: Nome do banco de dados.
            username: Usuário do banco.
            password: Senha do banco.
            driver: Driver ODBC.
            trusted_connection: Usar autenticação Windows.
        """
        # Carregar configurações se não fornecidas
        if server is None or database is None:
            config_loader = get_config_loader()
            db_config = config_loader.get("database", "sqlserver", {})

            server = server or db_config.get("server", "localhost")
            database = database or db_config.get("database", "MaintenanceDB")
            username = username or db_config.get("username", "")
            password = password or db_config.get("password", "")
            trusted_connection = db_config.get("trusted_connection", trusted_connection)

        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.trusted_connection = trusted_connection

        self.connection = None
        logger.info(f"SQL Server Connector criado: {server}/{database}")

    def connect(self) -> pyodbc.Connection:
        """
        Estabelece conexão com o banco de dados.

        Returns:
            Objeto de conexão.

        Raises:
            Exception: Se não conseguir conectar.
        """
        try:
            if self.trusted_connection:
                conn_str = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                conn_str = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )

            self.connection = pyodbc.connect(conn_str)
            logger.info("Conexão estabelecida com sucesso")
            return self.connection

        except Exception as e:
            logger.error(f"Erro ao conectar ao SQL Server: {e}")
            raise

    def disconnect(self) -> None:
        """Fecha a conexão com o banco."""
        if self.connection:
            self.connection.close()
            logger.info("Conexão fechada")
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Executa uma query SQL (INSERT, UPDATE, DELETE).

        Args:
            query: Query SQL a executar.
            params: Parâmetros da query.
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            logger.debug(f"Query executada: {query[:100]}...")

        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            self.connection.rollback()
            raise

    def fetch_data(
        self, query: str, params: Optional[tuple] = None
    ) -> pd.DataFrame:
        """
        Executa uma query SELECT e retorna resultados.

        Args:
            query: Query SQL SELECT.
            params: Parâmetros da query.

        Returns:
            DataFrame com os resultados.
        """
        if not self.connection:
            self.connect()

        try:
            if params:
                df = pd.read_sql_query(query, self.connection, params=params)
            else:
                df = pd.read_sql_query(query, self.connection)

            logger.debug(f"Dados obtidos: {len(df)} linhas")
            return df

        except Exception as e:
            logger.error(f"Erro ao buscar dados: {e}")
            raise

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe no banco.

        Args:
            table_name: Nome da tabela.

        Returns:
            True se a tabela existe.
        """
        query = """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = ?
        """

        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute(query, (table_name,))
        result = cursor.fetchone()

        return result[0] > 0

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class DatabaseManager:
    """Gerenciador de operações no banco de dados."""

    def __init__(self, connector: SQLServerConnector):
        """
        Inicializa o gerenciador.

        Args:
            connector: Conector SQL Server.
        """
        self.connector = connector

    def create_tables(self) -> None:
        """Cria as tabelas necessárias no banco de dados."""
        logger.info("Criando tabelas no banco de dados...")

        # Tabela de dados de sensores
        create_sensor_data_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sensor_data' AND xtype='U')
        CREATE TABLE sensor_data (
            id INT IDENTITY(1,1) PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            equipment_id VARCHAR(100) NOT NULL,
            localizacao VARCHAR(100),
            tipo_transformador VARCHAR(50),
            tensao_nominal FLOAT,
            corrente_fuga FLOAT,
            tg_delta FLOAT,
            capacitancia FLOAT,
            estado_saude INT,
            evento VARCHAR(50),
            temperatura_ambiente FLOAT,
            umidade_relativa FLOAT,
            created_at DATETIME DEFAULT GETDATE(),
            INDEX idx_equipment_timestamp (equipment_id, timestamp),
            INDEX idx_timestamp (timestamp)
        )
        """

        # Tabela de ordens de serviço
        create_maintenance_orders_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='maintenance_orders' AND xtype='U')
        CREATE TABLE maintenance_orders (
            id INT IDENTITY(1,1) PRIMARY KEY,
            os_id VARCHAR(100) UNIQUE NOT NULL,
            equipment_id VARCHAR(100) NOT NULL,
            localizacao VARCHAR(100),
            motivo_manutencao VARCHAR(50),
            mf_dga INT,
            mf_dga_data DATETIME,
            dga_taxa_n FLOAT,
            dga_taxa_d1 FLOAT,
            dga_taxa_d2 FLOAT,
            dga_taxa_d3 FLOAT,
            dga_custo_n FLOAT,
            dga_custo_d1 FLOAT,
            dga_custo_d2 FLOAT,
            dga_custo_d3 FLOAT,
            dga_custo_falha FLOAT,
            dga_indisponibilidade_n FLOAT,
            dga_indisponibilidade_d1 FLOAT,
            dga_indisponibilidade_d2 FLOAT,
            dga_indisponibilidade_d3 FLOAT,
            dga_indisponibilidade_falha FLOAT,
            created_at DATETIME DEFAULT GETDATE(),
            INDEX idx_equipment (equipment_id),
            INDEX idx_os_id (os_id)
        )
        """

        # Tabela de resultados de otimização
        create_optimization_results_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='optimization_results' AND xtype='U')
        CREATE TABLE optimization_results (
            id INT IDENTITY(1,1) PRIMARY KEY,
            os_id VARCHAR(100) NOT NULL,
            t_days INT,
            custo FLOAT,
            indisponibilidade FLOAT,
            data_otima DATETIME,
            prioridade INT,
            criterio_selecao VARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (os_id) REFERENCES maintenance_orders(os_id),
            INDEX idx_os_id (os_id),
            INDEX idx_prioridade (prioridade)
        )
        """

        # Executar criação das tabelas
        self.connector.execute_query(create_sensor_data_table)
        self.connector.execute_query(create_maintenance_orders_table)
        self.connector.execute_query(create_optimization_results_table)

        logger.info("Tabelas criadas com sucesso")

    def insert_sensor_data(self, data: pd.DataFrame) -> int:
        """
        Insere dados de sensores no banco com verificação de duplicatas.

        Args:
            data: DataFrame com dados de sensores.

        Returns:
            Número de registros inseridos.
        """
        logger.info(f"Verificando e inserindo {len(data)} registros de sensores...")

        # Verificar registros duplicados no banco antes de inserir
        existing_records = self._get_existing_sensor_records(data)

        # Filtrar apenas registros novos (não duplicados)
        new_data = data[~data.apply(lambda row: self._is_duplicate_sensor_record(row, existing_records), axis=1)]

        if len(new_data) == 0:
            logger.info("Todos os registros já existem no banco. Nenhum insert realizado.")
            return 0

        insert_query = """
        INSERT INTO sensor_data (
            timestamp, equipment_id, localizacao, tipo_transformador,
            tensao_nominal, corrente_fuga, tg_delta, capacitancia,
            estado_saude, evento, temperatura_ambiente, umidade_relativa
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = self.connector.connection.cursor()
        inserted = 0

        for _, row in new_data.iterrows():
            try:
                cursor.execute(insert_query, (
                    row['timestamp'],
                    row['equipment_id'],
                    row['localizacao'],
                    row['tipo_transformador'],
                    row['tensao_nominal'],
                    row['corrente_fuga'],
                    row['tg_delta'],
                    row['capacitancia'],
                    row['estado_saude'],
                    row['evento'],
                    row['temperatura_ambiente'],
                    row['umidade_relativa'],
                ))
                inserted += 1

            except Exception as e:
                logger.warning(f"Erro ao inserir registro (equipment={row['equipment_id']}, timestamp={row['timestamp']}): {e}")
                continue

        self.connector.connection.commit()
        logger.info(f"{inserted} registros de sensores inseridos (filtrados de {len(data)}, {len(data) - inserted} duplicatas ignoradas)")

        return inserted

    def _get_existing_sensor_records(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Busca registros existentes no banco para comparação.

        Args:
            data: DataFrame com dados para filtrar.

        Returns:
            DataFrame com registros existentes.
        """
        try:
            # Pegar equipamentos e datas únicas
            equipment_ids = data['equipment_id'].unique().tolist()
            min_timestamp = data['timestamp'].min()
            max_timestamp = data['timestamp'].max()

            if not equipment_ids:
                return pd.DataFrame()

            # Buscar registros existentes nesse range
            equipments_str = "', '".join(equipment_ids)
            query = f"""
            SELECT timestamp, equipment_id, corrente_fuga, tg_delta, capacitancia
            FROM sensor_data
            WHERE equipment_id IN ('{equipments_str}')
            AND timestamp BETWEEN ? AND ?
            """

            existing = self.connector.fetch_data(query, (min_timestamp, max_timestamp))
            return existing if existing is not None else pd.DataFrame()

        except Exception as e:
            logger.warning(f"Erro ao buscar registros existentes: {e}")
            return pd.DataFrame()

    def _is_duplicate_sensor_record(self, row, existing_records: pd.DataFrame) -> bool:
        """
        Verifica se um registro é duplicado comparando timestamp, equipment_id e valores.

        Args:
            row: Linha do DataFrame.
            existing_records: DataFrame com registros existentes.

        Returns:
            True se for duplicado, False caso contrário.
        """
        if existing_records.empty:
            return False

        # Buscar registros do mesmo equipamento e timestamp
        matches = existing_records[
            (existing_records['equipment_id'] == row['equipment_id']) &
            (existing_records['timestamp'] == row['timestamp'])
        ]

        return len(matches) > 0

    def insert_maintenance_orders(self, orders: pd.DataFrame) -> int:
        """
        Insere ordens de serviço no banco com verificação de duplicatas.

        Args:
            orders: DataFrame com ordens de serviço.

        Returns:
            Número de registros inseridos.
        """
        logger.info(f"Verificando e inserindo {len(orders)} ordens de serviço...")

        # Verificar IDs de OS que já existem
        existing_os_ids = self._get_existing_os_ids(orders)

        # Filtrar apenas OS novas (não duplicadas)
        new_orders = orders[~orders['OS_Id'].isin(existing_os_ids)]

        if len(new_orders) == 0:
            logger.info("Todas as ordens de serviço já existem no banco. Nenhum insert realizado.")
            return 0

        insert_query = """
        INSERT INTO maintenance_orders (
            os_id, equipment_id, localizacao, motivo_manutencao,
            mf_dga, mf_dga_data,
            dga_taxa_n, dga_taxa_d1, dga_taxa_d2, dga_taxa_d3,
            dga_custo_n, dga_custo_d1, dga_custo_d2, dga_custo_d3, dga_custo_falha,
            dga_indisponibilidade_n, dga_indisponibilidade_d1,
            dga_indisponibilidade_d2, dga_indisponibilidade_d3, dga_indisponibilidade_falha
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = self.connector.connection.cursor()
        inserted = 0

        for _, row in new_orders.iterrows():
            try:
                cursor.execute(insert_query, (
                    row['OS_Id'],
                    row['Equipamento'],
                    row['Localizacao'],
                    row['MotivoManutencao'],
                    row['MF_DGA'],
                    row['MF_DGA_DATA'],
                    row['DGA_TAXA_N'],
                    row['DGA_TAXA_D1'],
                    row['DGA_TAXA_D2'],
                    row['DGA_TAXA_D3'],
                    row['DGA_CUSTO_N'],
                    row['DGA_CUSTO_D1'],
                    row['DGA_CUSTO_D2'],
                    row['DGA_CUSTO_D3'],
                    row['DGA_CUSTO_FALHA'],
                    row['DGA_INDISPONIBILIDADE_N'],
                    row['DGA_INDISPONIBILIDADE_D1'],
                    row['DGA_INDISPONIBILIDADE_D2'],
                    row['DGA_INDISPONIBILIDADE_D3'],
                    row['DGA_INDISPONIBILIDADE_FALHA'],
                ))
                inserted += 1

            except Exception as e:
                logger.warning(f"Erro ao inserir OS {row['OS_Id']}: {e}")
                continue

        self.connector.connection.commit()
        logger.info(f"{inserted} ordens de serviço inseridas (filtradas de {len(orders)}, {len(orders) - inserted} duplicatas ignoradas)")

        return inserted

    def _get_existing_os_ids(self, orders: pd.DataFrame) -> List[str]:
        """
        Busca IDs de OS que já existem no banco.

        Args:
            orders: DataFrame com as OS a inserir.

        Returns:
            Lista com IDs de OS existentes.
        """
        try:
            # Pegar IDs únicos de OS
            os_ids = orders['OS_Id'].unique().tolist()

            if not os_ids:
                return []

            # Buscar OS existentes
            os_ids_str = "', '".join(os_ids)
            query = f"""
            SELECT os_id
            FROM maintenance_orders
            WHERE os_id IN ('{os_ids_str}')
            """

            result = self.connector.fetch_data(query)

            if result is not None and not result.empty:
                return result['os_id'].tolist()

            return []

        except Exception as e:
            logger.warning(f"Erro ao buscar IDs de OS existentes: {e}")
            return []

    def get_sensor_data(
        self,
        equipment_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Busca dados de sensores do banco.

        Args:
            equipment_id: Filtrar por equipamento.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            DataFrame com dados.
        """
        query = "SELECT * FROM sensor_data WHERE 1=1"
        params = []

        if equipment_id:
            query += " AND equipment_id = ?"
            params.append(equipment_id)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp DESC"

        return self.connector.fetch_data(query, tuple(params) if params else None)

    def get_maintenance_orders(self, equipment_id: Optional[str] = None) -> pd.DataFrame:
        """
        Busca ordens de serviço do banco.

        Args:
            equipment_id: Filtrar por equipamento.

        Returns:
            DataFrame com ordens.
        """
        query = "SELECT * FROM maintenance_orders WHERE 1=1"
        params = []

        if equipment_id:
            query += " AND equipment_id = ?"
            params.append(equipment_id)

        query += " ORDER BY created_at DESC"

        return self.connector.fetch_data(query, tuple(params) if params else None)
