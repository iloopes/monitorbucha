"""
Modelo de Cadeia de Markov para transições de estados de equipamentos.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class MarkovChainModel:
    """
    Modelo de Cadeia de Markov para modelar transições de estados de equipamentos.

    Estados:
        0: Normal
        1: Degradado 1
        2: Degradado 2
        3: Degradado 3
        4: Falha (estado absorvente)
    """

    def __init__(self, n_states: int = 5):
        """
        Inicializa o modelo de Cadeia de Markov.

        Args:
            n_states: Número de estados (padrão: 5).
        """
        self.n_states = n_states
        self.state_names = ["Normal", "Degradado 1", "Degradado 2", "Degradado 3", "Falha"]
        self.transition_matrix: np.ndarray = None

    def build_transition_matrix(self, transition_rates: np.ndarray) -> np.ndarray:
        """
        Constrói a matriz de transição baseada nas taxas de transição.

        A matriz de transição T tem a forma:
        ```
        ┌─────────────────────────────────┐
        │ 1-λ₀  λ₀    0     0     0     │
        │  0   1-λ₁  λ₁    0     0     │
        │  0    0   1-λ₂  λ₂    0     │
        │  0    0    0   1-λ₃  λ₃    │
        │  0    0    0    0     1     │
        └─────────────────────────────────┘
        ```

        Args:
            transition_rates: Array com as taxas de transição entre estados.
                             Dimensão: (n_states-1,) pois o último estado é absorvente.

        Returns:
            Matriz de transição de estados (n_states x n_states).

        Examples:
            >>> model = MarkovChainModel()
            >>> rates = np.array([0.1, 0.2, 0.3, 0.4])
            >>> T = model.build_transition_matrix(rates)
            >>> T.shape
            (5, 5)
        """
        # Adicionar taxa zero para o estado de falha (absorvente)
        rates_with_failure = np.append(transition_rates, 0)

        # Diagonal principal: 1 - λᵢ (probabilidade de permanecer no estado)
        transition = np.diag(1 - rates_with_failure, 0)

        # Diagonal superior: λᵢ (probabilidade de transição para próximo estado)
        transition += np.diag(rates_with_failure[:-1], 1)

        # Estado de falha é absorvente (probabilidade 1 de permanecer)
        transition[-1, -1] = 1

        self.transition_matrix = transition
        logger.debug(f"Matriz de transição construída: {transition.shape}")

        return transition

    def calculate_state_probabilities(
        self, n_cycles: int, initial_state: int = 0
    ) -> np.ndarray:
        """
        Calcula as probabilidades de estar em cada estado após n ciclos.

        Usa a equação: P(t) = P₀ × T^n

        Args:
            n_cycles: Número de ciclos (dias) a simular.
            initial_state: Estado inicial (padrão: 0 = Normal).

        Returns:
            Array com probabilidades de cada estado após n ciclos.

        Raises:
            ValueError: Se a matriz de transição não foi construída.

        Examples:
            >>> model = MarkovChainModel()
            >>> rates = np.array([0.01, 0.02, 0.03, 0.04])
            >>> model.build_transition_matrix(rates)
            >>> probs = model.calculate_state_probabilities(100)
            >>> probs.sum()
            1.0
        """
        if self.transition_matrix is None:
            raise ValueError(
                "Matriz de transição não foi construída. "
                "Chame build_transition_matrix() primeiro."
            )

        # Condição inicial: vetor com probabilidade 1 no estado inicial
        initial_condition = np.zeros((1, self.n_states))
        initial_condition[0, initial_state] = 1

        # Calcular T^n usando exponenciação de matriz
        transition_power = np.linalg.matrix_power(self.transition_matrix, n_cycles)

        # Calcular P(t) = P₀ × T^n
        probabilities = np.dot(initial_condition, transition_power)

        return probabilities[0]

    def calculate_expected_value(
        self, probabilities: np.ndarray, values: np.ndarray
    ) -> float:
        """
        Calcula o valor esperado baseado nas probabilidades de cada estado.

        Args:
            probabilities: Array com probabilidades de cada estado.
            values: Array com valores associados a cada estado.

        Returns:
            Valor esperado.

        Examples:
            >>> model = MarkovChainModel()
            >>> probs = np.array([0.7, 0.2, 0.1, 0.0, 0.0])
            >>> costs = np.array([100, 200, 300, 400, 500])
            >>> expected = model.calculate_expected_value(probs, costs)
            >>> expected
            130.0
        """
        return float(np.dot(probabilities, values))

    def simulate_trajectory(
        self, n_cycles: int, initial_state: int = 0, n_simulations: int = 1000
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Simula trajetórias individuais da cadeia de Markov.

        Args:
            n_cycles: Número de ciclos a simular.
            initial_state: Estado inicial.
            n_simulations: Número de simulações Monte Carlo.

        Returns:
            Tupla (estados_finais, distribuicao_estados):
                - estados_finais: Lista com o estado final de cada simulação
                - distribuicao_estados: Dict com frequência de cada estado final
        """
        if self.transition_matrix is None:
            raise ValueError("Matriz de transição não foi construída.")

        final_states = []

        for _ in range(n_simulations):
            current_state = initial_state

            for _ in range(n_cycles):
                # Probabilidades de transição do estado atual
                transition_probs = self.transition_matrix[current_state, :]

                # Escolher próximo estado baseado nas probabilidades
                next_state = np.random.choice(
                    self.n_states, p=transition_probs
                )

                current_state = next_state

                # Se atingiu estado absorvente (Falha), parar
                if current_state == self.n_states - 1:
                    break

            final_states.append(current_state)

        # Calcular distribuição de estados finais
        unique, counts = np.unique(final_states, return_counts=True)
        distribution = {int(state): float(count / n_simulations)
                       for state, count in zip(unique, counts)}

        logger.debug(
            f"Simulação concluída: {n_simulations} trajetórias, {n_cycles} ciclos"
        )

        return final_states, distribution

    def get_steady_state(self, tolerance: float = 1e-10, max_iterations: int = 10000) -> np.ndarray:
        """
        Calcula o estado estacionário da cadeia de Markov.

        Para uma cadeia de Markov com estado absorvente (Falha),
        o estado estacionário será [0, 0, 0, 0, 1] (todos eventualmente falham).

        Args:
            tolerance: Tolerância para convergência.
            max_iterations: Número máximo de iterações.

        Returns:
            Array com probabilidades do estado estacionário.
        """
        if self.transition_matrix is None:
            raise ValueError("Matriz de transição não foi construída.")

        # Estado inicial uniforme
        state = np.ones(self.n_states) / self.n_states

        for i in range(max_iterations):
            new_state = np.dot(state, self.transition_matrix)

            # Verificar convergência
            if np.allclose(state, new_state, atol=tolerance):
                logger.debug(f"Estado estacionário convergiu em {i} iterações")
                return new_state

            state = new_state

        logger.warning(
            f"Estado estacionário não convergiu em {max_iterations} iterações"
        )
        return state

    def calculate_mean_time_to_failure(self, initial_state: int = 0) -> float:
        """
        Calcula o tempo médio até falha (MTTF) a partir de um estado inicial.

        Args:
            initial_state: Estado inicial.

        Returns:
            Tempo médio (em ciclos) até atingir o estado de falha.
        """
        if self.transition_matrix is None:
            raise ValueError("Matriz de transição não foi construída.")

        # Remover o estado absorvente (falha)
        Q = self.transition_matrix[:-1, :-1]
        I = np.eye(Q.shape[0])

        # Calcular matriz fundamental N = (I - Q)^(-1)
        try:
            N = np.linalg.inv(I - Q)
        except np.linalg.LinAlgError:
            logger.error("Não foi possível calcular a matriz fundamental")
            return np.inf

        # Tempo esperado = soma da linha correspondente ao estado inicial
        mttf = N[initial_state, :].sum()

        logger.debug(f"MTTF a partir do estado {initial_state}: {mttf:.2f} ciclos")

        return float(mttf)
