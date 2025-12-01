"""
Script CLI para execução de otimização de manutenção.

Uso:
    python scripts/run_optimization.py --input data.csv --output results.xlsx
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import DataLoader, DataValidator, DataPreprocessor
from src.models import MarkovChainModel
from src.optimization import MaintenanceProblem, NSGA2Solver, ParetoAnalyzer
from src.utils import setup_logging, get_config_loader
from tqdm import tqdm
import pandas as pd
import numpy as np


def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema de Otimização de Manutenção Preditiva",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Otimização básica
  python scripts/run_optimization.py --input dados.csv --output resultados.xlsx

  # Com critério de seleção específico
  python scripts/run_optimization.py -i dados.csv -o resultados.xlsx -s min_cost

  # Com top N soluções
  python scripts/run_optimization.py -i dados.csv -o resultados.xlsx --top 5
        """
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Arquivo de entrada (CSV, Excel ou JSON) com ordens de serviço"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="data/output/resultados.xlsx",
        help="Arquivo de saída para resultados (padrão: data/output/resultados.xlsx)"
    )

    parser.add_argument(
        "-s", "--selection-criterion",
        type=str,
        choices=["knee_point", "min_cost", "min_unavailability", "balanced"],
        default="knee_point",
        help="Critério de seleção da melhor solução (padrão: knee_point)"
    )

    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Número de melhores soluções a exibir (padrão: 10)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nível de logging (padrão: INFO)"
    )

    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Pular validação de dados (não recomendado)"
    )

    return parser.parse_args()


