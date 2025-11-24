"""
Otimizador de manutenção que integra Cadeia de Markov + NSGA-II.
"""

import numpy as np
from typing import List, Dict
from ..models import MarkovChainModel
from .problem import MaintenanceProblem
from .solver import NSGA2Solver
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class MaintenanceOptimizer:
    """Otimizador completo de manutenção preditiva."""

    def __init__(
        self,
        max_evaluations: int = 4000,
        population_size: int = 200
    ):
        """
        Inicializa o otimizador.

        Args:
            max_evaluations: Número máximo de avaliações do NSGA-II.
            population_size: Tamanho da população do algoritmo genético.
        """
        self.max_evaluations = max_evaluations
        self.population_size = population_size
        logger.info(f"Otimizador criado: pop={population_size}, eval={max_evaluations}")

    def optimize(
        self,
        transition_rates: List[float],
        operational_costs: List[float],
        unavailabilities: List[float],
        initial_state: int = 0
    ) -> List[Dict]:
        """
        Executa otimização completa.

        Args:
            transition_rates: Taxas de transição [N, D1, D2, D3] -> [D1, D2, D3, F].
            operational_costs: Custos operacionais por estado [N, D1, D2, D3, F].
            unavailabilities: Indisponibilidades por estado [N, D1, D2, D3, F].
            initial_state: Estado inicial do equipamento.

        Returns:
            Lista de soluções da fronteira de Pareto.
        """
        try:
            # Criar modelo de Markov e construir matriz de transição
            markov_model = MarkovChainModel()
            transition_matrix = markov_model.build_transition_matrix(np.array(transition_rates))

            # Criar problema de otimização
            problem = MaintenanceProblem(
                transition_matrix=transition_matrix,
                operational_costs=np.array(operational_costs),
                unavailability_costs=np.array(unavailabilities),
                time_offset=0
            )

            # Executar NSGA-II
            config = {
                "algorithm": {
                    "population_size": self.population_size,
                    "offspring_population_size": self.population_size,
                    "max_evaluations": self.max_evaluations
                }
            }

            solver = NSGA2Solver(config=config)
            solutions_df = solver.solve(problem)

            # Converter DataFrame para formato de dicionário
            pareto_front = []
            for _, row in solutions_df.iterrows():
                pareto_front.append({
                    "t_days": int(row['t']),
                    "cost": float(row['Custo']),
                    "unavailability": float(row['Indisponibilidade'])
                })

            logger.info(f"Otimização concluída: {len(pareto_front)} soluções no Pareto")
            return pareto_front

        except Exception as e:
            logger.error(f"Erro na otimização: {e}")
            raise
