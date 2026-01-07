# core/classifier/model.py
import joblib
import numpy as np
from .base import BaseClassifier

class MLClassifier(BaseClassifier):
    def __init__(self, model_path: str, feature_order: list[str]):
        self.model = joblib.load(model_path)
        self.feature_order = feature_order

    def _extract_features(self, event: dict) -> np.ndarray:
        return np.array([[event.get(feat, 0) for feat in self.feature_order]])

    def predict(self, event: dict) -> str:
        x = self._extract_features(event)
        return self.model.predict(x)[0]

    def predict_proba(self, event: dict) -> float:
        x = self._extract_features(event)
        return float(np.max(self.model.predict_proba(x)))
