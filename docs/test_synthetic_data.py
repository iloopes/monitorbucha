#!/usr/bin/env python
"""Script para gerar dados sintéticos de teste."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def generate_test_data():
    """Gera dados de teste sintéticos para otimização."""

    print("="*70)
    print("Gerando Dados de Teste Sintéticos")
    print("="*70)

    # Configurações para gerar dados
    n_orders = 10  # Número de ordens de serviço

    # Criar dados de exemplo
    data = {
        'OS_Id': [f'OS_{i:03d}' for i in range(1, n_orders + 1)],
        'MotivoManutencao': ['DGA'] * n_orders,
        'estado_atual': [np.random.randint(0, 3) for _ in range(n_orders)],
        'data_medicao': pd.date_range('2025-01-01', periods=n_orders, freq='D'),
    }

    # Adicionar taxas de transição (simuladas)
    for i in range(4):  # 4 taxas (para 5 estados)
        data[f'taxa_{i}'] = np.random.uniform(0.01, 0.05, n_orders)

    # Adicionar custos operacionais (simulados)
    for i in range(5):  # 5 custos (um para cada estado)
        data[f'custo_{i}'] = np.random.uniform(100, 500, n_orders)

    # Adicionar indisponibilidade (horas)
    for i in range(5):  # 5 valores de indisponibilidade
        data[f'indisponibilidade_{i}'] = np.random.uniform(2, 48, n_orders)

    df = pd.DataFrame(data)

    # Salvar em CSV
    output_dir = Path('data/input')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'dados_teste.csv'
    df.to_csv(output_file, index=False, sep=';')

    print(f"\n✓ Dados gerados com sucesso!")
    print(f"  Arquivo: {output_file}")
    print(f"  Linhas: {len(df)}")
    print(f"  Colunas: {len(df.columns)}")
    print(f"\nPrimeiras linhas:\n{df.head()}")

    return output_file

def main():
    """Função principal."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Gerador de Dados de Teste Sintéticos".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print()

    try:
        output_file = generate_test_data()
        print("\n✓ Dados de teste gerados com sucesso!")
        print(f"\nProximate passo:")
        print(f"  python scripts/run_optimization.py -i {output_file} -o data/output/resultados.xlsx")
        return 0
    except Exception as e:
        print(f"\n✗ Erro ao gerar dados: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
