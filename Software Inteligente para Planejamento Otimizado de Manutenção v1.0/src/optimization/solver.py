"""
Solver NSGA-II para otimização multi-objetivo.
"""

from typing import Dict, Optional

import pandas as pd
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator.crossover import SBXCrossover
from jmetal.operator.mutation import PolynomialMutation
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from ..utils.logging_config import get_logger
from ..utils.config_loader import get_config_loader
from .problem import MaintenanceProblem

logger = get_logger(__name__)


class NSGA2Solver:
    """
    Solver baseado em NSGA-II para problemas de otimização multi-objetivo.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o solver NSGA-II.

        Args:
            config: Dicionário com configurações do algoritmo.
                   Se None, carrega da configuração YAML.
        """
        if config is None:
            config_loader = get_config_loader()
            config = config_loader.get_nsga_params()

        self.config = config
        logger.info("NSGA-II Solver inicializado")

    def solve(self, problem: MaintenanceProblem) -> pd.DataFrame:
        """
        Executa a otimização usando NSGA-II.

        Args:
            problem: Problema de otimização a resolver.

        Returns:
            DataFrame com a fronteira de Pareto.
            Colunas: ['t', 'Custo', 'Indisponibilidade']
        """
        logger.info(f"Iniciando otimização: {problem.name}")

        # Configurações do algoritmo
        algo_config = self.config.get("algorithm", {})
        pop_size = algo_config.get("population_size", 200)
        offspring_size = algo_config.get("offspring_population_size", 200)
        max_eval = algo_config.get("max_evaluations", 4000)

        # Configurações dos operadores
        operators_config = self.config.get("operators", {})

        # Crossover
        crossover_config = operators_config.get("crossover", {})
        crossover_prob = crossover_config.get("probability", 1.0)
        crossover_idx = crossover_config.get("distribution_index", 20)
        crossover = SBXCrossover(
            probability=crossover_prob, distribution_index=crossover_idx
        )

        # Mutação
        mutation_config = operators_config.get("mutation", {})
        mutation_idx = mutation_config.get("distribution_index", 20)
        mutation_prob = 1.0 / problem.number_of_variables
        mutation = PolynomialMutation(
            probability=mutation_prob, distribution_index=mutation_idx
        )

        # Critério de terminação
        termination = StoppingByEvaluations(max_evaluations=max_eval)

        # Criar algoritmo NSGA-II
        algorithm = NSGAII(
            problem=problem,
            population_size=pop_size,
            offspring_population_size=offspring_size,
            mutation=mutation,
            crossover=crossover,
            termination_criterion=termination,
        )

        logger.info(
            f"Configuração: população={pop_size}, "
            f"offspring={offspring_size}, "
            f"avaliações={max_eval}"
        )

        # Executar otimização
        algorithm.run()

        logger.info("Otimização concluída")

        # Extrair fronteira de Pareto
        pareto_front = get_non_dominated_solutions(algorithm.solutions)

        logger.info(f"Fronteira de Pareto: {len(pareto_front)} soluções")

        # Converter para DataFrame
        front_df = self._solutions_to_dataframe(pareto_front)

        return front_df

    def _solutions_to_dataframe(self, solutions: list) -> pd.DataFrame:
        """
        Converte lista de soluções para DataFrame.

        Args:
            solutions: Lista de FloatSolution.

        Returns:
            DataFrame ordenado por custo.
        """
        data = []

        for solution in solutions:
            data.append(
                {
                    "t": solution.variables[0],
                    "Custo": solution.objectives[0],
                    "Indisponibilidade": solution.objectives[1],
                }
            )

        df = pd.DataFrame(data)

        # Ordenar por custo
        df = df.sort_values("Custo").reset_index(drop=True)

        return df

    def get_algorithm_info(self) -> Dict[str, any]:
        """
        Retorna informações sobre a configuração do algoritmo.

        Returns:
            Dicionário com informações do algoritmo.
        """
        algo_config = self.config.get("algorithm", {})
        operators_config = self.config.get("operators", {})

        return {
            "algorithm": algo_config.get("name", "NSGA-II"),
            "population_size": algo_config.get("population_size", 200),
            "offspring_size": algo_config.get("offspring_population_size", 200),
            "max_evaluations": algo_config.get("max_evaluations", 4000),
            "crossover": operators_config.get("crossover", {}),
            "mutation": operators_config.get("mutation", {}),
        }
