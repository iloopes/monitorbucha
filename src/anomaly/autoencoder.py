"""
Autoencoder com Janela Deslizante para detecção de anomalias em buchas.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import warnings

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class MLPAutoEncoder(nn.Module):
    """Autoencoder com arquitetura MLP."""

    def __init__(self, input_dim: int, latent_dim: int = 5, hidden_layers: Tuple = (32, 16, 8)):
        super().__init__()

        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_layers:
            encoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim

        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)

        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_layers):
            decoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim

        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent


class CNNAutoEncoder(nn.Module):
    """Autoencoder com arquitetura CNN para séries temporais."""

    def __init__(self, input_dim: int, latent_dim: int = 5):
        super().__init__()

        # Encoder - Conv1d para séries temporais
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(8, 4, kernel_size=3, padding=1),
            nn.ReLU(),
        )

        # Calcula dimensão após convoluções
        conv_output_size = input_dim // 4 * 4
        self.fc_encode = nn.Linear(conv_output_size, latent_dim)

        # Decoder
        self.fc_decode = nn.Linear(latent_dim, conv_output_size)
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(4, 8, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(8, 16, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=3, padding=1),
        )

    def forward(self, x):
        # x shape: (batch, seq_len) -> (batch, 1, seq_len)
        x = x.unsqueeze(1)
        enc = self.encoder(x)
        enc = enc.reshape(enc.size(0), -1)
        latent = self.fc_encode(enc)

        dec = self.fc_decode(latent)
        dec = dec.reshape(-1, 4, dec.size(1) // 4)
        reconstructed = self.decoder(dec)
        reconstructed = reconstructed.squeeze(1)

        return reconstructed, latent


class MovingWindowAutoEncoder:
    """
    Autoencoder com janela deslizante para detecção de anomalias.
    """

    def __init__(
        self,
        model_arch: str = "mlp",
        latent_dim: int = 5,
        hidden_layers: Optional[Tuple] = None,
        device: Optional[str] = None
    ):
        """
        Inicializa o autoencoder.

        Args:
            model_arch: "mlp" ou "cnn"
            latent_dim: Dimensão do espaço latente
            hidden_layers: Tupla com dimensões das camadas ocultas (apenas para MLP)
            device: "cpu" ou "cuda"
        """
        self.model_arch = model_arch
        self.latent_dim = latent_dim
        self.hidden_layers = hidden_layers or (32, 16, 8)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = None
        self.scaler = StandardScaler()
        self.input_dim = None
        self.is_fitted = False

        logger.info(f"MovingWindowAutoEncoder inicializado: arch={model_arch}, device={self.device}")

    def fit(
        self,
        data: pd.DataFrame,
        window_size: int = 720,
        num_epochs: int = 50,
        learning_rate: float = 1e-3,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> None:
        """
        Treina o autoencoder.

        Args:
            data: DataFrame com dados históricos
            window_size: Tamanho da janela deslizante
            num_epochs: Número de épocas
            learning_rate: Taxa de aprendizado
            batch_size: Tamanho do batch
            validation_split: Proporção de dados para validação
        """
        logger.info(f"Iniciando treinamento do autoencoder ({self.model_arch})...")

        # Normalizar dados
        data_normalized = self.scaler.fit_transform(data)

        # Criar windows
        windows = self._create_windows(data_normalized, window_size)

        if len(windows) == 0:
            logger.warning(f"Nenhuma janela criada com window_size={window_size}")
            return

        # Split treino/validação
        n_train = int(len(windows) * (1 - validation_split))
        train_windows = windows[:n_train]
        val_windows = windows[n_train:]

        # Inicializar modelo
        self.input_dim = windows[0].shape[0]
        self._init_model()

        # Treinar
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()

        train_losses = []
        val_losses = []

        for epoch in range(num_epochs):
            # Treino
            train_loss = 0.0
            for i in range(0, len(train_windows), batch_size):
                batch = train_windows[i:i+batch_size]
                X = torch.FloatTensor(batch).to(self.device)

                optimizer.zero_grad()
                output, _ = self.model(X)
                loss = criterion(output, X)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            train_loss /= max(1, len(train_windows) // batch_size)
            train_losses.append(train_loss)

            # Validação
            if len(val_windows) > 0:
                val_loss = 0.0
                with torch.no_grad():
                    for i in range(0, len(val_windows), batch_size):
                        batch = val_windows[i:i+batch_size]
                        X = torch.FloatTensor(batch).to(self.device)
                        output, _ = self.model(X)
                        loss = criterion(output, X)
                        val_loss += loss.item()

                val_loss /= max(1, len(val_windows) // batch_size)
                val_losses.append(val_loss)

            if (epoch + 1) % 10 == 0:
                logger.info(f"Época {epoch+1}/{num_epochs} - Train Loss: {train_loss:.6f}")

        self.is_fitted = True
        logger.info("Treinamento concluído")

    def detect(
        self,
        data: pd.DataFrame,
        window_size: int = 720,
        threshold_percentile: float = 95.0,
        rolling_window: int = 12
    ) -> pd.DataFrame:
        """
        Detecta anomalias nos dados.

        Args:
            data: DataFrame com dados para análise
            window_size: Tamanho da janela deslizante
            threshold_percentile: Percentil para threshold
            rolling_window: Janela para suavização

        Returns:
            DataFrame com resultados de detecção
        """
        if not self.is_fitted:
            raise RuntimeError("Modelo não foi treinado. Use fit() primeiro.")

        logger.info("Detectando anomalias...")

        # Normalizar dados
        data_normalized = self.scaler.transform(data)

        # Criar windows
        windows = self._create_windows(data_normalized, window_size)

        if len(windows) == 0:
            return pd.DataFrame()

        # Calcular erros de reconstrução
        reconstruction_errors = []
        distances_latent = []

        with torch.no_grad():
            for window in windows:
                X = torch.FloatTensor([window]).to(self.device)
                output, latent = self.model(X)

                # Q: erro de reconstrução
                error = torch.mean((X - output) ** 2).item()
                reconstruction_errors.append(error)

                # T²: distância no espaço latente
                distance = torch.mean(latent ** 2).item()
                distances_latent.append(distance)

        # Calcular thresholds
        q_threshold = np.percentile(reconstruction_errors, threshold_percentile)
        t2_threshold = np.percentile(distances_latent, threshold_percentile)

        logger.info(f"Q threshold ({threshold_percentile}º percentil): {q_threshold:.6f}")
        logger.info(f"T2 threshold ({threshold_percentile}º percentil): {t2_threshold:.6f}")
        logger.info(f"Q - Min: {min(reconstruction_errors):.6f}, Max: {max(reconstruction_errors):.6f}, Mean: {np.mean(reconstruction_errors):.6f}")
        logger.info(f"T2 - Min: {min(distances_latent):.6f}, Max: {max(distances_latent):.6f}, Mean: {np.mean(distances_latent):.6f}")

        # Suavizar
        q_smooth = pd.Series(reconstruction_errors).rolling(window=rolling_window, min_periods=1).median().values
        t2_smooth = pd.Series(distances_latent).rolling(window=rolling_window, min_periods=1).median().values

        # Detectar anomalias
        anomalies = (q_smooth > q_threshold) | (t2_smooth > t2_threshold)

        logger.info(f"Valores acima de Q threshold: {(q_smooth > q_threshold).sum()}")
        logger.info(f"Valores acima de T2 threshold: {(t2_smooth > t2_threshold).sum()}")

        # Criar resultado
        result = pd.DataFrame({
            'timestamp': data.index[window_size-1:window_size-1+len(reconstruction_errors)],
            'Q': q_smooth,
            'T2': t2_smooth,
            'Q_threshold': q_threshold,
            'T2_threshold': t2_threshold,
            'is_anomaly': anomalies,
            'reconstruction_error': reconstruction_errors,
            'latent_distance': distances_latent
        })

        n_anomalies = anomalies.sum()
        logger.info(f"Detecção concluída: {n_anomalies} anomalias encontradas ({n_anomalies/len(anomalies)*100:.1f}%)")

        return result

    def _init_model(self):
        """Inicializa o modelo."""
        if self.model_arch == "mlp":
            self.model = MLPAutoEncoder(
                input_dim=self.input_dim,
                latent_dim=self.latent_dim,
                hidden_layers=self.hidden_layers
            )
        elif self.model_arch == "cnn":
            self.model = CNNAutoEncoder(
                input_dim=self.input_dim,
                latent_dim=self.latent_dim
            )
        else:
            raise ValueError(f"Arquitetura desconhecida: {self.model_arch}")

        self.model.to(self.device)

    def _create_windows(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """Cria janelas deslizantes dos dados."""
        windows = []
        for i in range(len(data) - window_size + 1):
            windows.append(data[i:i+window_size].flatten())

        return np.array(windows)

    def get_anomaly_summary(self, detections: pd.DataFrame) -> Dict:
        """Retorna resumo das anomalias detectadas."""
        n_total = len(detections)
        n_anomalies = detections['is_anomaly'].sum()

        return {
            'total_points': n_total,
            'anomalies_detected': int(n_anomalies),
            'anomaly_percentage': float(n_anomalies / n_total * 100) if n_total > 0 else 0,
            'mean_Q': float(detections['Q'].mean()),
            'mean_T2': float(detections['T2'].mean()),
            'max_Q': float(detections['Q'].max()),
            'max_T2': float(detections['T2'].max())
        }
