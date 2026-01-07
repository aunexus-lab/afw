# core/classifier/simple.py
from .base import BaseClassifier

class SimpleHeuristicClassifier(BaseClassifier):
    def predict(self, event: dict) -> str:
        if event.get("failed_logins", 0) >= 5:
            return "attack"
        if event.get("packet_count", 0) > 100:
            return "suspicious"
        return "normal"

    def predict_proba(self, event: dict) -> float:
        if event.get("failed_logins", 0) >= 5:
            return 0.95
        if event.get("packet_count", 0) > 100:
            return 0.75
        return 0.3
