"""
Definição do problema de otimização multi-objetivo de manutenção.
"""

import random
from typing import Dict, List

import numpy as np
from jmetal.core.problem import FloatProblem, FloatSolution

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class MaintenanceProblem(FloatProblem):
    """
    Problema de otimização multi-objetivo para planejamento de manutenção.

    Objetivos:
        1. Minimizar custo total (operacional + manutenção)
        2. Minimizar indisponibilidade esperada

    Variável de decisão:
        t: Tempo (em dias) até a manutenção programada [1, 3650]
    """

    def __init__(
        self,
        transition_matrix: np.ndarray,
        operational_costs: np.ndarray,
        unavailability_costs: np.ndarray,
        time_offset: int = 0,
        time_bounds: tuple = (1, 3650),
        cost_params: Dict[str, float] = None,
    ):
        """
        Inicializa o problema de otimização.

        Args:
            transition_matrix: Matriz de transição de Markov (n_states x n_states).
            operational_costs: Array com custos operacionais por estado.
            unavailability_costs: Array com custos de indisponibilidade por estado.
            time_offset: Offset temporal em dias (tempo desde última medição).
            time_bounds: Tupla (min_days, max_days) para variável de decisão.
            cost_params: Parâmetros para cálculo de custo de manutenção.
        """
        super(MaintenanceProblem, self).__init__()

        # Configurações do problema
        self.number_of_objectives_ = 2
        self.number_of_variables_ = 1
        self.number_of_constraints_ = 0

        # Parâmetros do modelo
        self.transition_matrix = transition_matrix
        self.operational_costs = operational_costs
        self.unavailability_costs = unavailability_costs
        self.time_offset = time_offset
        self.time_bounds = time_bounds

        # Parâmetros de custo de manutenção
        if cost_params is None:
            cost_params = {
                "base_cost": 500.0,  # Custo base de manutenção (R$)
                "decay_rate": 0.05,  # Taxa de decaimento do custo com tempo
            }
        self.cost_params = cost_params

        # Configurações do problema (requeridas por jMetal)
        self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ["Custo Total", "Indisponibilidade"]

        logger.debug(
            f"Problema de manutenção criado: "
            f"{self.number_of_variables_} variável, "
            f"{self.number_of_objectives_} objetivos"
        )

    @property
    def name(self) -> str:
        """Nome do problema."""
        return "Otimização de Manutenção Preditiva"

    @property
    def number_of_variables(self) -> int:
        """Número de variáveis de decisão."""
        return self.number_of_variables_

    @property
    def number_of_objectives(self) -> int:
        """Número de objetivos."""
        return self.number_of_objectives_

    @property
    def number_of_constraints(self) -> int:
        """Número de restrições."""
        return self.number_of_constraints_

    def create_solution(self) -> FloatSolution:
        """
        Cria uma solução inicial aleatória para o problema.

        Returns:
            Solução com tempo aleatório dentro dos limites.
        """
        new_solution = FloatSolution(
            lower_bound=[self.time_bounds[0]],
            upper_bound=[self.time_bounds[1]],
            number_of_objectives=self.number_of_objectives_,
        )

        # Gerar tempo aleatório
        new_solution.variables[0] = float(
            random.randrange(self.time_bounds[0], self.time_bounds[1])
        )

        return new_solution

    def calculate_state_probabilities(self, n_cycles: int) -> np.ndarray:
        """
        Calcula as probabilidades de estar em cada estado após n ciclos.

        Args:
            n_cycles: Número de ciclos (dias) a simular.

        Returns:
            Array com probabilidades de cada estado.
        """
        # Condição inicial: Normal (estado 0)
        n_states = self.transition_matrix.shape[0]
        initial_condition = np.zeros((1, n_states))
        initial_condition[0, 0] = 1

        # Calcular T^n
        transition_power = np.linalg.matrix_power(
            self.transition_matrix, n_cycles + self.time_offset
        )

        # P(t) = P₀ × T^n
        probabilities = np.dot(initial_condition, transition_power)

        return probabilities[0]

    def calculate_total_cost(self, probabilities: np.ndarray, time_days: int) -> float:
        """
        Calcula o custo total (operacional + manutenção).

        Fórmula:
            Custo_operacional = Σ(P_i × Custo_i) × (1 + P_degradado)
            Custo_manutenção = base_cost × exp(-decay_rate × t)
            Custo_total = Custo_operacional + Custo_manutenção

        Args:
            probabilities: Probabilidades de cada estado.
            time_days: Tempo até manutenção (dias).

        Returns:
            Custo total.
        """
        # Probabilidade de estar em estado normal
        prob_normal = probabilities[0]
        prob_degraded = 1.0 - prob_normal

        # Custo operacional esperado
        expected_operational_cost = np.dot(probabilities, self.operational_costs)

        # Ajuste por degradação
        operational_cost_adjusted = expected_operational_cost * (1.0 + prob_degraded)

        # Custo de manutenção (decresce com tempo)
        # Incentiva postergar manutenção quando degradação é baixa
        maintenance_cost = self.cost_params["base_cost"] * np.exp(
            -self.cost_params["decay_rate"] * time_days
        )

        total_cost = operational_cost_adjusted + maintenance_cost

        return float(total_cost)

    def calculate_unavailability(self, probabilities: np.ndarray) -> float:
        """
        Calcula a indisponibilidade esperada.

        Fórmula:
            Indisponibilidade_base = Σ(P_i × Indisponibilidade_i)
            Penalidade_degradação = (exp(2 × P_degradado) - 1) × 100
            Indisponibilidade_total = Indisponibilidade_base + Penalidade

        Args:
            probabilities: Probabilidades de cada estado.

        Returns:
            Indisponibilidade total.
        """
        # Probabilidade de estar degradado
        prob_normal = probabilities[0]
        prob_degraded = 1.0 - prob_normal

        # Indisponibilidade base esperada
        expected_unavailability = np.dot(probabilities, self.unavailability_costs)

        # Penalidade exponencial por degradação
        # Equipamento degradado fica indisponível com maior frequência
        degradation_penalty = (np.exp(2.0 * prob_degraded) - 1.0) * 100

        total_unavailability = expected_unavailability + degradation_penalty

        return float(total_unavailability)

    def evaluate(self, solution: FloatSolution) -> FloatSolution:
        """
        Avalia uma solução calculando os valores dos objetivos.

        Args:
            solution: Solução a ser avaliada (contém tempo t).

        Returns:
            Solução com objetivos calculados.
        """
        # Extrair tempo da solução
        time_days = int(solution.variables[0])

        # Calcular probabilidades de estados
        probabilities = self.calculate_state_probabilities(time_days)

        # Objetivo 1: Minimizar custo total
        solution.objectives[0] = self.calculate_total_cost(probabilities, time_days)

        # Objetivo 2: Minimizar indisponibilidade
        solution.objectives[1] = self.calculate_unavailability(probabilities)

        return solution

    def get_name(self) -> str:
        """Retorna o nome do problema (compatibilidade jMetal)."""
        return self.name
