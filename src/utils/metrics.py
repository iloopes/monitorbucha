"""
Calculadora de métricas e KPIs do sistema.
"""

from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class EquipmentMetrics:
    """Métricas de um equipamento."""

    equipamento_id: str
    corrente_fuga_atual: float
    corrente_fuga_max: float
    corrente_fuga_media: float
    taxa_degradacao: float
    estado_atual: int
    criticidade_score: float


class MetricsCalculator:
    """Calculadora de métricas e KPIs."""

    @staticmethod
    def calculate_degradation_rate(
        values: List[float], time_points: List[int]
    ) -> float:
        """
        Calcula a taxa de degradação usando regressão linear.

        Args:
            values: Lista de valores medidos.
            time_points: Lista de pontos temporais correspondentes.

        Returns:
            Taxa de degradação (coeficiente angular da reta).
        """
        if len(values) < 2:
            return 0.0

        # Usar numpy para regressão linear
        coefficients = np.polyfit(time_points, values, deg=1)
        return float(coefficients[0])

    @staticmethod
    def classify_health_state(
        value: float,
        thresholds: Dict[str, Dict[str, float]],
        metric_name: str = "corrente_fuga",
    ) -> int:
        """
        Classifica o estado de saúde baseado nos limiares.

        Args:
            value: Valor da métrica.
            thresholds: Dicionário com os limiares de classificação.
            metric_name: Nome da métrica (ex: "corrente_fuga").

        Returns:
            Estado de saúde (0=Normal, 1=Degradado1, 2=Degradado2, 3=Degradado3, 4=Falha).
        """
        metric_thresholds = thresholds.get(metric_name, {})

        # Normal
        if value <= metric_thresholds.get("normal", {}).get("max", float("inf")):
            return 0

        # Degradado1
        d1_max = metric_thresholds.get("degradado1", {}).get("max", float("inf"))
        if value <= d1_max:
            return 1

        # Degradado2
        d2_max = metric_thresholds.get("degradado2", {}).get("max", float("inf"))
        if value <= d2_max:
            return 2

        # Degradado3
        d3_max = metric_thresholds.get("degradado3", {}).get("max", float("inf"))
        if value <= d3_max:
            return 3

        # Falha
        return 4

    @staticmethod
    def calculate_criticality_score(
        current_value: float,
        degradation_rate: float,
        weights: Dict[str, float] = None,
    ) -> float:
        """
        Calcula o score de criticidade de um equipamento.

        Args:
            current_value: Valor atual da métrica principal.
            degradation_rate: Taxa de degradação.
            weights: Pesos para o cálculo (padrão: corrente=1.0, taxa=100.0).

        Returns:
            Score de criticidade.
        """
        if weights is None:
            weights = {"corrente_atual": 1.0, "taxa_degradacao": 100.0}

        score = (
            current_value * weights.get("corrente_atual", 1.0)
            + degradation_rate * weights.get("taxa_degradacao", 100.0)
        )

        return float(score)

    @staticmethod
    def get_state_name(state: int) -> str:
        """
        Obtém o nome do estado de saúde.

        Args:
            state: Código do estado (0-4).

        Returns:
            Nome do estado.
        """
        state_names = {
            0: "Normal",
            1: "Degradado 1",
            2: "Degradado 2",
            3: "Degradado 3",
            4: "Falha",
        }
        return state_names.get(state, "Desconhecido")

    @staticmethod
    def calculate_expected_cost(
        probabilities: np.ndarray, costs: List[float]
    ) -> float:
        """
        Calcula o custo esperado baseado nas probabilidades de cada estado.

        Args:
            probabilities: Array com probabilidades de cada estado.
            costs: Lista de custos por estado.

        Returns:
            Custo esperado.
        """
        return float(np.dot(probabilities, costs))

    @staticmethod
    def calculate_expected_unavailability(
        probabilities: np.ndarray, unavailability_hours: List[float]
    ) -> float:
        """
        Calcula a indisponibilidade esperada baseada nas probabilidades.

        Args:
            probabilities: Array com probabilidades de cada estado.
            unavailability_hours: Lista de horas de indisponibilidade por estado.

        Returns:
            Indisponibilidade esperada (horas).
        """
        return float(np.dot(probabilities, unavailability_hours))

    @staticmethod
    def normalize_values(values: List[float]) -> List[float]:
        """
        Normaliza valores para o intervalo [0, 1].

        Args:
            values: Lista de valores.

        Returns:
            Lista de valores normalizados.
        """
        values_array = np.array(values)
        min_val = np.min(values_array)
        max_val = np.max(values_array)

        if max_val == min_val:
            return [0.5] * len(values)

        return ((values_array - min_val) / (max_val - min_val)).tolist()

    @staticmethod
    def find_knee_point(
        costs: List[float], unavailabilities: List[float]
    ) -> Tuple[int, float]:
        """
        Encontra o ponto de joelho (knee point) na fronteira de Pareto.

        O ponto de joelho é a solução que representa o melhor compromisso
        entre os objetivos.

        Args:
            costs: Lista de custos.
            unavailabilities: Lista de indisponibilidades.

        Returns:
            Tupla (índice do ponto de joelho, distância máxima).
        """
        # Normalizar os valores
        costs_norm = np.array(MetricsCalculator.normalize_values(costs))
        unav_norm = np.array(MetricsCalculator.normalize_values(unavailabilities))

        # Calcular pontos inicial e final
        start_point = np.array([costs_norm[0], unav_norm[0]])
        end_point = np.array([costs_norm[-1], unav_norm[-1]])

        # Calcular distâncias de cada ponto à linha que conecta início e fim
        max_distance = 0.0
        knee_index = 0

        for i in range(len(costs)):
            point = np.array([costs_norm[i], unav_norm[i]])

            # Distância do ponto à linha
            distance = np.abs(
                np.cross(end_point - start_point, start_point - point)
            ) / np.linalg.norm(end_point - start_point)

            if distance > max_distance:
                max_distance = distance
                knee_index = i

        return knee_index, float(max_distance)
