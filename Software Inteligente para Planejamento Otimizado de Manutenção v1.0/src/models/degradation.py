"""
Modelo de degradação de equipamentos baseado em dados históricos.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..utils.logging_config import get_logger
from ..utils.metrics import MetricsCalculator

logger = get_logger(__name__)


class DegradationModel:
    """
    Modelo de degradação de equipamentos baseado em análise de tendência.
    """

    def __init__(self, thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Inicializa o modelo de degradação.

        Args:
            thresholds: Dicionário com limiares de classificação de estados.
                       Se None, usa valores padrão.
        """
        self.thresholds = thresholds or self._get_default_thresholds()
        self.metrics_calculator = MetricsCalculator()

    @staticmethod
    def _get_default_thresholds() -> Dict[str, Dict[str, float]]:
        """Retorna limiares padrão de classificação."""
        return {
            "corrente_fuga": {
                "normal": {"max": 0.5},
                "degradado1": {"max": 1.0},
                "degradado2": {"max": 2.0},
                "degradado3": {"max": 5.0},
            }
        }

    def classify_health_state(
        self, value: float, metric_name: str = "corrente_fuga"
    ) -> int:
        """
        Classifica o estado de saúde baseado no valor de uma métrica.

        Args:
            value: Valor da métrica.
            metric_name: Nome da métrica.

        Returns:
            Estado de saúde (0-4).
        """
        return self.metrics_calculator.classify_health_state(
            value, self.thresholds, metric_name
        )

    def calculate_degradation_rate(
        self,
        time_series: pd.DataFrame,
        value_column: str,
        time_column: str = "timestamp",
        method: str = "linear",
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calcula a taxa de degradação a partir de uma série temporal.

        Args:
            time_series: DataFrame com dados históricos.
            value_column: Nome da coluna com valores da métrica.
            time_column: Nome da coluna com timestamps.
            method: Método de regressão ("linear", "polynomial", "exponential").

        Returns:
            Tupla (taxa_degradacao, estatisticas):
                - taxa_degradacao: Coeficiente angular (unidade/dia)
                - estatisticas: Dict com R², erro médio, etc.
        """
        if len(time_series) < 2:
            logger.warning("Série temporal muito curta para calcular taxa de degradação")
            return 0.0, {}

        # Ordenar por tempo
        ts = time_series.sort_values(time_column).copy()

        # Converter timestamps para dias desde o início
        if pd.api.types.is_datetime64_any_dtype(ts[time_column]):
            time_days = (ts[time_column] - ts[time_column].iloc[0]).dt.total_seconds() / 86400
        else:
            time_days = np.arange(len(ts))

        values = ts[value_column].values

        # Regressão linear
        if method == "linear":
            coeffs = np.polyfit(time_days, values, deg=1)
            degradation_rate = float(coeffs[0])

            # Calcular R²
            predicted = np.polyval(coeffs, time_days)
            ss_res = np.sum((values - predicted) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            statistics = {
                "method": "linear",
                "r_squared": float(r_squared),
                "intercept": float(coeffs[1]),
                "slope": degradation_rate,
                "mean_error": float(np.mean(np.abs(values - predicted))),
                "n_points": len(ts),
            }

        elif method == "polynomial":
            degree = 2
            coeffs = np.polyfit(time_days, values, deg=degree)
            degradation_rate = float(coeffs[0])  # Coeficiente de maior grau

            predicted = np.polyval(coeffs, time_days)
            ss_res = np.sum((values - predicted) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            statistics = {
                "method": f"polynomial_deg{degree}",
                "r_squared": float(r_squared),
                "coefficients": coeffs.tolist(),
                "mean_error": float(np.mean(np.abs(values - predicted))),
                "n_points": len(ts),
            }

        else:
            logger.warning(f"Método desconhecido: {method}. Usando linear.")
            return self.calculate_degradation_rate(
                time_series, value_column, time_column, method="linear"
            )

        logger.debug(
            f"Taxa de degradação calculada: {degradation_rate:.6f} (R²={r_squared:.3f})"
        )

        return degradation_rate, statistics

    def predict_future_value(
        self,
        current_value: float,
        degradation_rate: float,
        days_ahead: int,
    ) -> float:
        """
        Prediz o valor futuro de uma métrica baseado na taxa de degradação.

        Args:
            current_value: Valor atual da métrica.
            degradation_rate: Taxa de degradação (unidade/dia).
            days_ahead: Número de dias no futuro.

        Returns:
            Valor predito.
        """
        predicted_value = current_value + (degradation_rate * days_ahead)
        return float(predicted_value)

    def estimate_time_to_failure(
        self,
        current_value: float,
        degradation_rate: float,
        failure_threshold: float,
    ) -> Optional[int]:
        """
        Estima o tempo até falha baseado na taxa de degradação atual.

        Args:
            current_value: Valor atual da métrica.
            degradation_rate: Taxa de degradação.
            failure_threshold: Limiar de falha.

        Returns:
            Número de dias até atingir o limiar de falha, ou None se não degradar.
        """
        if degradation_rate <= 0:
            # Equipamento não está degradando
            return None

        if current_value >= failure_threshold:
            # Já está em falha
            return 0

        days_to_failure = (failure_threshold - current_value) / degradation_rate
        return int(np.ceil(days_to_failure))

    def analyze_equipment_health(
        self,
        equipment_id: str,
        time_series: pd.DataFrame,
        value_column: str,
        time_column: str = "timestamp",
    ) -> Dict[str, any]:
        """
        Realiza análise completa de saúde de um equipamento.

        Args:
            equipment_id: Identificador do equipamento.
            time_series: DataFrame com dados históricos.
            value_column: Nome da coluna com valores.
            time_column: Nome da coluna com timestamps.

        Returns:
            Dicionário com análise completa.
        """
        logger.info(f"Analisando saúde do equipamento {equipment_id}")

        # Calcular estatísticas básicas
        current_value = float(time_series[value_column].iloc[-1])
        max_value = float(time_series[value_column].max())
        mean_value = float(time_series[value_column].mean())
        std_value = float(time_series[value_column].std())

        # Classificar estado atual
        current_state = self.classify_health_state(current_value)
        state_name = MetricsCalculator.get_state_name(current_state)

        # Calcular taxa de degradação
        degradation_rate, statistics = self.calculate_degradation_rate(
            time_series, value_column, time_column
        )

        # Estimar tempo até falha
        failure_threshold = self.thresholds["corrente_fuga"]["degradado3"]["max"]
        time_to_failure = self.estimate_time_to_failure(
            current_value, degradation_rate, failure_threshold
        )

        # Tendência
        if degradation_rate > 0.01:
            trend = "Deteriorando"
        elif degradation_rate < -0.01:
            trend = "Melhorando"
        else:
            trend = "Estável"

        analysis = {
            "equipment_id": equipment_id,
            "current_value": current_value,
            "max_value": max_value,
            "mean_value": mean_value,
            "std_value": std_value,
            "current_state": current_state,
            "state_name": state_name,
            "degradation_rate": degradation_rate,
            "trend": trend,
            "time_to_failure_days": time_to_failure,
            "statistics": statistics,
            "n_measurements": len(time_series),
        }

        logger.info(
            f"Equipamento {equipment_id}: Estado={state_name}, "
            f"Taxa={degradation_rate:.6f}, Tendência={trend}"
        )

        return analysis

    def rank_equipment_by_criticality(
        self, analyses: List[Dict[str, any]], top_n: int = 5
    ) -> List[Dict[str, any]]:
        """
        Classifica equipamentos por criticidade.

        Args:
            analyses: Lista de análises de equipamentos.
            top_n: Número de equipamentos mais críticos a retornar.

        Returns:
            Lista de análises ordenadas por criticidade (mais crítico primeiro).
        """
        # Calcular score de criticidade
        for analysis in analyses:
            score = MetricsCalculator.calculate_criticality_score(
                analysis["current_value"],
                analysis["degradation_rate"],
            )
            analysis["criticality_score"] = score

        # Ordenar por criticidade (decrescente)
        ranked = sorted(analyses, key=lambda x: x["criticality_score"], reverse=True)

        logger.info(f"Equipamentos ranqueados. Top {top_n} mais críticos identificados.")

        return ranked[:top_n]