def print_banner():
    """Exibe banner do sistema."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   Sistema Inteligente para Planejamento Otimizado de Manutenção  ║
║                          Versão 2.0.0                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def extract_os_parameters(os_row, field_mappings):
    """Extrai parâmetros de uma OS."""
    tipo = os_row['MotivoManutencao']
    mapping = field_mappings[tipo.upper() + "_mapping"] if tipo.upper() in ["DGA", "FQ"] else field_mappings["dga_mapping"]

    estado = int(os_row[mapping['estado_atual']])

    # Extrair taxas
    taxas_fields = list(mapping['taxas'].values())[estado:]
    rates = os_row[taxas_fields].values
    rates = np.array([float(str(x).replace(',', '.')) for x in rates])

    # Extrair custos operacionais
    custos_fields = list(mapping['custos'].values())[estado:]
    costs = os_row[custos_fields].values
    costs = np.array([float(str(x).replace(',', '.')) for x in costs])

    # Extrair indisponibilidade
    indisp_fields = list(mapping['indisponibilidade'].values())[estado:]
    unavailability = os_row[indisp_fields].values
    unavailability = np.array([float(str(x).replace(',', '.')) if isinstance(x, (int, float, str)) else x for x in unavailability])

    # Calcular offset temporal
    data_medicao = pd.to_datetime(os_row[mapping['data_medicao']])
    offset = (datetime.today() - data_medicao).days

    return rates, costs, unavailability, offset


def optimize_maintenance_orders(data, field_mappings, selection_criterion, logger):
    """Otimiza todas as ordens de serviço."""
    logger.info(f"Iniciando otimização de {len(data)} ordens de serviço...")

    all_results = []
    optimal_dates = []

    solver = NSGA2Solver()
    analyzer = ParetoAnalyzer()
    markov = MarkovChainModel(n_states=5)

    for idx, os in tqdm(data.iterrows(), total=len(data), desc="Otimizando OSs"):
        try:
            # Extrair parâmetros
            rates, costs, unavailability, offset = extract_os_parameters(os, field_mappings)

            # Criar modelo de Markov
            transition_matrix = markov.build_transition_matrix(rates)

            # Criar e resolver problema
            problem = MaintenanceProblem(
                transition_matrix=transition_matrix,
                operational_costs=costs,
                unavailability_costs=unavailability,
                time_offset=offset
            )

            pareto_front = solver.solve(problem)

            # Adicionar OS_id
            pareto_front['OS_Id'] = os['OS_Id']
            all_results.append(pareto_front)

            # Selecionar melhor solução
            best_idx, best_solution = analyzer.select_best_solution(
                pareto_front,
                criterion=selection_criterion
            )

            # Calcular data ótima
            data_otima = datetime.today() + timedelta(days=int(best_solution['t']))

            optimal_dates.append({
                'OS_Id': os['OS_Id'],
                'DataOtima': data_otima,
                'Dias': int(best_solution['t']),
                'Custo': best_solution['Custo'],
                'Indisponibilidade': best_solution['Indisponibilidade'],
                'Prioridade': 0  # Será atualizado
            })

        except Exception as e:
            logger.error(f"Erro ao otimizar OS {os['OS_Id']}: {e}")
            continue

    # Ordenar por custo e atualizar prioridades
    optimal_dates_df = pd.DataFrame(optimal_dates).sort_values('Custo').reset_index(drop=True)
    optimal_dates_df['Prioridade'] = range(len(optimal_dates_df), 0, -1)

    logger.info(f"Otimização concluída. {len(optimal_dates_df)} OSs processadas.")

    return all_results, optimal_dates_df


def print_results(optimal_dates, top_n, logger):
    """Exibe resultados no console."""
    print("\n" + "="*80)
    print(f"CALENDÁRIO OTIMIZADO DE MANUTENÇÃO - TOP {top_n}")
    print("="*80)
    print(f"{'Rank':<6} {'OS_Id':<15} {'Data Ótima':<12} {'Dias':<6} {'Custo':>10} {'Indisp.':>10}")
    print("-"*80)

    for idx, row in optimal_dates.head(top_n).iterrows():
        print(f"{row['Prioridade']:<6} {row['OS_Id']:<15} {row['DataOtima'].strftime('%Y-%m-%d'):<12} "
              f"{row['Dias']:<6} R$ {row['Custo']:>7.2f} {row['Indisponibilidade']:>8.2f}h")

    print("="*80)
    print(f"\nTotal de OSs otimizadas: {len(optimal_dates)}")
    print(f"Critério de seleção: {args.selection_criterion}")
    print()


def main():
    """Função principal."""
    global args
    args = parse_arguments()

    # Configurar logging
    logger = setup_logging(log_level=args.log_level)

    # Banner
    print_banner()

    # Carregar configurações
    logger.info("Carregando configurações...")
    config_loader = get_config_loader()
    field_mappings = config_loader.load("field_mappings")

    # Carregar dados
    logger.info(f"Carregando dados de: {args.input}")
    loader = DataLoader()
    data = loader.load_maintenance_orders(args.input)
    logger.info(f"Dados carregados: {len(data)} ordens de serviço")

    # Validar dados
    if not args.no_validation:
        logger.info("Validando dados...")
        validator = DataValidator()
        try:
            validator.validate_maintenance_order_data(data)
            logger.info("Validação concluída com sucesso")
        except ValueError as e:
            logger.error(f"Erro de validação: {e}")
            sys.exit(1)

    # Pré-processar
    logger.info("Pré-processando dados...")
    preprocessor = DataPreprocessor()
    data = preprocessor.normalize_numeric_columns(data)
    data = preprocessor.add_default_unavailability_fields(data)

    # Otimizar
    all_results, optimal_dates = optimize_maintenance_orders(
        data,
        field_mappings,
        args.selection_criterion,
        logger
    )

    # Exibir resultados
    print_results(optimal_dates, args.top, logger)

    # Salvar resultados
    logger.info(f"Salvando resultados em: {args.output}")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Salvar calendário
    loader.save_dataframe(optimal_dates, args.output)

    # Salvar fronteiras de Pareto
    if len(all_results) > 0:
        pareto_combined = pd.concat(all_results, ignore_index=True)
        pareto_path = output_path.parent / "fronteiras_de_pareto.xlsx"
        loader.save_dataframe(pareto_combined, pareto_path)
        logger.info(f"Fronteiras de Pareto salvas em: {pareto_path}")

    logger.info("Processo concluído com sucesso!")
    print("\n✓ Otimização finalizada!")


if __name__ == "__main__":
    main()
