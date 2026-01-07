import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
from datetime import datetime
from joblib import load
from core.context.context_enricher import enrich_event
from config.config import MODEL_PATH
from models.net import FirewallNet
from core.context.utils import get_active_model_info
from core.context.utils import verify_model_integrity
import hashlib

# Check model integrity
# This ensures the model has not been tampered with or corrupted.
# It reads the model file, computes its SHA-256 hash, and compares it with the
# If the model hash does not match, it raises an error.
verify_model_integrity("models/firewall_nn.pt")


# Load model and artifacts
checkpoint = torch.load("models/firewall_nn.pt", map_location="cpu", weights_only=False)

# Inferir tamaño de salida desde los pesos entrenados
fc2_weight = checkpoint["model_state_dict"]["fc2.weight"]
output_size = fc2_weight.shape[0]


model = FirewallNet(input_size=len(checkpoint["feature_order"]), output_size = output_size)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

feature_order = checkpoint["feature_order"]
label_encoder = checkpoint["label_encoder"]


scaler = load("models/nn_firewall_scaler.joblib")


def predict_action(event, score, recent_event_count, debug = False):
    enriched = enrich_event(event, debug = debug)

    # Combinar features básicas con las enriquecidas
    hour = datetime.fromisoformat(event['timestamp'].replace("Z", "+00:00")).hour
    success = int(bool(event.get('success')))

    row = {
        'hour'                  : hour,
        'score'                 : score,
        'recent_event_count'    : recent_event_count,
        'success'               : success,
        'action_login_attempt'  : 1 if event['action'] == 'login_attempt' else 0,
        'action_invalid_user'   : 1 if event['action'] == 'invalid_user' else 0,
        'parse_status_parsed'   : 1 if event['parse_status'] == 'parsed' else 0,
        'parse_status_failed'   : 1 if event['parse_status'] == 'failed' else 0,
    }

    row.update(enriched)

    if debug:
        print("🧪 Final feature vector:")
        for k, v in row.items():
            print(f"{k:25} → {v}")

    df = pd.DataFrame([row])
    df = df.reindex(columns=feature_order, fill_value=0)
    scaled = scaler.transform(df)

    with torch.no_grad():
        x_tensor = torch.tensor(scaled, dtype=torch.float32)
        logits = model(x_tensor)
        probs = F.softmax(logits, dim=1).numpy()[0]
        label_idx = np.argmax(probs)
        label = label_encoder.inverse_transform([label_idx])[0]

    if debug:
        print("\n🔍 Probabilities per class:")
        for cls, prob in zip(label_encoder.classes_, probs):
            print(f"  {cls:8} → {prob:.4f}")

    return label


# Uso manual de ejemplo
def vectorize_raw_event(event, score, recent_event_count):
    enriched = enrich_event(event)

    hour = datetime.fromisoformat(event['timestamp'].replace("Z", "+00:00")).hour
    success = int(bool(event.get('success')))

    row = {
        'hour'                  : hour,
        'score'                 : score,
        'recent_event_count'    : recent_event_count,
        'success'               : success,
        'action_login_attempt'  : 1 if event['action'] == 'login_attempt' else 0,
        'action_invalid_user'   : 1 if event['action'] == 'invalid_user' else 0,
        'parse_status_parsed'   : 1 if event['parse_status'] == 'parsed' else 0,
        'parse_status_failed'   : 1 if event['parse_status'] == 'failed' else 0,
    }

    row.update(enriched)
    df = pd.DataFrame([row])
    df = df.reindex(columns=feature_order, fill_value=0)
    return df


if __name__ == "__main__":
    raw_event = {
        "timestamp"     : "2025-05-25T14:10:00Z",
        "ip"            : "185.156.73.234",
        "port"          : 22,
        "process"       : "sshd",
        "user"          : "root",
        "action"        : "invalid_user",
        "success"       : False,
        "source"        : "auth",
        "raw"           : "...",
        "parsed"        : {},
        "parse_status"  : "parsed"
    }

    score = 120
    recent_event_count = 8

    result = predict_action(raw_event, score, recent_event_count, debug = True)
    print(f"\n🔐 Predicted action: {result}")
