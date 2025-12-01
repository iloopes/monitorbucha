#!/usr/bin/env python
"""Script para testar se o ambiente está configurado corretamente."""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testa se todas as dependências estão instaladas."""
    print("="*60)
    print("Testando Dependências")
    print("="*60)

    dependencies = {
        'pandas': 'Processamento de dados',
        'numpy': 'Computação numérica',
        'jmetal': 'Otimização NSGA-II',
        'yaml': 'Configurações YAML',
        'matplotlib': 'Visualização de gráficos',
        'seaborn': 'Gráficos estatísticos',
        'tqdm': 'Barras de progresso',
        'openpyxl': 'Arquivos Excel',
        'pyarrow': 'Arquivos Parquet',
    }

    failed = []
    for pkg, description in dependencies.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:15} - {description}")
        except ImportError as e:
            print(f"✗ {pkg:15} - {description} [ERRO]")
            failed.append((pkg, str(e)))

    print()
    if failed:
        print(f"⚠ {len(failed)} dependência(s) faltando:")
        for pkg, error in failed:
            print(f"  - {pkg}: {error}")
        return False
    else:
        print("✓ Todas as dependências instaladas com sucesso!")
        return True

def test_project_imports():
    """Testa se os módulos do projeto podem ser importados."""
    print("\n" + "="*60)
    print("Testando Módulos do Projeto")
    print("="*60)

    modules = [
        ('src.data', 'Carregamento de dados'),
        ('src.models', 'Modelos matemáticos'),
        ('src.optimization', 'Otimização'),
        ('src.utils', 'Utilitários'),
    ]

    failed = []
    for module, description in modules:
        try:
            __import__(module)
            print(f"✓ {module:25} - {description}")
        except ImportError as e:
            print(f"✗ {module:25} - {description} [ERRO]")
            failed.append((module, str(e)))

    print()
    if failed:
        print(f"⚠ {len(failed)} módulo(s) com erro:")
        for mod, error in failed:
            print(f"  - {mod}: {error}")
        return False
    else:
        print("✓ Todos os módulos importados com sucesso!")
        return True

def test_config_files():
    """Verifica se os arquivos de configuração existem."""
    print("\n" + "="*60)
    print("Verificando Arquivos de Configuração")
    print("="*60)

    config_files = [
        'config/default.yaml',
        'config/nsga_params.yaml',
        'config/thresholds.yaml',
        'config/field_mappings.yaml',
    ]

    failed = []
    for config_file in config_files:
        path = Path(config_file)
        if path.exists():
            print(f"✓ {config_file}")
        else:
            print(f"✗ {config_file} [NÃO ENCONTRADO]")
            failed.append(config_file)

    print()
    if failed:
        print(f"⚠ {len(failed)} arquivo(s) de configuração faltando")
        return False
    else:
        print("✓ Todos os arquivos de configuração encontrados!")
        return True

def test_data_directories():
    """Verifica se os diretórios de dados existem."""
    print("\n" + "="*60)
    print("Verificando Diretórios de Dados")
    print("="*60)

    dirs_to_create = [
        'data/input',
        'data/output',
        'data/examples',
    ]

    for dir_path in dirs_to_create:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"  Criando: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ {dir_path} [criado]")

    print("\n✓ Diretórios de dados verificados/criados!")
    return True

def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Sistema Inteligente de Manutenção Preditiva v2.0".center(58) + "║")
    print("║" + "  Teste de Configuração do Ambiente".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print()

    results = {
        'Dependências': test_imports(),
        'Módulos': test_project_imports(),
        'Configurações': test_config_files(),
        'Diretórios': test_data_directories(),
    }

    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"{test_name:25} {status}")

    print("="*60)

    if all_passed:
        print("\n✓ AMBIENTE CONFIGURADO COM SUCESSO!")
        print("\nPróximos passos:")
        print("  1. Gerar dados de teste: python test_synthetic_data.py")
        print("  2. Executar otimização: python scripts/run_optimization.py -i data/input/exemplo.csv -o data/output/resultados.xlsx")
        return 0
    else:
        print("\n✗ ALGUNS TESTES FALHARAM")
        print("Corrija os erros acima e execute este script novamente.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
