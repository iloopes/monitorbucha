"""
Módulo para pré-processamento de dados.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..utils.logging_config import get_logger
from ..utils.config_loader import get_config_loader

logger = get_logger(__name__)


class DataPreprocessor:
    """Pré-processador de dados."""

    def __init__(self):
        """Inicializa o pré-processador."""
        self.config_loader = get_config_loader()
        self.data_config = self.config_loader.get_default_config().get("data", {})

    def convert_string_to_float(self, value: Any, decimal_sep: str = ",") -> float:
        """
        Converte string para float, tratando separador decimal.

        Args:
            value: Valor a ser convertido.
            decimal_sep: Separador decimal na string.

        Returns:
            Valor float.

        Examples:
            >>> preprocessor = DataPreprocessor()
            >>> preprocessor.convert_string_to_float("1,25")
            1.25
        """
        if pd.isna(value):
            return np.nan

        if isinstance(value, (int, float)):
            return float(value)

        # Converter para string e trocar separador decimal
        str_value = str(value).replace(decimal_sep, ".")

        try:
            return float(str_value)
        except ValueError:
            logger.warning(f"Não foi possível converter '{value}' para float.")
            return np.nan

    def normalize_numeric_columns(
        self, df: pd.DataFrame, columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Normaliza colunas numéricas para ter separador decimal correto.

        Args:
            df: DataFrame a ser normalizado.
            columns: Lista de colunas a normalizar. Se None, normaliza todas as colunas object.

        Returns:
            DataFrame com colunas normalizadas.
        """
        df = df.copy()
        decimal_sep = self.data_config.get("decimal_separator", ",")

        if columns is None:
            # Identificar colunas que podem ser numéricas mas estão como object
            columns = df.select_dtypes(include=["object"]).columns.tolist()

        for column in columns:
            if column not in df.columns:
                continue

            try:
                df[column] = df[column].apply(
                    lambda x: self.convert_string_to_float(x, decimal_sep)
                )
                logger.debug(f"Coluna {column} normalizada para float.")
            except Exception as e:
                logger.debug(
                    f"Coluna {column} não pôde ser convertida para float: {e}"
                )

        return df

    def parse_dates(
        self, df: pd.DataFrame, date_columns: List[str], format: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Converte colunas de data para tipo datetime.

        Args:
            df: DataFrame a ser processado.
            date_columns: Lista de colunas de data.
            format: Formato da data. Se None, usa configuração padrão.

        Returns:
            DataFrame com datas convertidas.
        """
        df = df.copy()

        if format is None:
            format = self.data_config.get("date_format", "%Y-%m-%d")

        for column in date_columns:
            if column not in df.columns:
                logger.warning(f"Coluna de data não encontrada: {column}")
                continue

            try:
                df[column] = pd.to_datetime(df[column], format=format, errors="coerce")
                logger.debug(f"Coluna {column} convertida para datetime.")
            except Exception as e:
                logger.error(f"Erro ao converter coluna {column} para datetime: {e}")

        return df

    def fill_missing_values(
        self, df: pd.DataFrame, strategy: str = "mean", columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Preenche valores faltantes.

        Args:
            df: DataFrame a ser processado.
            strategy: Estratégia de preenchimento ("mean", "median", "mode", "ffill", "bfill", "zero").
            columns: Lista de colunas a preencher. Se None, preenche todas as colunas numéricas.

        Returns:
            DataFrame com valores preenchidos.
        """
        df = df.copy()

        if columns is None:
            columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

        for column in columns:
            if column not in df.columns:
                continue

            null_count = df[column].isnull().sum()

            if null_count == 0:
                continue

            if strategy == "mean":
                fill_value = df[column].mean()
            elif strategy == "median":
                fill_value = df[column].median()
            elif strategy == "mode":
                fill_value = df[column].mode()[0] if not df[column].mode().empty else 0
            elif strategy == "zero":
                fill_value = 0
            elif strategy == "ffill":
                df[column].fillna(method="ffill", inplace=True)
                logger.debug(
                    f"Coluna {column}: {null_count} valores preenchidos (forward fill)."
                )
                continue
            elif strategy == "bfill":
                df[column].fillna(method="bfill", inplace=True)
                logger.debug(
                    f"Coluna {column}: {null_count} valores preenchidos (backward fill)."
                )
                continue
            else:
                logger.warning(f"Estratégia desconhecida: {strategy}. Usando mean.")
                fill_value = df[column].mean()

            df[column].fillna(fill_value, inplace=True)
            logger.debug(
                f"Coluna {column}: {null_count} valores preenchidos com {strategy}={fill_value:.2f}."
            )

        return df

    def calculate_time_offset(self, date: datetime, reference_date: Optional[datetime] = None) -> int:
        """
        Calcula o offset temporal em dias entre uma data e uma referência.

        Args:
            date: Data a calcular o offset.
            reference_date: Data de referência. Se None, usa a data atual.

        Returns:
            Número de dias de diferença.
        """
        if reference_date is None:
            reference_date = datetime.today()

        if isinstance(date, str):
            date = pd.to_datetime(date)

        if isinstance(reference_date, str):
            reference_date = pd.to_datetime(reference_date)

        delta = reference_date - date
        return delta.days

    def add_default_unavailability_fields(
        self, df: pd.DataFrame, default_values: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Adiciona campos de indisponibilidade com valores padrão se não existirem.

        Args:
            df: DataFrame a ser processado.
            default_values: Valores padrão de indisponibilidade. Se None, usa configuração.

        Returns:
            DataFrame com campos de indisponibilidade.
        """
        df = df.copy()

        if default_values is None:
            # Usar valores da configuração
            unavail_config = (
                self.config_loader.get_default_config()
                .get("unavailability", {})
                .get("default_hours", {})
            )
            default_values = {
                "normal": unavail_config.get("normal", 2.0),
                "degradado1": unavail_config.get("degradado1", 4.0),
                "degradado2": unavail_config.get("degradado2", 8.0),
                "degradado3": unavail_config.get("degradado3", 16.0),
                "falha": unavail_config.get("falha", 48.0),
            }

        # Adicionar campos para DGA
        dga_fields = {
            "DGA_INDISPONIBILIDADE_N": default_values["normal"],
            "DGA_INDISPONIBILIDADE_D1": default_values["degradado1"],
            "DGA_INDISPONIBILIDADE_D2": default_values["degradado2"],
            "DGA_INDISPONIBILIDADE_D3": default_values["degradado3"],
            "DGA_INDISPONIBILIDADE_FALHA": default_values["falha"],
        }

        # Adicionar campos para FQ
        fq_fields = {
            "FQ_INDISPONIBILIDADE_N": default_values["normal"],
            "FQ_INDISPONIBILIDADE_D1": default_values["degradado1"],
            "FQ_INDISPONIBILIDADE_D2": default_values["degradado2"],
            "FQ_INDISPONIBILIDADE_D3": default_values["degradado3"],
            "FQ_INDISPONIBILIDADE_FALHA": default_values["falha"],
        }

        all_fields = {**dga_fields, **fq_fields}

        for field, value in all_fields.items():
            if field not in df.columns:
                df[field] = value
                logger.debug(f"Campo {field} adicionado com valor padrão: {value}")

        return df

    def remove_outliers(
        self, df: pd.DataFrame, columns: List[str], method: str = "iqr", threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers de colunas numéricas.

        Args:
            df: DataFrame a ser processado.
            columns: Lista de colunas a processar.
            method: Método de detecção ("iqr" ou "zscore").
            threshold: Threshold para detecção (1.5 para IQR, 3 para z-score).

        Returns:
            DataFrame sem outliers.
        """
        df = df.copy()
        initial_len = len(df)

        for column in columns:
            if column not in df.columns:
                continue

            if method == "iqr":
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR

                outliers_mask = (df[column] < lower_bound) | (df[column] > upper_bound)

            elif method == "zscore":
                mean = df[column].mean()
                std = df[column].std()
                z_scores = np.abs((df[column] - mean) / std)
                outliers_mask = z_scores > threshold

            else:
                logger.warning(f"Método desconhecido: {method}. Pulando coluna {column}.")
                continue

            outliers_count = outliers_mask.sum()

            if outliers_count > 0:
                df = df[~outliers_mask]
                logger.debug(f"Coluna {column}: {outliers_count} outliers removidos.")

        final_len = len(df)
        logger.info(f"Total de linhas removidas: {initial_len - final_len}")

        return df
