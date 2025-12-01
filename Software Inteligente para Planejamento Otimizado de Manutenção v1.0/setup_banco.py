"""
Script de setup automático do banco de dados.
Executa: python setup_banco.py
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pyodbc
    from src.database import SQLServerConnector, DatabaseManager
    from src.utils.logging_config import setup_logging
except ImportError as e:
    print("❌ Erro: Dependências não instaladas!")
    print("\nExecute primeiro:")
    print("  pip install pyodbc pyyaml")
    print(f"\nErro detalhado: {e}")
    sys.exit(1)


def print_banner():
    """Exibe banner do script."""
    print("="*70)
    print(" Setup Automatico do Banco de Dados")
    print(" Sistema de Manutencao Preditiva - Bucha Virtual")
    print("="*70)


def main():
    """Função principal."""
    print_banner()

    # Configurar logging
    logger = setup_logging(log_level="INFO")

    # Configurações do banco
    SERVER = "DESKTOP-0L1FQAQ\\KUZUSHI"
    DATABASE = "MaintenanceDB"

    print(f"\nConfiguracoes:")
    print(f"   Servidor: {SERVER}")
    print(f"   Banco: {DATABASE}")
    print(f"   Autenticacao: Windows (Trusted Connection)")
    print("\nIniciando setup...")

    try:
        # Passo 1: Conectar ao SQL Server
        print("\n[1/4] Conectando ao SQL Server...")

        # Primeiro conectar ao master para criar o banco
        connector_master = SQLServerConnector(
            server=SERVER,
            database="master",  # Conectar ao master primeiro
            trusted_connection=True
        )
        connector_master.connect()
        print("   OK - Conectado ao master")

        # Passo 2: Criar banco de dados
        print("\n[2/4] Criando banco de dados...")

        create_db_query = f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DATABASE}')
        BEGIN
            CREATE DATABASE {DATABASE}
            PRINT 'Banco de dados {DATABASE} criado'
        END
        ELSE
        BEGIN
            PRINT 'Banco de dados {DATABASE} já existe'
        END
        """

        try:
            connector_master.execute_query(create_db_query)
            print(f"   OK - Banco '{DATABASE}' verificado/criado")
        except Exception as e:
            print(f"   AVISO: {e}")

        connector_master.disconnect()

        # Passo 3: Conectar ao banco criado
        print(f"\n[3/4] Conectando ao banco '{DATABASE}'...")

        connector = SQLServerConnector(
            server=SERVER,
            database=DATABASE,
            trusted_connection=True
        )
        connector.connect()
        print(f"   OK - Conectado ao {DATABASE}")

        # Passo 4: Criar tabelas
        print("\n[4/4] Criando tabelas, views e procedures...")

        manager = DatabaseManager(connector)
        manager.create_tables()

        print("   OK - Tabela: sensor_data")
        print("   OK - Tabela: maintenance_orders")
        print("   OK - Tabela: optimization_results")
        print("   OK - Tabela: pareto_frontier")

        # Verificar tabelas criadas
        print("\nVerificando instalacao...")

        tables_query = "SELECT name FROM sys.tables ORDER BY name"
        tables_df = connector.fetch_data(tables_query)

        if len(tables_df) >= 4:
            print(f"   OK - {len(tables_df)} tabelas criadas:")
            for table in tables_df['name']:
                print(f"      - {table}")
        else:
            print(f"   AVISO - Apenas {len(tables_df)} tabelas encontradas")

        # Fechar conexão
        connector.disconnect()

        # Mensagem de sucesso
        print("\n" + "="*70)
        print("SETUP CONCLUIDO COM SUCESSO!")
        print("="*70)
        print(f"\nInformacoes importantes:")
        print(f"   - Servidor: {SERVER}")
        print(f"   - Banco: {DATABASE}")
        print(f"   - Status: Pronto para uso")

        print(f"\nProximos passos:")
        print(f"   1. Gerar dados de teste:")
        print(f"      cd api && python main.py")
        print(f"      Abrir: http://localhost:8000")
        print(f"\n   2. Ou gerar via Python:")
        print(f"      python -c \"from src.data.synthetic_generator import *; ...\"")

        print("\nSistema de Bucha Virtual pronto!")

    except pyodbc.Error as e:
        print(f"\nERRO de conexao SQL Server:")
        print(f"   {e}")
        print(f"\nPossiveis solucoes:")
        print(f"   1. Verificar se SQL Server esta rodando")
        print(f"   2. Confirmar nome do servidor: {SERVER}")
        print(f"   3. Verificar se voce tem permissoes de administrador")
        print(f"   4. Tentar abrir SQL Server Management Studio manualmente")
        sys.exit(1)

    except Exception as e:
        print(f"\nERRO inesperado:")
        print(f"   {e}")
        import traceback
        print(f"\nDetalhes:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelado pelo usuario.")
        sys.exit(0)
