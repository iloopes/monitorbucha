"""
Configuração de logging para o sistema.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config_loader import get_config_loader


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: Optional[bool] = None,
    log_to_console: Optional[bool] = None,
    log_dir: Optional[Path] = None,
) -> logging.Logger:
    """
    Configura o sistema de logging.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  Se None, usa o valor do arquivo de configuração.
        log_to_file: Se True, grava logs em arquivo. Se None, usa configuração.
        log_to_console: Se True, exibe logs no console. Se None, usa configuração.
        log_dir: Diretório para salvar logs. Se None, usa configuração.

    Returns:
        Logger configurado.
    """
    # Carregar configurações
    config_loader = get_config_loader()
    config = config_loader.get_default_config()
    log_config = config.get("logging", {})

    # Usar valores fornecidos ou padrões da configuração
    if log_level is None:
        log_level = log_config.get("level", "INFO")

    if log_to_file is None:
        log_to_file = log_config.get("log_to_file", True)

    if log_to_console is None:
        log_to_console = log_config.get("log_to_console", True)

    if log_dir is None:
        # Obter diretório de logs da configuração
        paths_config = config.get("paths", {})
        log_dir_str = paths_config.get("logs", "logs")

        # Converter para path absoluto
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        log_dir = project_root / log_dir_str

    # Criar diretório de logs se não existir
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configurar formato de log
    log_format = log_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    date_format = log_config.get("date_format", "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Obter o logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remover handlers existentes
    logger.handlers.clear()

    # Handler para console
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Handler para arquivo
    if log_to_file:
        log_file = log_dir / "maintenance_system.log"
        max_bytes = log_config.get("max_bytes", 10485760)  # 10 MB
        backup_count = log_config.get("backup_count", 5)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Sistema de logging configurado. Nível: {log_level}")

    if log_to_file:
        logger.info(f"Logs sendo gravados em: {log_file}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger com o nome especificado.

    Args:
        name: Nome do logger (geralmente __name__ do módulo).

    Returns:
        Logger configurado.
    """
    return logging.getLogger(name)
