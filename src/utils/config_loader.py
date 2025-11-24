"""
Módulo para carregamento de configurações YAML.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigLoader:
    """Carregador de configurações a partir de arquivos YAML."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Inicializa o carregador de configurações.

        Args:
            config_dir: Diretório contendo os arquivos de configuração.
                       Se None, usa o diretório config/ na raiz do projeto.
        """
        if config_dir is None:
            # Assume que estamos em src/utils/ e config/ está na raiz
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            config_dir = project_root / "config"

        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise FileNotFoundError(
                f"Diretório de configuração não encontrado: {self.config_dir}"
            )

        self._configs: Dict[str, Dict[str, Any]] = {}

    def load(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """
        Carrega um arquivo de configuração YAML.

        Args:
            config_name: Nome do arquivo de configuração (sem extensão .yaml).
            reload: Se True, recarrega o arquivo mesmo se já estiver em cache.

        Returns:
            Dicionário com as configurações.

        Raises:
            FileNotFoundError: Se o arquivo de configuração não existir.
            yaml.YAMLError: Se houver erro ao parsear o YAML.
        """
        if not reload and config_name in self._configs:
            return self._configs[config_name]

        config_file = self.config_dir / f"{config_name}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {config_file}"
            )

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            self._configs[config_name] = config
            return config

        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Erro ao parsear arquivo de configuração {config_file}: {e}"
            )

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Carrega todos os arquivos YAML do diretório de configuração.

        Returns:
            Dicionário com todas as configurações, indexado pelo nome do arquivo.
        """
        all_configs = {}

        for config_file in self.config_dir.glob("*.yaml"):
            config_name = config_file.stem
            try:
                all_configs[config_name] = self.load(config_name)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar {config_file}: {e}")

        return all_configs

    def get(self, config_name: str, key_path: str, default: Any = None) -> Any:
        """
        Obtém um valor específico de uma configuração usando uma chave aninhada.

        Args:
            config_name: Nome do arquivo de configuração.
            key_path: Caminho para a chave, separado por pontos (ex: "markov.n_states").
            default: Valor padrão se a chave não existir.

        Returns:
            Valor da configuração ou default se não encontrado.

        Examples:
            >>> loader = ConfigLoader()
            >>> loader.get("default", "logging.level", "INFO")
            'INFO'
        """
        config = self.load(config_name)

        keys = key_path.split(".")
        value = config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_field_mapping(self, analysis_type: str) -> Dict[str, Any]:
        """
        Obtém o mapeamento de campos para um tipo de análise.

        Args:
            analysis_type: Tipo de análise ("DGA" ou "FQ").

        Returns:
            Dicionário com o mapeamento de campos.
        """
        mappings = self.load("field_mappings")

        if analysis_type.upper() == "DGA":
            return mappings["dga_mapping"]
        elif analysis_type.upper() == "FQ":
            return mappings["fq_mapping"]
        else:
            raise ValueError(
                f"Tipo de análise inválido: {analysis_type}. "
                "Use 'DGA' ou 'FQ'."
            )

    def get_nsga_params(self) -> Dict[str, Any]:
        """
        Obtém os parâmetros do algoritmo NSGA-II.

        Returns:
            Dicionário com os parâmetros do NSGA-II.
        """
        return self.load("nsga_params")

    def get_thresholds(self, equipment_type: str = "bushings") -> Dict[str, Any]:
        """
        Obtém os limiares de classificação para um tipo de equipamento.

        Args:
            equipment_type: Tipo de equipamento (padrão: "bushings").

        Returns:
            Dicionário com os limiares.
        """
        thresholds = self.load("thresholds")
        return thresholds.get(equipment_type, {})

    def get_default_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração padrão do sistema.

        Returns:
            Dicionário com a configuração padrão.
        """
        return self.load("default")


# Instância singleton do carregador de configurações
_config_loader_instance: Optional[ConfigLoader] = None


def get_config_loader(config_dir: Optional[Path] = None) -> ConfigLoader:
    """
    Obtém a instância singleton do carregador de configurações.

    Args:
        config_dir: Diretório de configuração (usado apenas na primeira chamada).

    Returns:
        Instância do ConfigLoader.
    """
    global _config_loader_instance

    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_dir)

    return _config_loader_instance
