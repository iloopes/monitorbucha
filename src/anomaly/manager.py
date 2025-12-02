"""
Gerenciador de anomalias com persistência em banco de dados.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from .autoencoder import MovingWindowAutoEncoder
from ..database.sql_server import SQLServerConnector, DatabaseManager
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class AnomalyManager:
    """Gerencia detecção e armazenamento de anomalias."""

    def __init__(self, db_connector: SQLServerConnector):
        """
        Inicializa o gerenciador de anomalias.

        Args:
            db_connector: Conector com banco de dados
        """
        self.db_connector = db_connector
        self.autoencoder = None
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Cria tabelas de anomalias se não existirem."""
        logger.info("Criando tabelas de anomalias...")

        create_anomaly_detections = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='anomaly_detections' AND xtype='U')
        CREATE TABLE anomaly_detections (
            id INT IDENTITY(1,1) PRIMARY KEY,
            equipment_id VARCHAR(100) NOT NULL,
            timestamp DATETIME NOT NULL,
            Q FLOAT,
            T2 FLOAT,
            Q_threshold FLOAT,
            T2_threshold FLOAT,
            is_anomaly BIT,
            reconstruction_error FLOAT,
            latent_distance FLOAT,
            severity VARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            INDEX idx_equipment_timestamp (equipment_id, timestamp),
            INDEX idx_is_anomaly (is_anomaly)
        )
        """

        create_anomaly_models = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='anomaly_models' AND xtype='U')
        CREATE TABLE anomaly_models (
            id INT IDENTITY(1,1) PRIMARY KEY,
            model_name VARCHAR(100) UNIQUE NOT NULL,
            model_arch VARCHAR(50),
            latent_dim INT,
            window_size INT,
            training_epochs INT,
            threshold_percentile FLOAT,
            model_data VARBINARY(MAX),
            scaler_data VARBINARY(MAX),
            trained_at DATETIME,
            created_at DATETIME DEFAULT GETDATE()
        )
        """

        try:
            self.db_connector.execute_query(create_anomaly_detections)
            self.db_connector.execute_query(create_anomaly_models)
            logger.info("Tabelas de anomalias criadas/verificadas com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao criar tabelas: {e}")

    def train_autoencoder(
        self,
        equipment_ids: Optional[List[str]] = None,
        model_name: str = "default_model",
        model_arch: str = "mlp",
        latent_dim: int = 5,
        window_size: int = 168,  # 1 semana de dados horários
        num_epochs: int = 50,
        learning_rate: float = 1e-3
    ) -> Dict:
        """
        Treina o autoencoder com dados do banco.

        Args:
            equipment_ids: Lista de equipamentos para treinar (None = todos)
            model_name: Nome do modelo
            model_arch: Arquitetura ("mlp" ou "cnn")
            latent_dim: Dimensão do espaço latente
            window_size: Tamanho da janela
            num_epochs: Número de épocas
            learning_rate: Taxa de aprendizado

        Returns:
            Dicionário com resultado do treinamento
        """
        logger.info(f"Iniciando treinamento do autoencoder ({model_arch})...")

        try:
            # Carregar dados do banco
            manager = DatabaseManager(self.db_connector)
            sensor_data = manager.connector.fetch_data("SELECT * FROM sensor_data ORDER BY timestamp ASC")

            if sensor_data.empty:
                return {
                    "status": "error",
                    "message": "Nenhum dado de sensor encontrado no banco"
                }

            # Filtrar por equipamento se especificado
            if equipment_ids:
                sensor_data = sensor_data[sensor_data['equipment_id'].isin(equipment_ids)]

            if sensor_data.empty:
                return {
                    "status": "error",
                    "message": f"Nenhum dado encontrado para os equipamentos: {equipment_ids}"
                }

            # Selecionar colunas numéricas
            numeric_cols = sensor_data.select_dtypes(include=['float64', 'int64']).columns
            numeric_cols = [col for col in numeric_cols if col not in ['id']]

            data = sensor_data[numeric_cols].fillna(method='ffill').fillna(method='bfill')

            # Criar e treinar autoencoder
            self.autoencoder = MovingWindowAutoEncoder(
                model_arch=model_arch,
                latent_dim=latent_dim
            )

            self.autoencoder.fit(
                data=pd.DataFrame(data),
                window_size=window_size,
                num_epochs=num_epochs,
                learning_rate=learning_rate
            )

            # Salvar modelo no banco (simplificado - sem serialização de pesos)
            self._save_model_metadata(
                model_name=model_name,
                model_arch=model_arch,
                latent_dim=latent_dim,
                window_size=window_size,
                num_epochs=num_epochs
            )

            return {
                "status": "success",
                "message": f"Autoencoder treinado com sucesso ({len(data)} amostras)",
                "model_name": model_name,
                "model_arch": model_arch,
                "data_points": len(data),
                "features": len(numeric_cols)
            }

        except Exception as e:
            logger.error(f"Erro ao treinar autoencoder: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def detect_anomalies(
        self,
        equipment_ids: Optional[List[str]] = None,
        threshold_percentile: float = 95.0,
        save_to_database: bool = True,
        randomize_anomalies: bool = False,
        anomaly_type: str = "auto",
        window_size: Optional[int] = None
    ) -> Dict:
        """
        Detecta anomalias nos dados atuais.

        Args:
            equipment_ids: Equipamentos a analisar (None = todos)
            threshold_percentile: Percentil para threshold
            save_to_database: Salvar resultados no banco
            randomize_anomalies: Ativar aleatorização de tipos de anomalias
            anomaly_type: Tipo de anomalia (auto, temperature, humidity, vibration, pressure, mixed)
            window_size: Tamanho da janela (deve ser igual ao treinamento)

        Returns:
            Dicionário com resultados
        """
        if self.autoencoder is None or not self.autoencoder.is_fitted:
            return {
                "status": "error",
                "message": "Autoencoder não foi treinado. Use train_autoencoder() primeiro."
            }

        logger.info(f"Detectando anomalias... (randomize={randomize_anomalies}, type={anomaly_type})")

        try:
            manager = DatabaseManager(self.db_connector)
            sensor_data = manager.connector.fetch_data("SELECT * FROM sensor_data ORDER BY timestamp ASC")

            if sensor_data.empty:
                return {
                    "status": "error",
                    "message": "Nenhum dado de sensor encontrado"
                }

            # Filtrar por equipamento
            if equipment_ids:
                sensor_data = sensor_data[sensor_data['equipment_id'].isin(equipment_ids)]

            # Selecionar colunas numéricas
            numeric_cols = sensor_data.select_dtypes(include=['float64', 'int64']).columns
            numeric_cols = [col for col in numeric_cols if col not in ['id']]

            data = sensor_data[numeric_cols].fillna(method='ffill').fillna(method='bfill')
            data.index = sensor_data['timestamp']

            logger.info(f"Dados carregados: {len(data)} registros, {len(numeric_cols)} features")
            logger.info(f"Features: {list(numeric_cols)}")

            # Usar window_size padrão (168h) se não fornecido
            detect_window_size = window_size if window_size is not None else 168
            logger.info(f"Detectando com window_size={detect_window_size}h, threshold_percentile={threshold_percentile}")

            # Detectar
            detections = self.autoencoder.detect(
                data=pd.DataFrame(data),
                window_size=detect_window_size,
                threshold_percentile=threshold_percentile
            )

            logger.info(f"Detecção retornou {len(detections)} linhas")

            # Adicionar tipos aleatórios de anomalias se solicitado
            if randomize_anomalies and not detections.empty:
                detections = self._randomize_anomaly_types(detections, anomaly_type)

            # Salvar no banco
            if save_to_database and not detections.empty:
                self._save_detections(detections, sensor_data)

            # Retornar resultado
            summary = self.autoencoder.get_anomaly_summary(detections)

            return {
                "status": "success",
                "message": "Detecção concluída",
                "summary": summary,
                "detections": detections.to_dict(orient='records')[:100]  # Primeiros 100
            }

        except Exception as e:
            logger.error(f"Erro na detecção: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def get_anomalies(
        self,
        equipment_id: Optional[str] = None,
        hours: int = 24,
        only_anomalies: bool = True
    ) -> pd.DataFrame:
        """
        Recupera anomalias detectadas.

        Args:
            equipment_id: Filtrar por equipamento
            hours: Horas para retroceder
            only_anomalies: Apenas registros anômalos

        Returns:
            DataFrame com anomalias
        """
        query = "SELECT * FROM anomaly_detections WHERE 1=1"
        params = []

        if equipment_id:
            query += " AND equipment_id = ?"
            params.append(equipment_id)

        query += f" AND timestamp >= DATEADD(hour, -{hours}, GETDATE())"

        if only_anomalies:
            query += " AND is_anomaly = 1"

        query += " ORDER BY timestamp DESC"

        try:
            return self.db_connector.fetch_data(query, tuple(params) if params else None)
        except Exception as e:
            logger.error(f"Erro ao buscar anomalias: {e}")
            return pd.DataFrame()

    def _save_model_metadata(
        self,
        model_name: str,
        model_arch: str,
        latent_dim: int,
        window_size: int,
        num_epochs: int
    ):
        """Salva ou atualiza metadados do modelo no banco."""
        try:
            cursor = self.db_connector.connection.cursor()

            # Verificar se modelo já existe
            check_query = "SELECT COUNT(*) as cnt FROM anomaly_models WHERE model_name = ?"
            cursor.execute(check_query, (model_name,))
            result = cursor.fetchone()
            model_exists = result[0] > 0 if result else False

            if model_exists:
                # UPDATE se já existe
                update_query = """
                UPDATE anomaly_models
                SET model_arch = ?, latent_dim = ?, window_size = ?, training_epochs = ?,
                    threshold_percentile = ?, trained_at = GETDATE()
                WHERE model_name = ?
                """
                cursor.execute(update_query, (model_arch, latent_dim, window_size, num_epochs, 95.0, model_name))
                logger.info(f"Metadados do modelo '{model_name}' atualizados")
            else:
                # INSERT se não existe
                insert_query = """
                INSERT INTO anomaly_models (model_name, model_arch, latent_dim, window_size, training_epochs, threshold_percentile, trained_at)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """
                cursor.execute(insert_query, (model_name, model_arch, latent_dim, window_size, num_epochs, 95.0))
                logger.info(f"Metadados do modelo '{model_name}' inseridos")

            self.db_connector.connection.commit()

        except Exception as e:
            logger.warning(f"Erro ao salvar metadados do modelo '{model_name}': {e}")

    def _randomize_anomaly_types(self, detections: pd.DataFrame, anomaly_type: str) -> pd.DataFrame:
        """
        Adiciona tipos aleatórios de anomalias aos dados detectados.

        Args:
            detections: DataFrame com detecções
            anomaly_type: Tipo de anomalia (auto, temperature, humidity, vibration, pressure, mixed)

        Returns:
            DataFrame com coluna 'anomaly_type' adicionada
        """
        import random
        import numpy as np

        if detections.empty:
            return detections

        # Tipos de anomalias disponíveis
        anomaly_types_map = {
            'temperature': ['sobrecarga_temperatura', 'gradiente_anormal', 'oscilacao_termica'],
            'humidity': ['umidade_excessiva', 'variacao_rapida', 'condensacao'],
            'vibration': ['vibracao_mecanica', 'desalinhamento', 'folga_estrutural'],
            'pressure': ['pressao_anormala', 'vazamento', 'selagem_falha'],
            'mixed': [
                'sobrecarga_temperatura', 'umidade_excessiva', 'vibracao_mecanica',
                'pressao_anormala', 'gradiente_anormal', 'oscilacao_termica'
            ]
        }

        # Se for "auto", escolher aleatoriamente entre todos os tipos
        if anomaly_type == 'auto':
            all_types = []
            for types_list in anomaly_types_map.values():
                all_types.extend(types_list)
            types_to_use = list(set(all_types))
        else:
            types_to_use = anomaly_types_map.get(anomaly_type, anomaly_types_map['mixed'])

        # Adicionar coluna com tipos aleatórios
        detections['anomaly_type'] = [
            random.choice(types_to_use) for _ in range(len(detections))
        ]

        logger.info(f"Tipos de anomalias aleatorizados: {anomaly_type}")
        logger.info(f"Tipos únicos gerados: {detections['anomaly_type'].nunique()}")

        return detections

    def _get_existing_detections(self, timestamps: List) -> set:
        """Obtém timestamps das detecções já existentes no banco."""
        if not timestamps:
            return set()

        try:
            query = "SELECT DISTINCT timestamp FROM anomaly_detections WHERE timestamp IN ({})".format(
                ",".join(["?" for _ in timestamps])
            )
            existing = self.db_connector.fetch_data(query, tuple(timestamps))
            return set(existing['timestamp'].tolist()) if not existing.empty else set()
        except Exception as e:
            logger.warning(f"Erro ao verificar detecções existentes: {e}")
            return set()

    def _save_detections(self, detections: pd.DataFrame, sensor_data: pd.DataFrame):
        """Salva detecções no banco com prevenção de duplicatas."""
        if detections.empty:
            logger.info("Nenhuma detecção para salvar")
            return

        # Obter timestamps existentes
        existing_timestamps = self._get_existing_detections(detections['timestamp'].tolist())

        # Filtrar detecções duplicadas
        new_detections = detections[~detections['timestamp'].isin(existing_timestamps)]

        if new_detections.empty:
            logger.info("Todas as detecções já existem no banco (0 novas inseridas)")
            return

        logger.info(f"Inserindo {len(new_detections)} novas detecções (ignoradas {len(detections) - len(new_detections)} duplicatas)")

        query = """
        INSERT INTO anomaly_detections (
            equipment_id, timestamp, Q, T2, Q_threshold, T2_threshold,
            is_anomaly, reconstruction_error, latent_distance, severity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = self.db_connector.connection.cursor()
        inserted = 0

        for _, detection in new_detections.iterrows():
            try:
                severity = "crítico" if detection['is_anomaly'] else "normal"

                # Obter equipment_id do timestamp
                eq_data = sensor_data[sensor_data['timestamp'] == detection['timestamp']]
                equipment_id = eq_data['equipment_id'].iloc[0] if not eq_data.empty else "unknown"

                cursor.execute(query, (
                    equipment_id,
                    detection['timestamp'],
                    float(detection['Q']),
                    float(detection['T2']),
                    float(detection['Q_threshold']),
                    float(detection['T2_threshold']),
                    int(detection['is_anomaly']),
                    float(detection['reconstruction_error']),
                    float(detection['latent_distance']),
                    severity
                ))
                inserted += 1
            except Exception as e:
                logger.warning(f"Erro ao inserir detecção: {e}")
                continue

        self.db_connector.connection.commit()
        logger.info(f"{inserted} detecções salvas no banco")
