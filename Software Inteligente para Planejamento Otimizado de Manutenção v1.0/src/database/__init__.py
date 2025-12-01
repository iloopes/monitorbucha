"""Módulo de integração com banco de dados."""

from .sql_server import SQLServerConnector, DatabaseManager

__all__ = ["SQLServerConnector", "DatabaseManager"]
