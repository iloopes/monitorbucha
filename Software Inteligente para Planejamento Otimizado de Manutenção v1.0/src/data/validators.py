"""
Módulo para validação de dados de entrada.
"""

from typing import Dict, List, Optional, Set
import pandas as pd

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validador de dados de entrada."""

    @staticmethod
    def validate_required_columns(
        df: pd.DataFrame, required_columns: List[str]
    ) -> bool:
        """
        Valida se o DataFrame contém todas as colunas obrigatórias.

        Args:
            df: DataFrame a ser validado.
            required_columns: Lista de colunas obrigatórias.

        Returns:
            True se todas as colunas existem, False caso contrário.

        Raises:
            ValueError: Se alguma coluna obrigatória estiver faltando.
        """
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            error_msg = f"Colunas obrigatórias faltando: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Todas as colunas obrigatórias presentes.")
        return True

    @staticmethod
    def validate_data_types(
        df: pd.DataFrame, column_types: Dict[str, type]
    ) -> bool:
        """
        Valida os tipos de dados das colunas.

        Args:
            df: DataFrame a ser validado.
            column_types: Dicionário {coluna: tipo_esperado}.

        Returns:
            True se todos os tipos estão corretos.

        Raises:
            ValueError: Se algum tipo de dado estiver incorreto.
        """
        errors = []

        for column, expected_type in column_types.items():
            if column not in df.columns:
                continue

            # Verificar tipo compatível
            actual_dtype = df[column].dtype

            if expected_type == int and not pd.api.types.is_integer_dtype(actual_dtype):
                errors.append(f"{column}: esperado int, encontrado {actual_dtype}")

            elif expected_type == float and not pd.api.types.is_numeric_dtype(
                actual_dtype
            ):
                errors.append(f"{column}: esperado float, encontrado {actual_dtype}")

            elif expected_type == str and not pd.api.types.is_string_dtype(
                actual_dtype
            ):
                # Strings podem estar como object
                if actual_dtype != "object":
                    errors.append(f"{column}: esperado str, encontrado {actual_dtype}")

        if errors:
            error_msg = "Tipos de dados inválidos:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Tipos de dados válidos.")
        return True

    @staticmethod
    def validate_value_ranges(
        df: pd.DataFrame, column_ranges: Dict[str, tuple]
    ) -> bool:
        """
        Valida se os valores estão dentro dos intervalos esperados.

        Args:
            df: DataFrame a ser validado.
            column_ranges: Dicionário {coluna: (min, max)}.

        Returns:
            True se todos os valores estão dentro dos intervalos.

        Raises:
            ValueError: Se algum valor estiver fora do intervalo.
        """
        errors = []

        for column, (min_val, max_val) in column_ranges.items():
            if column not in df.columns:
                continue

            # Ignorar valores nulos
            values = df[column].dropna()

            if len(values) == 0:
                continue

            actual_min = values.min()
            actual_max = values.max()

            if actual_min < min_val or actual_max > max_val:
                errors.append(
                    f"{column}: valores fora do intervalo [{min_val}, {max_val}]. "
                    f"Encontrado: [{actual_min}, {actual_max}]"
                )

        if errors:
            error_msg = "Valores fora do intervalo:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Valores dentro dos intervalos esperados.")
        return True

    @staticmethod
    def validate_no_missing_values(
        df: pd.DataFrame, columns: Optional[List[str]] = None
    ) -> bool:
        """
        Valida se não há valores faltantes nas colunas especificadas.

        Args:
            df: DataFrame a ser validado.
            columns: Lista de colunas a verificar. Se None, verifica todas.

        Returns:
            True se não há valores faltantes.

        Raises:
            ValueError: Se houver valores faltantes.
        """
        if columns is None:
            columns = df.columns.tolist()

        missing_info = []

        for column in columns:
            if column not in df.columns:
                continue

            null_count = df[column].isnull().sum()

            if null_count > 0:
                percentage = (null_count / len(df)) * 100
                missing_info.append(
                    f"{column}: {null_count} valores faltantes ({percentage:.1f}%)"
                )

        if missing_info:
            error_msg = "Valores faltantes encontrados:\n" + "\n".join(missing_info)
            logger.warning(error_msg)
            raise ValueError(error_msg)

        logger.info("Nenhum valor faltante encontrado.")
        return True

    @staticmethod
    def validate_unique_ids(df: pd.DataFrame, id_column: str) -> bool:
        """
        Valida se os IDs são únicos.

        Args:
            df: DataFrame a ser validado.
            id_column: Nome da coluna de ID.

        Returns:
            True se todos os IDs são únicos.

        Raises:
            ValueError: Se houver IDs duplicados.
        """
        if id_column not in df.columns:
            error_msg = f"Coluna de ID não encontrada: {id_column}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        duplicates = df[id_column].duplicated()
        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            duplicate_ids = df[duplicates][id_column].tolist()
            error_msg = (
                f"{duplicate_count} IDs duplicados encontrados: {duplicate_ids}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Todos os {len(df)} IDs são únicos.")
        return True

    @staticmethod
    def validate_maintenance_order_data(df: pd.DataFrame) -> bool:
        """
        Valida dados de ordens de serviço de manutenção.

        Args:
            df: DataFrame com ordens de serviço.

        Returns:
            True se os dados são válidos.

        Raises:
            ValueError: Se houver problemas de validação.
        """
        logger.info("Validando dados de ordens de serviço...")

        # Colunas básicas obrigatórias
        required_columns = ["OS_Id", "MotivoManutencao"]

        DataValidator.validate_required_columns(df, required_columns)
        DataValidator.validate_unique_ids(df, "OS_Id")

        # Validar valores do MotivoManutencao
        valid_reasons = {"DGA", "FQ"}
        invalid_reasons = set(df["MotivoManutencao"].unique()) - valid_reasons

        if invalid_reasons:
            error_msg = (
                f"Motivos de manutenção inválidos: {invalid_reasons}. "
                f"Valores válidos: {valid_reasons}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Validação de ordens de serviço concluída com sucesso.")
        return True

    @staticmethod
    def validate_sensor_data(df: pd.DataFrame) -> bool:
        """
        Valida dados de sensores.

        Args:
            df: DataFrame com dados de sensores.

        Returns:
            True se os dados são válidos.

        Raises:
            ValueError: Se houver problemas de validação.
        """
        logger.info("Validando dados de sensores...")

        if df.empty:
            error_msg = "DataFrame de sensores está vazio."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Verificar se há colunas numéricas
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns

        if len(numeric_columns) == 0:
            error_msg = "Nenhuma coluna numérica encontrada nos dados de sensores."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(
            f"Validação de dados de sensores concluída. {len(numeric_columns)} colunas numéricas encontradas."
        )
        return True
