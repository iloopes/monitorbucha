"""
Gerador de dados sintéticos de buchas de transformador (Bucha Virtual).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class AnomalyType(Enum):
    """Tipos de anomalias que podem ser injetadas."""
    SPIKE = "spike"  # Pico súbito
    DRIFT = "drift"  # Desvio gradual
    NOISE = "noise"  # Aumento de ruído
    SHIFT = "shift"  # Mudança de nível


@dataclass
class BushinConfig:
    """Configuração de uma bucha virtual."""
    equipment_id: str
    localizacao: str
    tipo_transformador: str
    tensao_nominal: float  # kV

    # Estado inicial
    estado_inicial: int = 0  # 0=Normal, 1=Degradado1, etc.
    corrente_fuga_inicial: float = 0.3  # mA
    tg_delta_inicial: float = 0.3  # %
    capacitancia_nominal: float = 300.0  # pF

    # Taxas de degradação
    taxa_degradacao_corrente: float = 0.001  # mA/dia
    taxa_degradacao_tg: float = 0.0005  # %/dia
    taxa_variacao_capacitancia: float = 0.01  # %/dia

    # Ruído
    ruido_corrente: float = 0.05  # mA
    ruido_tg: float = 0.02  # %
    ruido_capacitancia: float = 5.0  # pF


class VirtualBushingGenerator:
    """
    Gerador de dados sintéticos de buchas de transformador.

    Simula o comportamento real de buchas ao longo do tempo,
    incluindo degradação progressiva e ruído aleatório.
    Suporta injeção de anomalias para testes.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Inicializa o gerador de buchas virtuais.

        Args:
            seed: Seed para geração de números aleatórios (reprodutibilidade).
        """
        if seed is not None:
            np.random.seed(seed)

        self.configs: List[BushinConfig] = []
        self.anomaly_indices: Dict[str, List[int]] = {}  # Track injected anomalies
        logger.info("Gerador de Buchas Virtuais inicializado")

    def add_bushing(self, config: BushinConfig) -> None:
        """
        Adiciona uma bucha virtual ao gerador.

        Args:
            config: Configuração da bucha.
        """
        self.configs.append(config)
        logger.info(f"Bucha adicionada: {config.equipment_id}")

    def add_multiple_bushings(
        self,
        n_bushings: int,
        prefix: str = "BUCHA",
        localizacao: str = "SPGR",
        tipo_transformador: str = "ATF",
        tensao_nominal: float = 138.0,
    ) -> None:
        """
        Adiciona múltiplas buchas com configurações padrão.

        Args:
            n_bushings: Número de buchas a criar.
            prefix: Prefixo para IDs.
            localizacao: Localização das buchas.
            tipo_transformador: Tipo de transformador.
            tensao_nominal: Tensão nominal (kV).
        """
        for i in range(1, n_bushings + 1):
            # Variar levemente os parâmetros para cada bucha
            corrente_inicial = np.random.uniform(0.2, 0.5)
            tg_inicial = np.random.uniform(0.2, 0.4)
            taxa_deg = np.random.uniform(0.0005, 0.002)

            config = BushinConfig(
                equipment_id=f"{localizacao}.{tipo_transformador}{i}",
                localizacao=localizacao,
                tipo_transformador=tipo_transformador,
                tensao_nominal=tensao_nominal,
                corrente_fuga_inicial=corrente_inicial,
                tg_delta_inicial=tg_inicial,
                taxa_degradacao_corrente=taxa_deg,
            )

            self.add_bushing(config)

        logger.info(f"{n_bushings} buchas adicionadas com sucesso")

    def generate_data(
        self,
        start_date: datetime,
        end_date: datetime,
        frequency_hours: int = 1,
    ) -> pd.DataFrame:
        """
        Gera dados sintéticos para todas as buchas configuradas.

        Args:
            start_date: Data inicial de geração.
            end_date: Data final de geração.
            frequency_hours: Frequência de medição em horas.

        Returns:
            DataFrame com dados gerados.
        """
        if not self.configs:
            raise ValueError("Nenhuma bucha configurada. Use add_bushing() primeiro.")

        logger.info(
            f"Gerando dados de {start_date} a {end_date} "
            f"(frequência: {frequency_hours}h)"
        )

        # Criar timestamps
        timestamps = pd.date_range(
            start=start_date,
            end=end_date,
            freq=f"{frequency_hours}H"
        )

        all_data = []

        for config in self.configs:
            data = self._generate_bushing_data(config, timestamps)
            all_data.extend(data)

        df = pd.DataFrame(all_data)

        logger.info(
            f"Dados gerados: {len(df)} registros, "
            f"{len(self.configs)} buchas, "
            f"{len(timestamps)} timestamps"
        )

        return df

    def _generate_bushing_data(
        self,
        config: BushinConfig,
        timestamps: pd.DatetimeIndex
    ) -> List[Dict]:
        """
        Gera dados para uma bucha específica.

        Args:
            config: Configuração da bucha.
            timestamps: Timestamps para geração.

        Returns:
            Lista de dicionários com os dados.
        """
        data = []

        # Valores iniciais
        corrente = config.corrente_fuga_inicial
        tg_delta = config.tg_delta_inicial
        capacitancia = config.capacitancia_nominal

        for i, timestamp in enumerate(timestamps):
            # Degradação linear com tempo
            dias_passados = i * (timestamps.freq.n / 24)  # Converter para dias

            corrente_base = (
                config.corrente_fuga_inicial +
                config.taxa_degradacao_corrente * dias_passados
            )

            tg_base = (
                config.tg_delta_inicial +
                config.taxa_degradacao_tg * dias_passados
            )

            capacitancia_base = (
                config.capacitancia_nominal *
                (1 + config.taxa_variacao_capacitancia * dias_passados / 100)
            )

            # Adicionar ruído aleatório
            corrente_medida = corrente_base + np.random.normal(0, config.ruido_corrente)
            tg_medida = tg_base + np.random.normal(0, config.ruido_tg)
            capacitancia_medida = capacitancia_base + np.random.normal(0, config.ruido_capacitancia)

            # Garantir valores não negativos
            corrente_medida = max(0.0, corrente_medida)
            tg_medida = max(0.0, tg_medida)
            capacitancia_medida = max(0.0, capacitancia_medida)

            # Calcular estado de saúde
            estado = self._classify_health_state(corrente_medida)

            # Adicionar eventos ocasionais (picos)
            if np.random.random() < 0.01:  # 1% de chance
                corrente_medida *= np.random.uniform(1.5, 2.0)
                evento = "ANOMALIA_DETECTADA"
            else:
                evento = "NORMAL"

            data.append({
                'timestamp': timestamp,
                'equipment_id': config.equipment_id,
                'localizacao': config.localizacao,
                'tipo_transformador': config.tipo_transformador,
                'tensao_nominal': config.tensao_nominal,
                'corrente_fuga': round(corrente_medida, 4),
                'tg_delta': round(tg_medida, 4),
                'capacitancia': round(capacitancia_medida, 2),
                'estado_saude': estado,
                'evento': evento,
                'temperatura_ambiente': round(np.random.uniform(20, 35), 1),
                'umidade_relativa': round(np.random.uniform(40, 80), 1),
            })

        return data

    def inject_anomalies(
        self,
        data: pd.DataFrame,
        anomaly_rate: float = 5.0,
        anomaly_type: str = "spike",
        equipment_ids: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Injeta anomalias nos dados gerados para teste de detecção.

        Args:
            data: DataFrame com dados gerados.
            anomaly_rate: Porcentagem de dados a injetar anomalias (0-100).
            anomaly_type: Tipo de anomalia ("spike", "drift", "noise", "shift").
            equipment_ids: Lista de equipamentos para injetar anomalias (None = todos).

        Returns:
            DataFrame com anomalias injetadas.
        """
        data = data.copy()

        # Selecionar equipamentos alvo
        if equipment_ids is None:
            target_equipments = data['equipment_id'].unique().tolist()
        else:
            target_equipments = equipment_ids

        logger.info(
            f"Injetando anomalias: {anomaly_type} ({anomaly_rate}%) "
            f"em {len(target_equipments)} equipamentos"
        )

        # Processar cada equipamento
        for equipment_id in target_equipments:
            equipment_data = data[data['equipment_id'] == equipment_id]

            if len(equipment_data) == 0:
                logger.warning(f"Equipamento {equipment_id} não encontrado")
                continue

            # Calcular número de anomalias a injetar
            n_anomalies = max(1, int(len(equipment_data) * anomaly_rate / 100))

            # Selecionar índices aleatórios para anomalias
            anomaly_indices = np.random.choice(
                len(equipment_data),
                size=min(n_anomalies, len(equipment_data)),
                replace=False
            )

            # Aplicar anomalia
            equipment_indices = data[data['equipment_id'] == equipment_id].index

            for idx in anomaly_indices:
                actual_idx = equipment_indices[idx]

                if anomaly_type == "spike":
                    # Pico súbito (corrente se triplica)
                    data.loc[actual_idx, 'corrente_fuga'] *= np.random.uniform(2.5, 3.5)
                    data.loc[actual_idx, 'evento'] = "SPIKE_ANOMALICO"

                elif anomaly_type == "drift":
                    # Desvio gradual (aumento de 50-100%)
                    data.loc[actual_idx, 'corrente_fuga'] *= np.random.uniform(1.5, 2.0)
                    data.loc[actual_idx, 'tg_delta'] *= np.random.uniform(1.5, 2.0)
                    data.loc[actual_idx, 'evento'] = "DRIFT_ANOMALICO"

                elif anomaly_type == "noise":
                    # Aumento de ruído (50% de variação extra)
                    data.loc[actual_idx, 'corrente_fuga'] += np.random.normal(0, 0.2)
                    data.loc[actual_idx, 'tg_delta'] += np.random.normal(0, 0.1)
                    data.loc[actual_idx, 'evento'] = "NOISE_ANOMALICO"

                elif anomaly_type == "shift":
                    # Mudança de nível permanente (aumento constante)
                    data.loc[actual_idx, 'corrente_fuga'] += np.random.uniform(0.5, 1.5)
                    data.loc[actual_idx, 'evento'] = "SHIFT_ANOMALICO"

            # Garantir valores não negativos
            data.loc[equipment_indices, 'corrente_fuga'] = data.loc[equipment_indices, 'corrente_fuga'].apply(
                lambda x: max(0.0, x)
            )
            data.loc[equipment_indices, 'tg_delta'] = data.loc[equipment_indices, 'tg_delta'].apply(
                lambda x: max(0.0, x)
            )

            # Registrar anomalias injetadas
            self.anomaly_indices[equipment_id] = [
                equipment_indices[i] for i in anomaly_indices
            ]

            logger.info(
                f"Equipamento {equipment_id}: {len(anomaly_indices)} anomalias "
                f"injetadas ({anomaly_type})"
            )

        return data

    def _classify_health_state(self, corrente_fuga: float) -> int:
        """
        Classifica o estado de saúde baseado na corrente de fuga.

        Args:
            corrente_fuga: Corrente de fuga em mA.

        Returns:
            Estado de saúde (0-4).
        """
        if corrente_fuga < 0.5:
            return 0  # Normal
        elif corrente_fuga < 1.0:
            return 1  # Degradado 1
        elif corrente_fuga < 2.0:
            return 2  # Degradado 2
        elif corrente_fuga < 5.0:
            return 3  # Degradado 3
        else:
            return 4  # Falha

    def generate_maintenance_orders(
        self,
        data: pd.DataFrame,
        threshold_corrente: float = 1.0
    ) -> pd.DataFrame:
        """
        Gera ordens de serviço baseadas nos dados gerados.

        Args:
            data: DataFrame com dados das buchas.
            threshold_corrente: Limiar de corrente para gerar OS.

        Returns:
            DataFrame com ordens de serviço.
        """
        logger.info("Gerando ordens de serviço...")

        # Identificar equipamentos que ultrapassaram o limiar
        critical_equipment = data[data['corrente_fuga'] > threshold_corrente]

        # Agrupar por equipamento e pegar última leitura
        latest_readings = critical_equipment.groupby('equipment_id').last().reset_index()

        orders = []

        for idx, row in latest_readings.iterrows():
            # Gerar taxas de transição baseadas no estado
            estado = row['estado_saude']

            orders.append({
                'OS_Id': f"OS_{row['equipment_id']}_{datetime.now().strftime('%Y%m%d')}",
                'Equipamento': row['equipment_id'],
                'Localizacao': row['localizacao'],
                'MotivoManutencao': 'DGA',
                'MF_DGA': estado,
                'MF_DGA_DATA': row['timestamp'],
                'DGA_TAXA_N': 0.01 * (estado + 1),
                'DGA_TAXA_D1': 0.02 * (estado + 1),
                'DGA_TAXA_D2': 0.03 * (estado + 1),
                'DGA_TAXA_D3': 0.04 * (estado + 1),
                'DGA_CUSTO_N': 100,
                'DGA_CUSTO_D1': 200,
                'DGA_CUSTO_D2': 300,
                'DGA_CUSTO_D3': 400,
                'DGA_CUSTO_FALHA': 1000,
                'DGA_INDISPONIBILIDADE_N': 2,
                'DGA_INDISPONIBILIDADE_D1': 4,
                'DGA_INDISPONIBILIDADE_D2': 8,
                'DGA_INDISPONIBILIDADE_D3': 16,
                'DGA_INDISPONIBILIDADE_FALHA': 48,
            })

        os_df = pd.DataFrame(orders)
        logger.info(f"{len(os_df)} ordens de serviço geradas")

        return os_df

    def generate_scenario(
        self,
        scenario_name: str,
        n_bushings: int,
        days: int,
        degradation_rate: str = "medium",
        anomaly_rate: Optional[float] = None,
        anomaly_type: str = "spike",
        anomaly_equipments: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Gera um cenário completo de dados.

        Args:
            scenario_name: Nome do cenário.
            n_bushings: Número de buchas.
            days: Número de dias de dados.
            degradation_rate: Taxa de degradação ("low", "medium", "high").
            anomaly_rate: Porcentagem de dados para injetar anomalias (None = sem anomalias).
            anomaly_type: Tipo de anomalia ("spike", "drift", "noise", "shift").
            anomaly_equipments: Lista de IDs de equipamentos para injetar anomalias.

        Returns:
            Tupla (dados_sensores, ordens_servico).
        """
        logger.info(f"Gerando cenário: {scenario_name}")

        # Limpar configurações anteriores
        self.configs = []
        self.anomaly_indices = {}

        # Definir taxas de degradação
        rates = {
            "low": 0.0005,
            "medium": 0.001,
            "high": 0.003
        }

        # Adicionar buchas com diferentes estados iniciais
        for i in range(1, n_bushings + 1):
            estado_inicial = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            corrente_inicial = 0.3 + (estado_inicial * 0.3)

            config = BushinConfig(
                equipment_id=f"SPGR.ATF{i}",
                localizacao="SPGR",
                tipo_transformador=f"ATF{i}",
                tensao_nominal=138.0,
                estado_inicial=estado_inicial,
                corrente_fuga_inicial=corrente_inicial,
                taxa_degradacao_corrente=rates.get(degradation_rate, 0.001),
            )

            self.add_bushing(config)

        # Gerar dados
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        sensor_data = self.generate_data(start_date, end_date, frequency_hours=1)

        # Injetar anomalias se solicitado
        if anomaly_rate is not None and anomaly_rate > 0:
            sensor_data = self.inject_anomalies(
                sensor_data,
                anomaly_rate=anomaly_rate,
                anomaly_type=anomaly_type,
                equipment_ids=anomaly_equipments
            )
            logger.info(f"Anomalias injetadas: {anomaly_type} ({anomaly_rate}%)")

        maintenance_orders = self.generate_maintenance_orders(sensor_data)

        logger.info(
            f"Cenário '{scenario_name}' gerado: "
            f"{len(sensor_data)} registros, "
            f"{len(maintenance_orders)} OS"
        )

        return sensor_data, maintenance_orders
