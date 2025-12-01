#!/usr/bin/env python
"""Quick test to verify environment is working."""

import sys
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("TESTE RÁPIDO DO AMBIENTE".center(70))
print("="*70 + "\n")

# Test 1: Check Python version
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}\n")

# Test 2: Import key packages
try:
    import numpy as np
    print("✓ NumPy importado com sucesso")
    print(f"  Versão: {np.__version__}\n")
except ImportError as e:
    print(f"✗ Erro ao importar NumPy: {e}\n")
    sys.exit(1)

try:
    import pandas as pd
    print("✓ Pandas importado com sucesso")
    print(f"  Versão: {pd.__version__}\n")
except ImportError as e:
    print(f"✗ Erro ao importar Pandas: {e}\n")
    sys.exit(1)

try:
    import jmetal
    print("✓ jMetal importado com sucesso\n")
except ImportError as e:
    print(f"✗ Erro ao importar jMetal: {e}\n")
    sys.exit(1)

# Test 3: Import project modules
try:
    from src.data import DataLoader
    print("✓ DataLoader importado com sucesso")
except ImportError as e:
    print(f"✗ Erro ao importar DataLoader: {e}")
    sys.exit(1)

try:
    from src.models import MarkovChainModel
    print("✓ MarkovChainModel importado com sucesso")
except ImportError as e:
    print(f"✗ Erro ao importar MarkovChainModel: {e}")
    sys.exit(1)

try:
    from src.optimization import NSGA2Solver
    print("✓ NSGA2Solver importado com sucesso\n")
except ImportError as e:
    print(f"✗ Erro ao importar NSGA2Solver: {e}")
    sys.exit(1)

# Test 4: Create data directories
from pathlib import Path
dirs = ['data/input', 'data/output', 'data/examples']
for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
print("✓ Diretórios de dados criados/verificados\n")

# Test 5: Quick simulation
print("="*70)
print("TESTE DE FUNCIONAMENTO - Simulação de Markov")
print("="*70 + "\n")

rates = np.array([0.01, 0.02, 0.03, 0.04])
markov = MarkovChainModel(n_states=5)
transition_matrix = markov.build_transition_matrix(rates)
print(f"✓ Cadeia de Markov construída com sucesso")
print(f"  Matriz de transição (5x5):\n{transition_matrix}\n")

print("="*70)
print("✓ AMBIENTE CONFIGURADO COM SUCESSO!".center(70))
print("="*70)
print("\nPróximas etapas:")
print("  1. python test_synthetic_data.py     # Gerar dados de teste")
print("  2. python scripts/run_optimization.py # Executar otimização\n")
