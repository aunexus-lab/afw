# core/classifier/base.py
from abc import ABC, abstractmethod

class BaseClassifier(ABC):
    @abstractmethod
    def predict(self, event: dict) -> str:
        """Devuelve la etiqueta predicha: 'normal', 'suspicious', 'attack'"""
        pass

    @abstractmethod
    def predict_proba(self, event: dict) -> float:
        """Devuelve un score de confianza entre 0 y 1"""
        pass
