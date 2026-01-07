# core/classifier/nn_model.py

import torch
import torch.nn.functional as F
import numpy as np
from .base import BaseClassifier
from core.config import MODEL_PATH
from models.net import FirewallNet


class NNClassifier(BaseClassifier):
    def __init__(self, model_path: str = MODEL_PATH):
        # Cargar el checkpoint entrenado
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"))

        self.feature_order = checkpoint["feature_order"]
        self.label_encoder = checkpoint["label_encoder"]
        input_size = len(self.feature_order)

        # Cargar el modelo
        self.model = FirewallNet(input_size)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    def _vectorize(self, event: dict) -> torch.Tensor:
        values = [float(event.get(f, 0)) for f in self.feature_order]
        return torch.tensor([values], dtype=torch.float32)

    def predict(self, event: dict) -> str:
        x = self._vectorize(event)
        logits = self.model(x)
        predicted_idx = torch.argmax(logits, dim=1).item()
        return self.label_encoder.inverse_transform([predicted_idx])[0]

    def predict_proba(self, event: dict) -> float:
        x = self._vectorize(event)
        logits = self.model(x)
        probs = F.softmax(logits, dim=1)
        return float(torch.max(probs))
