"""
Análise da fronteira de Pareto.
"""

from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from ..utils.logging_config import get_logger
from ..utils.metrics import MetricsCalculator

logger = get_logger(__name__)


class ParetoAnalyzer:
    """
    Analisador da fronteira de Pareto para seleção de soluções.
    """

    def __init__(self):
        """Inicializa o analisador de Pareto."""
        self.metrics_calculator = MetricsCalculator()

    def select_best_solution(
        self,
        pareto_front: pd.DataFrame,
        criterion: str = "knee_point",
        weights: Optional[Dict[str, float]] = None,
    ) -> Tuple[int, pd.Series]:
        """
        Seleciona a melhor solução da fronteira de Pareto.

        Args:
            pareto_front: DataFrame com a fronteira de Pareto.
            criterion: Critério de seleção:
                      - "min_cost": Minimiza custo
                      - "min_unavailability": Minimiza indisponibilidade
                      - "balanced": Solução balanceada (média normalizada)
                      - "knee_point": Ponto de joelho (melhor compromisso)
            weights: Pesos para critério "balanced" (padrão: {cost: 0.5, unavail: 0.5}).

        Returns:
            Tupla (índice, solução_selecionada).
        """
        if len(pareto_front) == 0:
            raise ValueError("Fronteira de Pareto vazia")

        if criterion == "min_cost":
            idx = pareto_front["Custo"].idxmin()
            logger.info(f"Solução selecionada por custo mínimo: índice {idx}")

        elif criterion == "min_unavailability":
            idx = pareto_front["Indisponibilidade"].idxmin()
            logger.info(f"Solução selecionada por indisponibilidade mínima: índice {idx}")

        elif criterion == "balanced":
            if weights is None:
                weights = {"cost": 0.5, "unavailability": 0.5}

            # Normalizar objetivos
            costs_norm = self.metrics_calculator.normalize_values(
                pareto_front["Custo"].tolist()
            )
            unavail_norm = self.metrics_calculator.normalize_values(
                pareto_front["Indisponibilidade"].tolist()
            )

            # Calcular score balanceado
            scores = [
                weights["cost"] * c + weights["unavailability"] * u
                for c, u in zip(costs_norm, unavail_norm)
            ]

            idx = np.argmin(scores)
            logger.info(f"Solução balanceada selecionada: índice {idx}")

        elif criterion == "knee_point":
            idx, _ = self.metrics_calculator.find_knee_point(
                pareto_front["Custo"].tolist(),
                pareto_front["Indisponibilidade"].tolist(),
            )
            logger.info(f"Ponto de joelho selecionado: índice {idx}")

        else:
            logger.warning(
                f"Critério desconhecido: {criterion}. Usando min_cost."
            )
            idx = pareto_front["Custo"].idxmin()

        return idx, pareto_front.iloc[idx]

    def calculate_hypervolume(
        self, pareto_front: pd.DataFrame, reference_point: Optional[List[float]] = None
    ) -> float:
        """
        Calcula o hipervolume da fronteira de Pareto.

        O hipervolume mede a qualidade da fronteira de Pareto.
        Valores maiores indicam fronteiras melhores.

        Args:
            pareto_front: DataFrame com a fronteira de Pareto.
            reference_point: Ponto de referência [custo_max, indisponibilidade_max].
                            Se None, usa 1.1× máximo de cada objetivo.

        Returns:
            Hipervolume.
        """
        if len(pareto_front) == 0:
            return 0.0

        costs = pareto_front["Custo"].values
        unavail = pareto_front["Indisponibilidade"].values

        if reference_point is None:
            reference_point = [
                costs.max() * 1.1,
                unavail.max() * 1.1,
            ]

        # Ordenar por custo
        sorted_indices = np.argsort(costs)
        costs_sorted = costs[sorted_indices]
        unavail_sorted = unavail[sorted_indices]

        # Calcular hipervolume (aproximação 2D)
        hypervolume = 0.0
        prev_unavail = reference_point[1]

        for i in range(len(costs_sorted)):
            width = reference_point[0] - costs_sorted[i]
            height = prev_unavail - unavail_sorted[i]

            if width > 0 and height > 0:
                hypervolume += width * height

            prev_unavail = unavail_sorted[i]

        logger.debug(f"Hipervolume calculado: {hypervolume:.2f}")

        return float(hypervolume)

    def analyze_pareto_front(self, pareto_front: pd.DataFrame) -> Dict[str, any]:
        """
        Realiza análise completa da fronteira de Pareto.

        Args:
            pareto_front: DataFrame com a fronteira de Pareto.

        Returns:
            Dicionário com estatísticas e análises.
        """
        if len(pareto_front) == 0:
            return {"n_solutions": 0, "error": "Fronteira de Pareto vazia"}

        costs = pareto_front["Custo"].values
        unavail = pareto_front["Indisponibilidade"].values
        times = pareto_front["t"].values

        # Estatísticas de custo
        cost_stats = {
            "min": float(costs.min()),
            "max": float(costs.max()),
            "mean": float(costs.mean()),
            "std": float(costs.std()),
            "median": float(np.median(costs)),
        }

        # Estatísticas de indisponibilidade
        unavail_stats = {
            "min": float(unavail.min()),
            "max": float(unavail.max()),
            "mean": float(unavail.mean()),
            "std": float(unavail.std()),
            "median": float(np.median(unavail)),
        }

        # Estatísticas de tempo
        time_stats = {
            "min": float(times.min()),
            "max": float(times.max()),
            "mean": float(times.mean()),
            "std": float(times.std()),
            "median": float(np.median(times)),
        }

        # Encontrar soluções extremas
        min_cost_idx = pareto_front["Custo"].idxmin()
        min_unavail_idx = pareto_front["Indisponibilidade"].idxmin()
        knee_idx, _ = self.metrics_calculator.find_knee_point(
            costs.tolist(), unavail.tolist()
        )

        extreme_solutions = {
            "min_cost": {
                "index": int(min_cost_idx),
                "t": float(pareto_front.loc[min_cost_idx, "t"]),
                "cost": float(pareto_front.loc[min_cost_idx, "Custo"]),
                "unavailability": float(
                    pareto_front.loc[min_cost_idx, "Indisponibilidade"]
                ),
            },
            "min_unavailability": {
                "index": int(min_unavail_idx),
                "t": float(pareto_front.loc[min_unavail_idx, "t"]),
                "cost": float(pareto_front.loc[min_unavail_idx, "Custo"]),
                "unavailability": float(
                    pareto_front.loc[min_unavail_idx, "Indisponibilidade"]
                ),
            },
            "knee_point": {
                "index": int(knee_idx),
                "t": float(pareto_front.iloc[knee_idx]["t"]),
                "cost": float(pareto_front.iloc[knee_idx]["Custo"]),
                "unavailability": float(
                    pareto_front.iloc[knee_idx]["Indisponibilidade"]
                ),
            },
        }

        # Hipervolume
        hypervolume = self.calculate_hypervolume(pareto_front)

        analysis = {
            "n_solutions": len(pareto_front),
            "cost_statistics": cost_stats,
            "unavailability_statistics": unavail_stats,
            "time_statistics": time_stats,
            "extreme_solutions": extreme_solutions,
            "hypervolume": hypervolume,
        }

        logger.info(
            f"Análise de Pareto concluída: {len(pareto_front)} soluções, "
            f"Hipervolume={hypervolume:.2f}"
        )

        return analysis

    def filter_solutions_by_constraints(
        self,
        pareto_front: pd.DataFrame,
        max_cost: Optional[float] = None,
        max_unavailability: Optional[float] = None,
        min_time: Optional[int] = None,
        max_time: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Filtra soluções da fronteira de Pareto por restrições.

        Args:
            pareto_front: DataFrame com a fronteira de Pareto.
            max_cost: Custo máximo aceitável.
            max_unavailability: Indisponibilidade máxima aceitável.
            min_time: Tempo mínimo até manutenção (dias).
            max_time: Tempo máximo até manutenção (dias).

        Returns:
            DataFrame filtrado.
        """
        filtered = pareto_front.copy()

        if max_cost is not None:
            filtered = filtered[filtered["Custo"] <= max_cost]

        if max_unavailability is not None:
            filtered = filtered[filtered["Indisponibilidade"] <= max_unavailability]

        if min_time is not None:
            filtered = filtered[filtered["t"] >= min_time]

        if max_time is not None:
            filtered = filtered[filtered["t"] <= max_time]

        logger.info(
            f"Filtro aplicado: {len(pareto_front)} → {len(filtered)} soluções"
        )

        return filtered
