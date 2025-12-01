"""
Módulo para carregamento de dados de diferentes formatos.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..utils.logging_config import get_logger
from ..utils.config_loader import get_config_loader

logger = get_logger(__name__)


class DataLoader:
    """Carregador de dados de diferentes formatos."""

    def __init__(self):
        """Inicializa o carregador de dados."""
        self.config_loader = get_config_loader()
        self.data_config = self.config_loader.get_default_config().get("data", {})

    def load_csv(
        self,
        file_path: Union[str, Path],
        decimal: Optional[str] = None,
        sep: Optional[str] = None,
        encoding: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Carrega dados de um arquivo CSV.

        Args:
            file_path: Caminho para o arquivo CSV.
            decimal: Separador decimal (padrão: usar configuração).
            sep: Separador de campos (padrão: usar configuração).
            encoding: Encoding do arquivo (padrão: usar configuração).
            **kwargs: Argumentos adicionais para pd.read_csv.

        Returns:
            DataFrame com os dados.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            pd.errors.ParserError: Se houver erro ao parsear o CSV.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        if decimal is None:
            decimal = self.data_config.get("decimal_separator", ",")

        if sep is None:
            sep = self.data_config.get("field_separator", ",")

        if encoding is None:
            encoding = self.data_config.get("encoding", "utf-8")

        logger.info(f"Carregando arquivo CSV: {file_path}")

        try:
            df = pd.read_csv(
                file_path, decimal=decimal, sep=sep, encoding=encoding, **kwargs
            )
            logger.info(
                f"Arquivo carregado com sucesso. {len(df)} linhas, {len(df.columns)} colunas."
            )
            return df

        except pd.errors.ParserError as e:
            logger.error(f"Erro ao parsear arquivo CSV: {e}")
            raise

    def load_excel(
        self, file_path: Union[str, Path], sheet_name: Optional[str] = None, **kwargs
    ) -> pd.DataFrame:
        """
        Carrega dados de um arquivo Excel.

        Args:
            file_path: Caminho para o arquivo Excel.
            sheet_name: Nome da planilha (padrão: primeira planilha).
            **kwargs: Argumentos adicionais para pd.read_excel.

        Returns:
            DataFrame com os dados.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        logger.info(f"Carregando arquivo Excel: {file_path}")

        if sheet_name:
            logger.info(f"Planilha: {sheet_name}")

        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        logger.info(
            f"Arquivo carregado com sucesso. {len(df)} linhas, {len(df.columns)} colunas."
        )

        return df

    def load_parquet(
        self, file_path: Union[str, Path], **kwargs
    ) -> pd.DataFrame:
        """
        Carrega dados de um arquivo Parquet.

        Args:
            file_path: Caminho para o arquivo Parquet.
            **kwargs: Argumentos adicionais para pd.read_parquet.

        Returns:
            DataFrame com os dados.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        logger.info(f"Carregando arquivo Parquet: {file_path}")

        df = pd.read_parquet(file_path, **kwargs)
        logger.info(
            f"Arquivo carregado com sucesso. {len(df)} linhas, {len(df.columns)} colunas."
        )

        return df

    def load_json(
        self, file_path: Union[str, Path], encoding: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Carrega dados de um arquivo JSON.

        Args:
            file_path: Caminho para o arquivo JSON.
            encoding: Encoding do arquivo (padrão: usar configuração).

        Returns:
            Dicionário ou lista com os dados.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            json.JSONDecodeError: Se houver erro ao parsear o JSON.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        if encoding is None:
            encoding = self.data_config.get("encoding", "utf-8")

        logger.info(f"Carregando arquivo JSON: {file_path}")

        with open(file_path, "r", encoding=encoding) as f:
            data = json.load(f)

        logger.info(f"Arquivo carregado com sucesso.")
        return data

    def load_maintenance_orders(
        self, file_path: Union[str, Path]
    ) -> pd.DataFrame:
        """
        Carrega dados de ordens de serviço de manutenção.

        Detecta automaticamente o formato do arquivo (CSV, Excel, JSON).

        Args:
            file_path: Caminho para o arquivo.

        Returns:
            DataFrame com as ordens de serviço.

        Raises:
            ValueError: Se o formato do arquivo não for suportado.
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return self.load_csv(file_path)
        elif suffix in [".xlsx", ".xls"]:
            return self.load_excel(file_path)
        elif suffix == ".json":
            data = self.load_json(file_path)
            return pd.DataFrame(data)
        else:
            raise ValueError(
                f"Formato de arquivo não suportado: {suffix}. "
                "Use CSV, Excel ou JSON."
            )

    def save_dataframe(
        self,
        df: pd.DataFrame,
        file_path: Union[str, Path],
        format: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Salva um DataFrame em arquivo.

        Args:
            df: DataFrame a ser salvo.
            file_path: Caminho para o arquivo de saída.
            format: Formato de saída ("csv", "excel", "parquet", "json").
                   Se None, detecta pelo sufixo do arquivo.
            **kwargs: Argumentos adicionais para o método de salvamento.
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if format is None:
            format = file_path.suffix.lower().replace(".", "")

        logger.info(f"Salvando DataFrame em {format.upper()}: {file_path}")

        if format == "csv":
            decimal = self.data_config.get("decimal_separator", ",")
            sep = self.data_config.get("field_separator", ",")
            encoding = self.data_config.get("encoding", "utf-8")
            df.to_csv(
                file_path,
                decimal=decimal,
                sep=sep,
                encoding=encoding,
                index=False,
                **kwargs,
            )

        elif format in ["xlsx", "excel"]:
            df.to_excel(file_path, index=False, **kwargs)

        elif format == "parquet":
            df.to_parquet(file_path, index=False, **kwargs)

        elif format == "json":
            encoding = self.data_config.get("encoding", "utf-8")
            df.to_json(
                file_path, orient="records", force_ascii=False, indent=2, **kwargs
            )

        else:
            raise ValueError(f"Formato não suportado: {format}")

        logger.info(f"Arquivo salvo com sucesso: {file_path}")
